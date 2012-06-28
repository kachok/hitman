# -*- coding: utf-8 -*-


import mturk
from settings import settings

import wikilanguages

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

logging.info("similar hit creation pipeline - START")

target_language = settings["target_language"]
logging.info("target language: %s" % (target_language))

# generate list of languages to process
#TODO: for now just load this list from data/languages/languages.txt (list of wikipedia languages with 10,000+ articles)


langs=[] #list of languages represented as wikipedia prefixes e.g. xx - xx.wikipedia.org
langs=wikilanguages.load(settings["languages_file"])

logging.info("# of languages loaded: %s" %(len(langs)))
if len(langs)<=5:
	logging.info("languages are: %s" %(langs))

langs_properties={} #list of languages' properties (e.g. LTR vs RTL script, non latin characters, etc) 
langs_properties=wikilanguages.langs


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

parameters2=settings["similarHITtype"]


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
cur.execute(sql,("Similar translations HIT for English", mturk_hittype_id,  lang_id, "similar"))
hittype_id = cur.fetchone()[0]
	
conn.commit()


	
logging.info("processing all languages altogether: %s " %(len(langs)))

cur = conn.cursor()
cur2 = conn.cursor()



#sql="select vhr.translation, d.translation, assignment_id, word_id from voc_hits_results vhr, dictionary d where reason='' and is_control='0' and d.id=vhr.word_id and language_id=%s"
sql="select * from similar_hits_data where hit_id is null limit (select (count(*) / %s)*%s from similar_hits_data where hit_id is null);" % (settings["similar_num_unknowns"],settings["similar_num_unknowns"])
cur.execute(sql)
rows = cur.fetchall()

web_endpoint='http://'+settings["web_enpoint_domain"]+settings["web_endpoint_similar_hit_path"]+"/"+lang

for batchiter in batch(rows, settings["similar_num_unknowns"]):

	guid=str(uuid.uuid4())

	sql="SELECT add_hit(%s, %s, %s, %s, %s, %s, %s);"
	cur2.execute(sql,("", guid, hittype_id, target_lang_id, 0, 0, 0))
	hit_id = cur2.fetchone()[0]

	logging.info("Batch ")
	for item in batchiter:
		data_id=item[2]
		
		sql="UPDATE similar_hits_data SET hit_id=%s where id=%s;"
		cur2.execute(sql,(hit_id, data_id))
		#tied data to specific HIT

conn.commit()

	

conn.close()
	

logging.info("similar hit creation pipeline - FINISH")
