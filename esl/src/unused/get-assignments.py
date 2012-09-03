 # -*- coding: utf-8 -*-


import mturk
from settings import settings

#from langlib import get_languages_list, get_languages_properties

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

logging.info("esl hit creation pipeline in MTurk- START")

target_language = settings["target_language"]
logging.info("target language: %s" % (target_language))

# generate list of languages to process
#TODO: for now just load this list from data/languages/languages.txt (list of wikipedia languages with 10,000+ articles)

langs=['en'] #list of languages represented as wikipedia prefixes e.g. xx - xx.wikipedia.org
#langs=get_languages_list(settings["languages_file"], target_language)

logging.info("# of languages loaded: %s" %(len(langs)))
if len(langs)<=5:
	logging.info("languages are: %s" %(langs))

#langs_properties={} #list of languages' properties (e.g. LTR vs RTL script, non latin characters, etc) 
#langs_properties=get_languages_properties(settings["languages_properties_file"], target_language)


logging.info("getting assignments for HITs for each language")
# iterate over each language individually
for i, lang in enumerate(langs):
	
	logging.info("processing language: %s (#%s out of %s) " %(lang,i+1,len(langs)))
	

	#get all words from vocabulary
	try:
		conn = psycopg2.connect("dbname='esl2' user='epavlick' host='localhost'")
		logging.info("successfully connected to database")
	except:
		logging.error("unable to connect to the database")

	cur = conn.cursor()

	create = "CREATE TABLE esl_hits_data ( id serial NOT NULL, hit_id integer, esl_sentence_id integer, output character varying, data_quality real, language_id integer, CONSTRAINT esl_hits_data_id_pk PRIMARY KEY (id ));"
	
	cur.execute(create)


	#getting language_id from database
#	sql="SELECT id from languages where prefix=%s;"
#	cur.execute(sql, (lang,))
#	rows = cur.fetchall()
#
#	lang_id=0
#	for row in rows:
#		lang_id=str(row[0])

	
#	sql="SELECT mturk_hit_id from esl_hits_data where language_id=%s;"
	sql="SELECT mturk_hit_id from esl_hits_data where language_id=en;"
#	cur.execute(sql,(lang_id,))
	cur.execute(sql)
	rows = cur.fetchall()

	cur2=conn.cursor()

	for row in rows:
		mturk_hit_id=str(row[0])

		timeout=5
		passed=False
		
		conn2=mturk.conn()
		
		assignments=conn2.get_assignments(hit_id=mturk_hit_id)
		
		for assgnmnt in assignments:
			worker_id=assgnmnt.WorkerId
			assignment_id=assgnmnt.AssignmentId
			submit_time=assgnmnt.SubmitTime
			
			results={}
			for i in assgnmnt.answers[0]:
				results[i.fields[0][0]]=i.fields[0][1]
				
			result=json.dumps(results)

			print worker_id, assignment_id, submit_time
			print "answers ", len(assgnmnt.answers)
			print result

			sql2="INSERT into esl_hits_results ( mturk_hit_id,mturk_assignment_id,mturk_worker_id,results) VALUES( %s,%s,%s,%s);"
			cur2.execute(sql2, (mturk_hit_id, assignment_id, worker_id, result))
			print "saved to DB"		
			conn.commit()
			try:			
				conn2.approve_assignment(assignment_id, "Thank you!")
				print "approved HIT ", assignment_id
			except:
				print "already approved ", assignment_id
		conn2.disable_hit(mturk_hit_id)
		print "disable HIT ",mturk_hit_id
	conn.close()
	

logging.info("esl hit creation pipeline - FINISH")

#import uuid
#str(uuid.uuid1())
