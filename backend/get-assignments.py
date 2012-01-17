# -*- coding: utf-8 -*-


import mturk
from settings import settings

from langlib import get_languages_list, get_languages_properties

import psycopg2

from itertools import islice, chain

import uuid
import urllib

import json

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

logging.info("get assignments from MTurk pipeline- START")

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


logging.info("getting assignments for HITs for each language")
# iterate over each language individually
for i, lang in enumerate(langs):
	
	logging.info("processing language: %s (#%s out of %s) " %(lang,i+1,len(langs)))
	

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

	
	sql="SELECT mturk_hit_id from vocabularyhits where language_id=%s;"
	cur.execute(sql,(lang_id,))
	rows = cur.fetchall()

	for row in rows:
		mturk_hit_id=str(row[0])

		timeout=5
		passed=False
		
		mturk_conn=mturk.conn()
		
		assignments=mturk_conn.get_assignments(hit_id=mturk_hit_id)
		
		for assgnmnt in assignments:
			worker_id=assgnmnt.WorkerId
			assignment_id=assgnmnt.AssignmentId
			submit_time=assgnmnt.SubmitTime
			
			results={}
			for i in assgnmnt.answers[0]:
				results[i.fields[0][0]]=i.fields[0][1]
				
			result=json.dumps(results)
			
			#for i in range(settings["num_knowns"]+settings["num_unknowns"]):
			for key in results.keys():
				if key.find("word")==0:
					wordnum=key
					num=wordnum[4:5]
					word_id=wordnum[6:15]
					is_control=wordnum[15:16]=="0"
					translation=results[key]
					reason=results["reason"+num]

					sql="SELECT add_vocabularyhitresult(%s, %s, %s, %s, %s, %s, %s, %s, %s);"
					cur.execute(sql,(mturk_hit_id, assignment_id, worker_id, result, submit_time, int(word_id), translation, reason, int(is_control)))
					result_id = cur.fetchone()[0]
					conn.commit()					
					
					
				
			"""	
			{
			"word1-0000011190": "is", "ip": "127.0.0.1", "surveyname": "foreignenglishspeakersurvey_Russian", 
			"word4-0000011180": "quantity", 
			"word5-0000011100": "not", 
			"word7-0000011290": "few", 
			"word2-0000011550": "to", "city": "-", 
			"word3-0000011390": "this", 
			"reason9": "", 
			"reason8": "", 
			"word0-0000011540": "many", 
			"reason3": "", 
			"reason2": "", 
			"reason1": "", 
			"reason0": "", 
			"reason7": "", 
			"reason6": "", 
			"reason5": "", 
			"reason4": "", "survey_years_speaking_foreign": "0", "survey_what_country": "US", "survey_years_speaking_english": "10", 
			"word6-0000011020": "USSR", 
			"word9-0000002891": "paiute", "survey_is_native_english_speaker": "yes", "region": "-", "survey_is_native_foreign_speaker": "no", "survey_what_country_born": "Asia", 
			"word8-0000002811": "frakia"}	
			"""

			
			

			sql="SELECT add_worker(%s, %s);"
			cur.execute(sql,(worker_id, "unknown"))
			db_worker_id = cur.fetchone()[0]


			ip=results["ip"]
			city=results["city"]
			region=results["region"]
			country=""
			zipcode=""
			lat=""
			lng=""
			timestamp=submit_time
			sql="SELECT add_location(%s, %s, %s, %s, %s, %s, %s, %s, %s);"
			cur.execute(sql,(db_worker_id, ip, city, region, country, zipcode, lat, lng, timestamp))

			#sql="SELECT add_foreignenglishspeakingsurvey(%s, %s, %s, %s, %s);"
			#cur.execute(sql,(db_worker_id, timestamp, native_speaker, years_speaking_foreign, native_english_speaker, years_speaking_english, country, born_country, language, language_id))

			conn.commit()

			print worker_id, assignment_id, submit_time
			print "answers ", len(assgnmnt.answers)
			print result
		
	conn.close()
	

logging.info("get assignments from MTurk pipeline - FINISH")

#import uuid
#str(uuid.uuid1())
