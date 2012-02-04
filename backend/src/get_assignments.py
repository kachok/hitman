# -*- coding: utf-8 -*-


import mturk
from settings import settings

from langlib import get_languages_list

import psycopg2

from itertools import islice, chain

import json


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

logging.info("get assignments from MTurk - START")

target_language = settings["target_language"]
logging.info("target language: %s" % (target_language))

# generate list of languages to process
#TODO: for now just load this list from data/languages/languages.txt (list of wikipedia languages with 10,000+ articles)

langs=[] #list of languages represented as wikipedia prefixes e.g. xx - xx.wikipedia.org
langs=get_languages_list(settings["languages_file"], target_language)

# add English to list of languages
langs.append(target_language)

logging.info("# of languages loaded: %s" %(len(langs)))
if len(langs)<=5:
	logging.info("languages are: %s" %(langs))


try:
	conn = psycopg2.connect("dbname='"+settings["dbname"]+"' user='"+settings["user"]+"' host='"+settings["host"]+"'")
	logging.info("successfully connected to database")
except:
	logging.error("unable to connect to the database")



logging.info("getting assignments for HITs for each language")
# iterate over each language individually
for i, lang in enumerate(langs):
	
	logging.info("processing language: %s (#%s out of %s) " %(lang,i+1,len(langs)))
	

	#get all words from vocabulary
	cur = conn.cursor()

	#getting language_id from database
	sql="SELECT id from languages where prefix=%s;"
	cur.execute(sql, (lang,))
	rows = cur.fetchall()

	lang_id=0
	for row in rows:
		lang_id=str(row[0])

	
	sql="SELECT mturk_hit_id, h.id, typename from hits h, hittypes ht where h.hittype_id=ht.id and h.language_id=%s and assignments>(rejected+approved);"
	cur.execute(sql,(lang_id,))
	rows = cur.fetchall()

	for row in rows:
		mturk_hit_id=str(row[0])
		hit_id=str(row[1])
		typename=str(row[2])

		timeout=5
		passed=False
		
		mturk_conn=mturk.conn()
		
		assignments=mturk_conn.get_assignments(hit_id=mturk_hit_id)
		
		for assgnmnt in assignments:
			mturk_worker_id=assgnmnt.WorkerId
			mturk_assignment_id=assgnmnt.AssignmentId
			submit_time=assgnmnt.SubmitTime
			status=assgnmnt.AssignmentStatus
			results={}
			for i in assgnmnt.answers[0]:
				results[i.fields[0][0]]=i.fields[0][1]
				
			result=json.dumps(results)

			mturk_status=""

			sql="SELECT add_worker(%s, %s);"
			cur.execute(sql,(mturk_worker_id, "unknown"))
			db_worker_id = cur.fetchone()[0]
			conn.commit()

			sql="SELECT add_assignment(%s, %s, %s, %s, %s, %s, %s);"
			cur.execute(sql,(mturk_assignment_id, hit_id, mturk_worker_id, status, submit_time, result, mturk_status))
			
			assignment_id = cur.fetchone()[0]	
			
			if typename=="vocabulary":
				#for i in range(settings["num_knowns"]+settings["num_unknowns"]):
				for key in results.keys():
					if key.find("word")==0:
						wordnum=key
						num=wordnum[4:5]
						word_id=wordnum[6:15]
						is_control=wordnum[15:16]=="0"
						translation=results[key]
						reason=results["reason"+num]

						sql="SELECT add_voc_hits_result(%s, %s, %s, %s, %s);"
						cur.execute(sql,(assignment_id, int(word_id), translation, reason, int(is_control)))
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

					
			
			if typename=="synonyms":
			
				#for i in range(settings["num_knowns"]+settings["num_unknowns"]):
				for key in results.keys():
					if key.find("pair")==0:
						pairnum=key
						pair_id=pairnum[5:14]
						pair_id_with_control=pairnum[5:15]
						is_control=pairnum[14:15]
						are_synonyms=results[key]
						misspelled=""
						try:
							misspelled=results["misspelled_"+pair_id_with_control]
						except KeyError:
							pass

						#debug for misspelled issue, fixed now
						#print "pair ",pair_id ," misspelled ", misspelled
						print "pair ", pair_id, " are_synonyms ", are_synonyms

						sql="SELECT add_syn_hits_result(%s, %s, %s, %s, %s);"
						cur.execute(sql,(assignment_id, int(pair_id), are_synonyms, misspelled, is_control))
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



			ip=results.get("ip","")
			city=results.get("city","")
			region=results.get("region","")
			country=results.get("country","")
			zipcode=results.get("zipcode","")
			lat=results.get("lat","")
			lng=results.get("lng","")
			timestamp=submit_time
			sql="SELECT add_location(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
			cur.execute(sql,(assignment_id, db_worker_id, ip, city, region, country, zipcode, lat, lng, timestamp))

			#sql="SELECT add_foreignenglishspeakingsurvey(%s, %s, %s, %s, %s);"
			#cur.execute(sql,(db_worker_id, timestamp, native_speaker, years_speaking_foreign, native_english_speaker, years_speaking_english, country, born_country, language, language_id))

			conn.commit()

			print mturk_worker_id, assignment_id, submit_time
			print "answers ", len(assgnmnt.answers)
			print result
		
conn.close()
	

logging.info("get assignments from MTurk - FINISH")

#import uuid
#str(uuid.uuid1())
