
"""
select * from similar_hits_results, assignments, hits where quality !=null and mturk_status=null
for each:
	if quality< -0.25:
		reject
		for hit : assignments=assignmetn +1
		update database
	if quality >=-0.25
		pay
		approve
		update database
		
"""

# -*- coding: utf-8 -*-

import mturk
import boto.mturk.connection
from settings import settings

import threading
import psycopg2

import json

import logging
import argparse

# command line parameters parsing
# loading proper settings file
# basic logging setup for console output

parser = argparse.ArgumentParser(description='Process QC/Similar HITs (run quality control and pay workers)',epilog="And that's how you'd do it")

parser.add_argument('--settings', default='settings', help='filename of settings file to use: settings (.py) will be used by default')
parser.add_argument('--level',default='INFO', choices=["DEBUG","INFO","WARNING","ERROR","CRITICAL"],help='logging level: e.g. DEBUG, INFO, etc.')

args = parser.parse_args()

print "debug level: ", args.level

# basic logging setup for console output
numeric_level = getattr(logging, args.level.upper(), None)
if not isinstance(numeric_level, int):
	raise ValueError('Invalid log level: %s' % args.level)

logging.basicConfig(
	format='%(asctime)s %(levelname)s %(message)s', 
	datefmt='%m/%d/%Y %I:%M:%S %p',
	level=numeric_level)


try:
	settings_module = __import__(args.settings) #, globals={}, locals={}, fromlist=[], level=-1
	settings=settings_module.settings
except ImportError: 
	import sys
	sys.stderr.write("Error: Can't find the file '%r.py' in the directory containing %r.\n" % (args.settings, args.settings))
	sys.exit(1)




logging.info("process ESL HITs (run quality control and pay workers) - START")

target_language = settings["target_language"]
logging.info("target language: %s" % (target_language))

try:
	conn = psycopg2.connect("dbname='"+settings["esl_dbname"]+"' user='"+settings["user"]+"' host='"+settings["host"]+"'")
	logging.info("successfully connected to database")
except:
	logging.error("unable to connect to the database")

cur=conn.cursor()
cur2=conn.cursor()


mturk_conn=mturk.conn()

#select all Graded assignment (with any  status including Approved/Rejected mturk_status) and pay workers and Approve/Reject them in MTurk
sql="""SELECT a.id, a.mturk_assignment_id, a.hit_id, a.data_status, a.worker_id, p.quality as worker_quality, p.total as worker_total, a.mturk_status, sh.mturk_hit_id 
		FROM assignments a, similar_hits sh, similar_workers_performance p 
		WHERE a.hit_id = sh.id and a.mturk_status ='Submitted' and a.data_status is not null
			and p.worker_id=a.worker_id;"""
cur.execute(sql)
rows=cur.fetchall()

for row in rows:
	assignment_id=str(row[0])
	mturk_assignment_id=str(row[1])
	hit_id=str(row[2])
	data_status=float(row[3])
	worker_id=str(row[4])
	worker_quality=float(row[5])
	worker_total=float(row[6])

	db_mturk_status=str(row[7]) # MTurk status (Approved/Rejected if worker was already paid)
	
	mturk_hit_id=str(row[8])
	
	#creating local vars to keep state
	mturk_status=''
	status=''
	
	print "worker: ", worker_id, " quality: ", worker_quality, " total: ", worker_total
		
	#approve all HITs of high quality workers
	if worker_quality>=0.75:
		mturk_status='Approved'
		
	#approve based on current assignment quality for medium quality workers
	else: 
		mturk_status='Rejected'

	#data_status - objective quality based on passed/failed controls
	#data_quality - subjective quality based on worker perforance (e.g. workers with 75%+ performance assumed being right all the time)
	data_quality=data_status

	# not bumping up data quality (control is easy enough)
	# if worker performance is > 75%, override his tasks' quality with good quality (e.g. 1)
	# if worker_quality>0.75:
	#	data_quality=1
	#	print "bumped up good worker's assignment quality"

	#pushing approve/reject status to Mechanical Turk
	#updating MTurk if it wasn't updated already
	if db_mturk_status=='Submitted':
		#if this assignment wasn't paid (e.g. Approved/Rejected) 
		if mturk_status=='Approved':			
			logging.info("approving assignment %s" % (mturk_assignment_id))
			try:
				#pass
				mturk_conn.approve_assignment(mturk_assignment_id, feedback=settings["similar_approve_feedback"])
			except boto.mturk.connection.MTurkRequestError, err:
				print "mturk api error while approving assignment"
		elif mturk_status=='Rejected':
			logging.info("rejecting assignment %s" % (mturk_assignment_id))
			try:
				reject_feedback='Thank you for working on this assignment. Unfortunately, we had to reject it because you failed on control questions embedded into this task. Your overall performance on tasks of this type is {:.2%} correct answers.'.format(worker_quality)
	
				#this settings replaced by polite rejection message			
				#mturk_conn.reject_assignment(mturk_assignment_id, feedback=settings["synonyms_reject_feedback"])
				print reject_feedback
				mturk_conn.reject_assignment(mturk_assignment_id, feedback=reject_feedback)
			except boto.mturk.connection.MTurkRequestError, err:
				print "mturk api error while rejecting assignment"

		#if data quality is not perfect, rerun this assignment again
		if data_status!=1:
			try:
				#increase number of assignments on related HIT
				mturk_conn.extend_hit(mturk_hit_id, assignments_increment=1)

			except boto.mturk.connection.MTurkRequestError, err:
				print "mturk api error while incrementing assignment"

	else:
		#we can't change MTurk status if it is already Approved/Rejected
		mturk_status=db_mturk_status


	status='Closed'
	
	#update assignment mturk_status and status based on local vars in database
	sql2="UPDATE assignments SET mturk_status=%s, status=%s, data_status=%s, data_quality=%s WHERE id=%s;"
	cur2.execute(sql2, (mturk_status, status, data_status, data_quality, assignment_id))
	conn.commit()
	logging.debug("assignment %s processed in full" % (assignment_id))
	

conn.commit()
conn.close()

logging.info("FINISH")


	
