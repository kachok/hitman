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

parser = argparse.ArgumentParser(description='Review Vocabulary HITs (run quality control and pay workers)',epilog="And that's how you'd do it")

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




logging.info("review Vocabulary HITs (run quality control and pay workers) - START")

target_language = settings["target_language"]
logging.info("target language: %s" % (target_language))

try:
	conn = psycopg2.connect("dbname='"+settings["dbname"]+"' user='"+settings["user"]+"' host='"+settings["host"]+"'")
	logging.info("successfully connected to database")
except:
	logging.error("unable to connect to the database")


#grade all controls that have result matching wiki-links translation first
#-- old version without -s : update voc_hits_results t set quality=1 where exists (select vhr.*, d.translation from voc_hits_results vhr, dictionary d where vhr.word_id=d.id and is_control=0 and upper(vhr.translation)=upper(d.translation) and t.id=vhr.id)
#update voc_hits_results t set quality=1 where exists (select vhr.*, d.translation from voc_hits_results vhr, dictionary d where vhr.word_id=d.id and is_control=0 and upper(trim(both ' ' from vhr.translation))=upper(trim(both ' ' from d.translation)) and t.id=vhr.id);

#pay to all workers on assignments with correct controls

#select a.id, mturk_assignment_id from voc_hits_results vhr, assignments a where vhr.assignment_id=a.id and is_control=0 and status!='Closed' group by a.id, mturk_assignment_id having sum(quality)=2;

#select all assignments with both controls graded
#select a.id, mturk_assignment_id from voc_hits_results vhr, assignments a where vhr.assignment_id=a.id and is_control=0 group by a.id, mturk_assignment_id having count(quality)=2

cur=conn.cursor()


sql="update voc_hits_results t set quality=1 where exists (select vhr.*, d.translation from voc_hits_results vhr, dictionary d where vhr.word_id=d.id and is_control=0 and upper(trim(both ' ' from vhr.translation))=upper(trim(both ' ' from d.translation)) and t.id=vhr.id);"
cur.execute(sql)
conn.commit();

mturk_conn=mturk.conn()

#mark all voc assignments that are fully graded but not closed yet and update their data_quality value
sql="""update assignments a set status='Graded', data_status=t.avg_quality
from
(select a.id, mturk_assignment_id, avg(quality) as avg_quality from voc_hits_results vhr, assignments a where vhr.assignment_id=a.id and is_control=0 and status!='Closed' group by a.id, mturk_assignment_id having count(quality)=2) t
where a.id=t.id;"""
cur.execute(sql)
conn.commit();




#select all Graded assignment (with any  status including Approved/Rejected mturk_status) and pay workers and Approve/Reject them in MTurk
sql="SELECT a.*, vh.mturk_hit_id, vh.language_id FROM assignments a, voc_hits vh WHERE a.hit_id = vh.id and a.status='Graded';"
cur.execute(sql)
rows=cur.fetchall()

cur.execute(sql)
rows=cur.fetchall()
for row in rows:
	assignment_id=str(row[0])
	mturk_assignment_id=str(row[1])
	hit_id=str(row[2])
	data_status=float(row[7])
	worker_id=str(row[3])
	db_mturk_status=str(row[8]) # MTurk status (Approved/Rejected if worker was already paid)
	
	mturk_hit_id=str(row[11])
	language_id=str(row[12]) 
	
	#fetch current worker performance stats
	cur2=conn.cursor()
	sql2="SELECT * from voc_hits_workers_performance where id=%s and language_id=%s;"
	cur2.execute(sql2, (worker_id,language_id,))
	rows2=cur2.fetchall()
	worker_quality=0
	worker_total=0
	
	for row2 in rows2:
		worker_quality=float(row2[2])
		worker_total=float(row2[3])
	#worker performance fetched

	#creating local vars to keep state
	mturk_status=''
	status=''
	
	print "---"	
	print "worker ", worker_id, " quality ", worker_quality, " total ",worker_total
	#newbie worker approve first 10 tasks
	if worker_total<10:
		mturk_status='Approved'
		print "approved newbie worker's assignment"
	else:
		#approve all HITs of high quality workers
		if worker_quality>0.75:
			mturk_status='Approved'
			
		#approve based on current assignment quality for medium quality workers
		elif worker_quality>0.45:
			#approve only if both controls where correct (e.g. data_status==1)
			if data_status>0.98:
				mturk_status='Approved'
			else:
				mturk_status='Rejected'
			
		#reject all HITs of low quality workers
		elif worker_quality<=0.45:
			mturk_status='Rejected'

	#data_status - objective quality based on passed/failed controls
	#data_quality - subjective quality based on worker perforance (e.g. workers with 75%+ performance assumed being right all the time)
	data_quality=data_status

	#if worker performance is > 75%, override his tasks' quality with good quality (e.g. 1)
	if worker_quality>0.75:
		data_quality=1
		print "bumped up good worker's assignment quality"


	

	#pushing approve/reject status to Mechanical Turk
	#updating MTurk if it wasn't updated already
	if db_mturk_status=='Submitted':
		#if this assignment wasn't paid (e.g. Approved/Rejected) 
		
		if mturk_status=='Approved':			
			logging.info("approving assignment %s" % (mturk_assignment_id))
			try:
				mturk_conn.approve_assignment(mturk_assignment_id, feedback=settings["vocabulary_approve_feedback"])
				print "approved", mturk_assignment_id
			except boto.mturk.connection.MTurkRequestError, err:
				print "mturk api error while approving assignment"
		elif mturk_status=='Rejected':
			logging.info("rejecting assignment %s" % (mturk_assignment_id))
			try:
				reject_feedback='Thank you for working on this assignment. Unfortunately, we had to reject it because you failed on control questions embedded into this task. Your overall performance on tasks of this type is {:.2%} correct answers.'.format(worker_quality)
	
				#this settings replaced by polite rejection message			
				#mturk_conn.reject_assignment(mturk_assignment_id, feedback=settings["synonyms_reject_feedback"])
				
				mturk_conn.reject_assignment(mturk_assignment_id, feedback=reject_feedback)
				print "rejected", mturk_assignment_id, reject_feedback
			except boto.mturk.connection.MTurkRequestError, err:
				print "mturk api error while rejecting assignment"


	status='Closed'
	
	#update assignment mturk_status and status based on local vars in database
	sql2="UPDATE assignments SET mturk_status=%s, status=%s, data_status=%s, data_quality=%s WHERE id=%s;"
	cur2.execute(sql2, (mturk_status, status, data_status, data_quality, assignment_id))
	conn.commit()
	logging.info("assignment %s processed in full" % (assignment_id))
	

sql="UPDATE assignments SET status='Closed' WHERE status='Graded' and (mturk_status!='Approved' or mturk_status!='Rejected');"
cur.execute(sql)
conn.commit()

conn.close()


logging.info("FINISH")


