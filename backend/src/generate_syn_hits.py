# -*- coding: utf-8 -*-


import mturk
from settings import settings

from langlib import get_languages_list, get_languages_properties

import psycopg2

from itertools import islice, chain

import uuid




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

try:
	conn = psycopg2.connect("dbname='"+settings["dbname"]+"' user='"+settings["user"]+"' host='"+settings["host"]+"'")
	logging.info("successfully connected to database")
except:
	logging.error("unable to connect to the database")


cur = conn.cursor()



lang="en"
# step #1 register HIT type for current language

#getting language_id from database
sql="SELECT id from languages where prefix=%s;"
cur.execute(sql, (lang,))
rows = cur.fetchall()

target_lang_id=0
for row in rows:
	target_lang_id=str(row[0])

operation="RegisterHITType"

parameters2=settings["synonymsHITtype"]


output=mturk.call_turk(operation, parameters2)
logging.debug("RegisterHITType response: %s" % (output))
mturk_hittype_id= mturk.get_val(output, "HITTypeId")
logging.info("HIT type for language: %s created with id: %s" % (lang, mturk_hittype_id))



#getting language_id from database
sql="SELECT id from languages where prefix=%s;"
cur.execute(sql, (lang,))
rows = cur.fetchall()

lang_id=0
for row in rows:
	lang_id=str(row[0])


sql="SELECT add_hittype (%s, %s, %s, %s);"
cur.execute(sql,("Synonyms HIT for English", mturk_hittype_id,  lang_id, "synonyms"))
hittype_id = cur.fetchone()[0]
	
conn.commit()


	
logging.info("processing all languages altogether: %s " %(len(langs)))

cur = conn.cursor()
cur2 = conn.cursor()


#select all Submitted assignments
logging.info("select all submitted assignements of syn type")
sql="SELECT vas.* from voc_assignments_submitted vas, hits h where vas.hit_id=h.id"

cur.execute(sql)
rows=cur.fetchall()
for row in rows:
	assignment_id=str(row[0])
	worker_id=str(row[3])
	
	print "processing - ", assignment_id, worker_id
	
	#mark assignment as under review
	cur2 = conn.cursor()
	sql2="UPDATE assignments SET status='Under Review' WHERE id=%s;"
	cur2.execute(sql2, (assignment_id,))
	conn.commit()
	print "marked assignment as Under Review"
	
	
	sql="select vhr.translation, d.translation from voc_hits_results vhr, dictionary d where reason='' and is_control='0' and d.id=vhr.word_id   and vhr.translation <> d.translation  and vhr.assignment_id=%s"	
	cur2.execute(sql, (assignment_id, ))
	rows2 = cur2.fetchall()
	print lang_id
	for row2 in rows2:
		translation=str(row2[0])
		synonym=str(row2[1])
		
		print translation, synonym
		
		cur3=conn.cursor()
		sql="select add_syn_hit_data(%s, %s, %s, %s);"
		cur3.execute(sql, (synonym, translation, 0, lang_id))
	
	conn.commit()
		


#sql="select vhr.translation, d.translation, assignment_id, word_id from voc_hits_results vhr, dictionary d where reason='' and is_control='0' and d.id=vhr.word_id and language_id=%s"
sql="select translation, synonym, id from syn_hits_data where hit_id is null"
cur.execute(sql)
rows = cur.fetchall()

web_endpoint='http://'+settings["web_enpoint_domain"]+settings["web_endpoint_synonyms_hit_path"]+"/"+lang

for batchiter in batch(rows, settings["synonyms_num_unknowns"]):

	guid=str(uuid.uuid4())

	sql="SELECT add_hit(%s, %s, %s, %s, %s, %s, %s);"
	cur2.execute(sql,("", guid, hittype_id, target_lang_id, 0, 0, 0))
	hit_id = cur2.fetchone()[0]

	logging.info("Batch ")
	for item in batchiter:
		#word_id=item[3]
		translation=item[0]
		synonym=item[1]
		data_id=item[2]
		#assignment_id=item[2] #this assignment id traced to vocabulary HITs assignments table primary key (so we can traverse back from QA)
		
		
		#sql="INSERT INTO syn_hits_data (hit_id, word_id, synonym, translation, voc_assignment_id, is_control) VALUES (%s, %s, %s, %s, %s, %s);"
		sql="UPDATE syn_hits_data SET hit_id=%s where id=%s;"
		cur2.execute(sql,(hit_id, data_id))
		#tied data to specific HIT

	# this will be handled on web side
	#for i in range(settings["synonyms_num_knowns"]):
	#	sql="INSERT INTO syn_hits_data (hit_id, synonym, translation, is_control, language_id) VALUES (%s, %s, %s, %s,%s);"
	#	synonym, translation=syn()
	#	cur2.execute(sql,(hit_id, synonym, translation,1, lang_id))

conn.commit()

	

conn.close()
	

logging.info("synonyms hit creation pipeline - FINISH")
