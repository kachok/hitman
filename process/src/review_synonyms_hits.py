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

parser = argparse.ArgumentParser(description='Review Synonyms HITs (run quality control and pay workers)',epilog="And that's how you'd do it")

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




logging.info("review Synonyms HITs (run quality control and pay workers) - START")

target_language = settings["target_language"]
logging.info("target language: %s" % (target_language))

try:
	conn = psycopg2.connect("dbname='"+settings["dbname"]+"' user='"+settings["user"]+"' host='"+settings["host"]+"'")
	logging.info("successfully connected to database")
except:
	logging.error("unable to connect to the database")

"""
--grade all controls first
update syn_hits_results set quality=1 where is_control=2 and are_synonyms='no';
update syn_hits_results set quality=0 where is_control=2 and are_synonyms!='no';
update syn_hits_results set quality=1 where is_control=1 and are_synonyms!='no';
update syn_hits_results set quality=0 where is_control=1 and are_synonyms='no';

--update all non-controls based on average controls quality
update syn_hits_results set quality=avg_quality from (select assignment_id as t_id, avg(quality) as avg_quality from syn_hits_results where is_control>0 group by assignment_id) t where t_id=assignment_id and is_control=0;
update assignments set data_status=avg_quality, status='Graded' from (select assignment_id as t_id, avg(quality) as avg_quality from syn_hits_results where is_control>0 group by assignment_id) t where t_id=id;
"""
cur=conn.cursor()

sql="update syn_hits_results set quality=1 where is_control=2 and are_synonyms='no';"
cur.execute(sql)
conn.commit();
sql="update syn_hits_results set quality=0 where is_control=2 and are_synonyms!='no';"
cur.execute(sql)
conn.commit();
sql="update syn_hits_results set quality=1 where is_control=1 and are_synonyms!='no';"
cur.execute(sql)
conn.commit();
sql="update syn_hits_results set quality=0 where is_control=1 and are_synonyms='no';";
cur.execute(sql)
conn.commit();


sql="update syn_hits_results set quality=avg_quality from (select assignment_id as t_id, avg(quality) as avg_quality from syn_hits_results where is_control>0 group by assignment_id) t where t_id=assignment_id and is_control=0;"
cur.execute(sql)
conn.commit();


"""
update assignments 
set data_status=avg_quality, status='Graded' 
from (select assignment_id as t_id, avg(quality) as avg_quality 
		from syn_hits_results 
		where is_control>0 
		group by assignment_id) t 
where t_id=id;
"""

sql="update assignments set data_status=avg_quality, status='Graded' from (select assignment_id as t_id, avg(quality) as avg_quality from syn_hits_results where is_control>0 group by assignment_id) t where t_id=id;"
cur.execute(sql)
conn.commit();

mturk_conn=mturk.conn()

#select all Graded assignment (with any  status including Approved/Rejected mturk_status) and pay workers and Approve/Reject them in MTurk
sql="SELECT a.*, sh.mturk_hit_id FROM assignments a, syn_hits sh WHERE a.hit_id = sh.id and a.status='Graded';"
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
	
	#fetch current worker performance stats
	cur2=conn.cursor()
	sql2="SELECT * from syn_hits_workers_performance where id=%s;"
	cur2.execute(sql2, (worker_id,))
	rows2=cur2.fetchall()
	worker_quality=0
	worker_total=0
	
	for row2 in rows2:
		worker_quality=float(row2[1])
		worker_total=float(row2[2])
	#worker performance fetched

	#creating local vars to keep state
	mturk_status=''
	status=''
		
	#newbie worker approve first 10 tasks
	if worker_total<10:
		mturk_status='Approved'
		print "approved newbie worker's assignment"
	else:
		#approve all HITs of high quality workers
		if worker_quality>0.75:
			mturk_status='Approved'
			
		#approve based on current assignment quality for medium quality workers
		elif worker_quality>0.5:
			#approve only if both controls where correct (e.g. data_status==1)
			if data_status==1:
				mturk_status='Approved'
			else:
				mturk_status='Rejected'
			
		#reject all HITs of low quality workers
		elif worker_quality<=0.5:
			mturk_status='Rejected'

	#data_status - objective quality based on passed/failed controls
	#data_quality - subjective quality based on worker perforance (e.g. workers with 75%+ performance assumed being right all the time)
	data_quality=data_status

	#if worker performance is > 75%, override his tasks' quality with good quality (e.g. 1)
	if worker_quality>0.75:
		data_quality=1
		print "bumped up good worker's assignment quality"


	"""
	#saving status based on quality
	#and updating HIT counters (and adding extra assignments if results are of bad quality)
	if data_quality==1:
		status='Closed'
		
		sql2="UPDATE hits SET approved=approved+1 WHERE id=%s;"
		cur2.execute(sql2, (hit_id,))
		conn.commit()

	else:
		status='Closed'

		#increment only if this assignment is not already rejected (based on DB status (that comes from MTurk))
		if (db_mturk_status!='Rejected'):		
			logging.info("incrementing assignment for hit %s" % (mturk_hit_id))
			try:
				mturk_conn.extend_hit(mturk_hit_id, assignments_increment=1)
			except boto.mturk.connection.MTurkRequestError, err:
				print "mturk api error while incrementing assignments on HIT"

		sql2="UPDATE hits SET rejected=rejected+1, assignments=assignments+1 WHERE id=%s;"
		cur2.execute(sql2, (hit_id,))
		conn.commit()
	"""

	#pushing approve/reject status to Mechanical Turk
	#updating MTurk if it wasn't updated already
	if db_mturk_status=='Submitted':
		#if this assignment wasn't paid (e.g. Approved/Rejected) 
		
		if mturk_status=='Approved':			
			logging.info("approving assignment %s" % (mturk_assignment_id))
			try:
				mturk_conn.approve_assignment(mturk_assignment_id, feedback=settings["synonyms_approve_feedback"])
			except boto.mturk.connection.MTurkRequestError, err:
				print "mturk api error while approving assignment"
		elif mturk_status=='Rejected':
			logging.info("rejecting assignment %s" % (mturk_assignment_id))
			try:
				reject_feedback='Thank you for working on this assignment. Unfortunately, we had to reject it because you failed on control questions embedded into this task. Your overall performance on tasks of this type is {:.2%} correct answers.'.format(worker_quality)
	
				#this settings replaced by polite rejection message			
				#mturk_conn.reject_assignment(mturk_assignment_id, feedback=settings["synonyms_reject_feedback"])
				mturk_conn.reject_assignment(mturk_assignment_id, feedback=reject_feedback)
			except boto.mturk.connection.MTurkRequestError, err:
				print "mturk api error while rejecting assignment"


	status='Closed'
	
	#update assignment mturk_status and status based on local vars in database
	sql2="UPDATE assignments SET mturk_status=%s, status=%s, data_status=%s, data_quality=%s WHERE id=%s;"
	cur2.execute(sql2, (mturk_status, status, data_status, data_quality, assignment_id))
	conn.commit()
	logging.debug("assignment %s processed in full" % (assignment_id))
	

sql="UPDATE assignments SET status='Closed' WHERE status='Graded' and (mturk_status!='Approved' or mturk_status!='Rejected');"
cur.execute(sql)
conn.commit()

conn.close()


logging.info("FINISH")


