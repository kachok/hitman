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

parser = argparse.ArgumentParser(description='Block poor quality/fraudulent workers and reject all their assignments',epilog="And that's how you'd do it")

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




logging.info("Block poor quality/fraudulent workers and reject all their assignments - START")

target_language = settings["target_language"]
logging.info("target language: %s" % (target_language))

try:
	conn = psycopg2.connect("dbname='"+settings["dbname"]+"' user='"+settings["user"]+"' host='"+settings["host"]+"'")
	logging.info("successfully connected to database")
except:
	logging.error("unable to connect to the database")

cur=conn.cursor()


# mark workers with 10+ assignmetns submitted and 50%+ controls failed (on Vocabulary HITs) as blocked in workers table
sql="""update workers set banned=true
where id in
(select t.worker_id from 
(select id, avg(quality) as quality2, sum(total) as total2 from voc_hits_workers_performance group by id) t2, 
(select worker_id, count(*) as total_empty from voc_hits_results vhr, assignments a where vhr.assignment_id=a.id  and vhr.is_control=0 and length(reason)>1 group by worker_id) t, 
(select worker_id, count(*) as total_all from voc_hits_results vhr, assignments a where vhr.is_control=0 and vhr.assignment_id=a.id group by worker_id) t3 
where t.worker_id=t2.id and t.worker_id=t3.worker_id
and cast(total_empty as float)/cast(total_all as float)>0.5 and total_all>20 and t.worker_id=id
);"""
cur.execute(sql)
conn.commit();


mturk_conn=mturk.conn()

#select all banned workers and block them on MTurk
sql="SELECT mturk_worker_id, id from workers where banned=true;"
cur.execute(sql)
rows=cur.fetchall()

for row in rows:
	mturk_worker_id=str(row[0])
	worker_id=str(row[1])

	print "blocking worker: ", mturk_worker_id, " id:",worker_id
	reason="We are sorry, but you are blocked from working on our HITs. Quality of your work is less than 50%, meaning you failed more than half of controls embedded into our tasks."
	mturk_conn.block_worker(mturk_worker_id, reason)

	cur2=conn.cursor()

	#select open assignmetns that belongs to banned workers
	sql2="SELECT  a.id, a.mturk_assignment_id, a.mturk_status FROM assignments a WHERE a.worker_id=%s;"
	cur2.execute(sql2, (worker_id,))
	rows2=cur2.fetchall()
	for row2 in rows2:
		assignment_id=str(row2[0])
		mturk_assignment_id=str(row2[1])
		mturk_status=str(row2[2]) # MTurk status (Approved/Rejected if worker was already paid)
		
		if mturk_status=='Submitted':
			logging.info("rejecting assignment %s" % (mturk_assignment_id))
			
			try:
				reject_feedback='Thank you for working on this assignment. Unfortunately, we had to reject it because quality of your work is less than 50%, meaning you failed more than half of controls embedded into our tasks.'
	
				mturk_conn.reject_assignment(mturk_assignment_id, feedback=reject_feedback)
				print "rejected", mturk_assignment_id, reject_feedback
			except boto.mturk.connection.MTurkRequestError, err:
				print "mturk api error while rejecting assignment"

		mturk_status='Rejected'
		status='Closed'
		data_quality=0
		data_status=0
		
		#update assignment mturk_status and status based on local vars in database
		sql2="UPDATE assignments SET mturk_status=%s, status=%s, data_status=%s, data_quality=%s WHERE id=%s;"
		cur2.execute(sql2, (mturk_status, status, data_status, data_quality, assignment_id))
		conn.commit()
		logging.info("assignment %s processed in full" % (assignment_id))
	
conn.close()


logging.info("FINISH")


