# -*- coding: utf-8 -*-


import mturk
from settings import settings

from langlib import get_languages_list, get_languages_properties

import psycopg2

# basic logging setup for console output
import logging
logging.basicConfig(
	format='%(asctime)s %(levelname)s %(message)s', 
	datefmt='%m/%d/%Y %I:%M:%S %p',
	level=logging.INFO)

logging.info("HIT Types migration pipeline - START")

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


#get all words from vocabulary
try:
	conn = psycopg2.connect("dbname='"+settings["dbname"]+"' user='"+settings["user"]+"' host='"+settings["host"]+"'")
	logging.info("successfully connected to database")
except:
	logging.error("unable to connect to the database")

cur = conn.cursor()


logging.info("generating HITTypes for each language")
# iterate over each language individually
for i, lang in enumerate(langs):
	
	logging.info("processing language: %s (#%s out of %s) " %(lang,i+1,len(langs)))
	
	cur = conn.cursor()

	#getting language_id from database
	sql="SELECT id from languages where prefix=%s;"
	cur.execute(sql, (lang,))
	rows = cur.fetchall()

	lang_id=0
	for row in rows:
		lang_id=str(row[0])


	#getting hittype_id from database
	sql="SELECT id from hittypes where language_id=%s and typename='vocabulary';"
	cur.execute(sql, (lang_id,))
	rows = cur.fetchall()

	hittype_id=0
	for row in rows:
		hittype_id=str(row[0])

	langs_properties[lang]["hittype_id"]=hittype_id

	print hittype_id, lang
	#break
	
	# step #1 register HIT type for current language

	operation="RegisterHITType"
	settings["vocabularyHITtype"]["Description"]=(u"Translate 10 words from "+langs_properties[lang]["name"]+u" to English").encode('utf-8')
	settings["vocabularyHITtype"]["Title"]=(u"Translate 10 words from "+langs_properties[lang]["name"]+u" to English").encode('utf-8')
	settings["vocabularyHITtype"]["Keywords"]=(u"translation, vocabulary, dictionary, "+langs_properties[lang]["name"]+u", English, language, research, JHU").encode('utf-8')

	parameters2=settings["vocabularyHITtype"]

	
	output=mturk.call_turk(operation, parameters2)
	logging.debug("RegisterHITType response: %s" % (output))
	mturk_hittype_id= mturk.get_val(output, "HITTypeId")
	logging.info("HIT type for language: %s created with id: %s" % (lang, mturk_hittype_id))


	
	sql="SELECT add_hittype (%s, %s, %s, %s);"
	cur.execute(sql,("Vocabulary HIT for "+langs_properties[lang]["name"], mturk_hittype_id,  lang_id, "vocabulary 2"))
	hittype_id2 = cur.fetchone()[0]
	
	conn.commit()
	langs_properties[lang]["hittype_id"]=hittype_id2
	
	
	sql="SELECT id from hittypes where language_id=%s and typename='vocabulary';"
	cur.execute(sql, (lang_id,))
	rows = cur.fetchall()

	hittype_id=0
	for row in rows:
		hittype_id=str(row[0])


	sql="SELECT mturk_hit_id, h.id, typename from hits h, hittypes ht where h.hittype_id=ht.id and h.language_id=%s and assignments>(rejected+approved);"
	cur.execute(sql,(lang_id,))
	rows = cur.fetchall()

	mturk_conn=mturk.conn()

	print "changing HIT types"
	for row in rows:
		mturk_hit_id=str(row[0])
		hit_id=str(row[1])
		typename=str(row[2])

		timeout=5
		passed=False
		
		mturk_conn.change_hit_type_of_hit(mturk_hit_id, mturk_hittype_id)


conn.close()
	

logging.info("HIT Types migration pipeline - FINISH")
