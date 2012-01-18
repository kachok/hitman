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

logging.info("get assignments 2 from MTurk pipeline- START")

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

	
	sql="SELECT mturk_hit_id from synonymshits where language_id=%s;"
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
			status=assgnmnt.AssignmentStatus
			results={}
			for i in assgnmnt.answers[0]:
				results[i.fields[0][0]]=i.fields[0][1]
				
			result=json.dumps(results)

			control=""
			quality=""

			sql="SELECT add_synonymshitassignment(%s, %s, %s, %s, %s, %s, %s, %s);"
			cur.execute(sql,(mturk_hit_id, assignment_id, worker_id, status, result, submit_time, control, quality))
			
			assignment_id = cur.fetchone()[0]			
			
			
			#for i in range(settings["num_knowns"]+settings["num_unknowns"]):
			for key in results.keys():
				if key.find("pair")==0:
					pairnum=key
					pair_id=pairnum[5:14]
					is_control=pairnum[14:15]
					are_synonyms=results[key]
					misspelled=""
					try:
						misspelled=results["misspelled_"+pair_id]
					except KeyError:
						pass
						
					quality=""
					control=""

					sql="SELECT add_synonymshitresult(%s, %s, %s, %s, %s, %s, %s);"
					cur.execute(sql,(assignment_id, int(pair_id), are_synonyms, misspelled, is_control, quality, control ))
					result_id = cur.fetchone()[0]
					conn.commit()					
			
				
			"""	
			A3STHRZDWNG7UO 247J51Y7QEOZQMEGQEJTPOFXRSKFCA 2012-01-17T18:59:27Z
			answers  1
			{"pair-0000009441": "no", "city": "ATLANTA", "survey_is_native_english_speaker": "no", 
			"pair-0000009471": "yes", 
			"pair-0000009461": "no", "ip": "74.125.45.100", "region": "GEORGIA", 
			"pair-0000009491": "no", 
			"pair-0000009481": "yes", "surveyname": "englishspeakersurvey", 
			"pair-0000009501": "no", "survey_what_country": "", 
			"pair-0000009431": "yes", "survey_years_speaking_english": "", "survey_what_country_born": "", 
			"pair-0000009451": "yes"}
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
	

logging.info("get assignments 2 from MTurk pipeline - FINISH")

#import uuid
#str(uuid.uuid1())
