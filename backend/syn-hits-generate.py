# -*- coding: utf-8 -*-


import mturk
from settings import settings

from langlib import get_languages_list, get_languages_properties

import psycopg2

from itertools import islice, chain

import uuid


from nltk.corpus import wordnet
from nltk.corpus import brown # some random corpus...

import random

def syn():
	
	while True:
		#syns=wordnet.synsets(brown.words()[random.randint(1, len(brown.words())-1)].lower())
		syns=wordnet.synsets(brown.words()[random.randint(1, 1000000)].lower())
		try:
			word=syns[0].lemmas[0].name
			#print "word: ", word
			for syn in syns:
				for l in syn.lemmas:
					word2=l.name
					#print "word2: ", word2
					#not(word.search("_")>0 or len(word)<4) and not( word2.search("_")>0 or len(word2)<4) and 
					if not (word==word2):
						return (word,word2)
		except Exception:
			continue


def batch(iterable, size):
    sourceiter = iter(iterable)
    while True:
        batchiter = islice(sourceiter, size)
        yield chain([batchiter.next()], batchiter)

# basic logging setup for console output
import logging
logging.basicConfig(
	format='%(asctime)s %(levelname)s %(message)s', 
	datefmt='%m/%d/%Y %I:%M:%S %p',
	level=logging.INFO)

logging.info("synonyms hit creation pipeline - START")

target_language = settings["target_language"]
logging.info("target language: %s" % (target_language))

# generate list of languages to process
#TODO: for now just load this list from data/languages/languages.txt (list of wikipedia languages with 10,000+ articles)

langs=[] #list of languages represented as wikipedia prefixes e.g. xx - xx.wikipedia.org
langs=get_languages_list(settings["languages_file"], target_language)

logging.info("# of languages loaded: %s" %(len(langs)))
if len(langs)<=5:
	logging.info("languages are: %s" %(langs))

langs_properties={} #list of languages' properties (e.g. LTR vs RTL script, non latin characters, etc) 
langs_properties=get_languages_properties(settings["languages_properties_file"], target_language)


logging.info("generating HITTypes for each language")
# iterate over each language individually

lang="en"
# step #1 register HIT type for current language

operation="RegisterHITType"

parameters2=settings["synonymsHITtype"]


output=mturk.call_turk(operation, parameters2)
logging.debug("RegisterHITType response: %s" % (output))
hittype_id= mturk.get_val(output, "HITTypeId")
logging.info("HIT type for language: %s created with id: %s" % (lang, hittype_id))


#get all words from vocabulary
try:
	conn = psycopg2.connect("dbname='hitman' user='dkachaev' host='localhost'")
	logging.info("successfully connected to database")
except:
	logging.error("unable to connect to the database")

cur = conn.cursor()

#getting language_id from database
sql="SELECT id from languages where prefix=%s;"
cur.execute(sql, (lang,))
rows = cur.fetchall()

lang_id=0
for row in rows:
	lang_id=str(row[0])


sql="SELECT add_hittype(%s, %s, %s, %s, %s);"
cur.execute(sql,(hittype_id, "Synonyms HIT for English", lang_id, lang, "synonyms"))
conn.commit()
mturk_hittype_id=hittype_id

# iterate over each language individually
for i, lang in enumerate(langs):
	
	logging.info("processing language: %s (#%s out of %s) " %(lang,i+1,len(langs)))
	
	hittype_id= mturk_hittype_id


	#get all words from vocabulary
	try:
		conn = psycopg2.connect("dbname='hitman' user='dkachaev' host='localhost'")
		logging.info("successfully connected to database")
	except:
		logging.error("unable to connect to the database")
	
	cur = conn.cursor()
	cur2 = conn.cursor()


	sql="SELECT id from languages where prefix=%s;"
	cur.execute(sql, (lang,))
	rows = cur.fetchall()

	lang_id=0
	for row in rows:
		lang_id=row[0]

	"""
	sql="SELECT * from dictionary WHERE language_id=%s;"
	cur.execute(sql, (lang_id,))
	rows = cur.fetchall()
	"""
	
	sql="select vhr.translation, d.translation, mturk_assignment_id, word_id from vocabularyhitresults vhr, dictionary d where reason='' and is_control='0' and d.id=vhr.word_id and language_id=%s"
	cur.execute(sql, (lang_id,))
	rows = cur.fetchall()

	web_endpoint='http://'+settings["web_enpoint_domain"]+settings["web_endpoint_synonyms_hit_path"]+"/"+lang

	for batchiter in batch(rows, settings["synonyms_num_unknowns"]):

		guid=str(uuid.uuid4())

		sql="INSERT INTO synonymshits (mturk_hittype_id, uuid, language_id) VALUES (%s, %s, %s) RETURNING id;"
		cur2.execute(sql,(hittype_id, guid, lang_id))
		hit_id = cur2.fetchone()[0]

		print "Batch: ",
		for item in batchiter:
			word_id=item[3]
			translation=item[0]
			synonym=item[1]
			mturk_assignment_id=item[2]
			
			
			sql="INSERT INTO synonymshitsdata (hit_id, word_id, synonym, translation) VALUES (%s, %s, %s, %s);"
			cur2.execute(sql,(hit_id, word_id, synonym, translation))

		for i in range(settings["synonyms_num_knowns"]):
			sql="INSERT INTO synonymshitsdata (hit_id, word_id, synonym, translation) VALUES (%s, %s, %s, %s);"
			synonym, translation=syn()
			cur2.execute(sql,(hit_id, 0, synonym, translation))

	conn.commit()

	conn.close()
	

logging.info("synonyms hit creation pipeline - FINISH")
