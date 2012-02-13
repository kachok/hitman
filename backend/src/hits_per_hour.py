# -*- coding: utf-8 -*-

from datetime import datetime

import mturk
from settings import settings

from langlib import get_languages_list

import psycopg2

# basic logging setup for console output
import logging
logging.basicConfig(
	format='%(asctime)s %(levelname)s %(message)s', 
	datefmt='%m/%d/%Y %I:%M:%S %p',
	level=logging.INFO)

logging.info("run through bunch of assignments and calculate HITs per hour rate - START")

target_language = settings["target_language"]
logging.info("target language: %s" % (target_language))

# generate list of languages to process
#TODO: for now just load this list from data/languages/languages.txt (list of wikipedia languages with 10,000+ articles)

langs=[] #list of languages represented as wikipedia prefixes e.g. xx - xx.wikipedia.org
langs=get_languages_list(settings["languages_file"], target_language)


total_assignments=0
total_time=0

try:
	conn = psycopg2.connect("dbname='"+settings["dbname"]+"' user='"+settings["user"]+"' host='"+settings["host"]+"'")
	logging.info("successfully connected to database")
except:
	logging.error("unable to connect to the database")




#get all words from vocabulary
cur = conn.cursor()

#getting language_id from database
sql="SELECT id from languages where prefix=%s;"
cur.execute(sql, (target_language,))
rows = cur.fetchall()

lang_id=0
for row in rows:
	lang_id=str(row[0])


sql="SELECT distinct(mturk_hit_id),l.name  from assignments a, hits h, languages l where a.hit_id=h.id and h.language_id=l.id;"
cur.execute(sql)
rows = cur.fetchall()

for row in rows:
	mturk_hit_id=str(row[0])
	language=str(row[1])
	#print mturk_hit_id
	
	timeout=5
	passed=False
	
	mturk_conn=mturk.conn()
	
	assignments=mturk_conn.get_assignments(hit_id=mturk_hit_id)
	
	for assgnmnt in assignments:
		mturk_worker_id=assgnmnt.WorkerId
		mturk_assignment_id=assgnmnt.AssignmentId
		accept_time=assgnmnt.AcceptTime
		submit_time=assgnmnt.SubmitTime
		status=assgnmnt.AssignmentStatus
		

		#print accept_time
		#print submit_time
		
		at=datetime.strptime(accept_time, "%Y-%m-%dT%H:%M:%SZ")
		st=datetime.strptime(submit_time, "%Y-%m-%dT%H:%M:%SZ")
		#date_object = datetime.strptime('Jun 1 2005  1:33PM', '%b %d %Y %I:%M%p')	#2012-02-06T18:12:18Z
		
		
		#time in secons
		time=st-at
		#print time
		#print time.seconds
		total_assignments+=1
		
		total_time=total_time+time.seconds

		print time.seconds, ",", mturk_worker_id, ",", language

		
		
print "total assignments: ", total_assignments
print "total time in seconds: ", total_time, " in hours:", total_time/3600
print "avg seconds per HITs: ", float(total_time)/float(total_assignments)
print "HITs per hour: ", float(3600)/(float(total_time)/float(total_assignments))
conn.close()
	

logging.info("FINISH")

#import uuid
#str(uuid.uuid1())
