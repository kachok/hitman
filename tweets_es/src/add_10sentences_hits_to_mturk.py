# -*- coding: utf-8 -*-


import mturk
from settings import settings

import wikilanguages

import psycopg2

from itertools import islice, chain

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

logging.info("ten sentences HITs creation in MTurk- START")

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

try:
	conn = psycopg2.connect("dbname='"+settings["dbname"]+"' user='"+settings["user"]+"' host='"+settings["host"]+"'")
	logging.info("successfully connected to database")
except:
	logging.error("unable to connect to the database")


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
	sql="SELECT id from hittypes where language_id=%s and typename='tensentences';"
	cur.execute(sql, (lang_id,))
	rows = cur.fetchall()

	hittype_id=0
	for row in rows:
		hittype_id=str(row[0])

	langs_properties[lang]["hittype_id"]=hittype_id

	print hittype_id, lang
	#break


	cur = conn.cursor()
	cur2 = conn.cursor()


	sql="SELECT id from languages where prefix=%s;"
	cur.execute(sql, (lang,))
	rows = cur.fetchall()

	lang_id=0
	for row in rows:
		lang_id=row[0]

	sql="SELECT * from tensentences_hits WHERE language_id=%s and mturk_hit_id = '';"
	cur.execute(sql, (lang_id,))
	rows = cur.fetchall()

	web_endpoint='http://'+settings["web_enpoint_domain"]+settings["web_endpoint_tensentences_hit_path"]+"/"+lang

	for row in rows:

		timeout=5
		passed=False
		
		while not passed:
			#fetching unique UUID for hit to be created in MTurk
			guid=row[2]
			mturk_hittype_id=row[8]
			operation="CreateHIT"
			parameters2={
				"HITTypeId":mturk_hittype_id,
				'Question':'<ExternalQuestion xmlns="http://mechanicalturk.amazonaws.com/AWSMechanicalTurkDataSchemas/2006-07-14/ExternalQuestion.xsd"><ExternalURL>'+web_endpoint+'</ExternalURL><FrameHeight>800</FrameHeight></ExternalQuestion>',
				"Title":"Translate "+(u"Translate tweets from "+langs_properties[lang]["name"]+u" to English").encode('utf-8'),
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
		
		
			sql="UPDATE hits SET mturk_hit_id=%s, assignments=%s WHERE uuid=%s;"
			cur2.execute(sql,(mturk_hit_id, settings["max_assignments"], guid))
			conn.commit()
		

conn.close()
	

logging.info("ten sentences HITs creation in MTurk - FINISH")


