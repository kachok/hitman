# -*- coding: utf-8 -*-


import mturk
from settings import settings

from langlib import get_languages_list

import psycopg2

from itertools import islice, chain

import json


# basic logging setup for console output
import logging
logging.basicConfig(
	format='%(asctime)s %(levelname)s %(message)s', 
	datefmt='%m/%d/%Y %I:%M:%S %p',
	level=logging.INFO)

logging.info("pay for first 10 tasks - START")

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



cur = conn.cursor()
cur2 = conn.cursor()
	
sql="SELECT * FROM workers;"
cur.execute(sql)
rows = cur.fetchall()

	
mturk_conn=mturk.conn()

for row in rows:
	worker_id=str(row[0])
	
	sql2="select * from assignments where worker_id=%s order by submit_time asc limit 10;"
	cur2.execute(sql2, (worker_id,))
	rows2 = cur2.fetchall()
	
	for row2 in rows2:
		mturk_assignment_id=str(row[1])
		mturk_status=str(row[8])
	
		if mturk_status=='':
			print "approve", mturk_assignment_id
			#mturk_conn.approve_assignment(mturk_assignment_id, feedback=settings["synonyms_approve_feedback"])
		else:
			print "assignment is already ", mturk_status


conn.close()
	

logging.info("FINISH")

#import uuid
#str(uuid.uuid1())
