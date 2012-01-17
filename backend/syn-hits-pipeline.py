# -*- coding: utf-8 -*-


import mturk
from settings import settings

from langlib import get_languages_list, get_languages_properties

import psycopg2

from itertools import islice, chain

import uuid
import urllib

from time import sleep

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

logging.info("synonyms hit creation pipeline in MTurk- START")

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

lang="en"
# step #1 register HIT type for current language

operation="RegisterHITType"

parameters2=settings["synonymsHITtype"]


output=mturk.call_turk(operation, parameters2)
logging.debug("RegisterHITType response: %s" % (output))
hittype_id= mturk.get_val(output, "HITTypeId")
logging.info("HIT type for language: %s created with id: %s" % (lang, hittype_id))


#get all words from synonyms
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


sql="INSERT INTO hittypes (mturk_hittype_id, name, language_id, language, typename) VALUES (%s, %s, %s, %s, %s);"
cur.execute(sql,(hittype_id, "Synonyms HIT for English", lang_id, lang, "synonyms"))
conn.commit()
mturk_hittype_id=hittype_id

# iterate over each language individually
for i, lang in enumerate(langs):
	
	logging.info("processing language: %s (#%s out of %s) " %(lang,i+1,len(langs)))
	
	hittype_id= mturk_hittype_id
	print hittype_id, lang
	#break


	#get all words from synonyms
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

	sql="SELECT * from synonymshits WHERE language_id=%s and mturk_hit_id is null;"
	cur.execute(sql, (lang_id,))
	rows = cur.fetchall()

	web_endpoint='http://'+settings["web_enpoint_domain"]+settings["web_endpoint_synonyms_hit_path"]

	for row in rows:

		timeout=5
		passed=False
		
		while not passed:
			#fetching unique UUID for hit to be created in MTurk
			guid=row[2]
			operation="CreateHIT"
			parameters2={
				"HITTypeId":hittype_id,
				'Question':'<ExternalQuestion xmlns="http://mechanicalturk.amazonaws.com/AWSMechanicalTurkDataSchemas/2006-07-14/ExternalQuestion.xsd"><ExternalURL>'+web_endpoint+'</ExternalURL><FrameHeight>800</FrameHeight></ExternalQuestion>',
				"Title":"Mark pairs of words as synonyms or not in English",
				'LifetimeInSeconds':settings["lifetimeinseconds"],
				"MaxAssignments":settings["max_assignments"],
				"UniqueRequestToken":guid,
			}
			output= mturk.call_turk(operation, parameters2)
			try:
				mturk_hit_id=mturk.get_val(output, "HITId")
				passed=True
			except:
				passed=False
				timeout=timeout*2
				print "Sleep for %s seconds " % (timeout)
				sleep(timeout)

			logging.info("new HIT created with id: %s" % (mturk_hit_id))
		
		
			sql="UPDATE synonymshits SET mturk_hit_id=%s WHERE uuid=%s;"
			cur2.execute(sql,(mturk_hit_id, guid))
			conn.commit()
		

	conn.close()
	

logging.info("synonyms hit creation pipeline - FINISH")
