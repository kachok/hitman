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
#update voc_hits_results t set quality=1 where exists (select vhr.*, d.translation from voc_hits_results vhr, dictionary d where vhr.word_id=d.id and is_control=0 and upper(vhr.translation)=upper(d.translation) and t.id=vhr.id)

#pay to all workers on assignments with correct controls

#select a.id, mturk_assignment_id from voc_hits_results vhr, assignments a where vhr.assignment_id=a.id group by a.id, mturk_assignment_id having sum(quality)=2;


cur=conn.cursor()


sql="update voc_hits_results t set quality=1 where exists (select vhr.*, d.translation from voc_hits_results vhr, dictionary d where vhr.word_id=d.id and is_control=0 and upper(trim(both ' ' from vhr.translation))=upper(trim(both ' ' from d.translation)) and t.id=vhr.id);"
cur.execute(sql)
conn.commit();

mturk_conn=mturk.conn()

#select all Graded assignment (with non Approved/Rejected mturk_status) and pay workers and Approve/Reject them in MTurk
sql="select a.id, mturk_assignment_id from voc_hits_results vhr, assignments a where vhr.assignment_id=a.id group by a.id, mturk_assignment_id having sum(quality)=2;"
cur.execute(sql)
rows=cur.fetchall()

cur2=conn.cursor()
for row in rows:
	assignment_id=str(row[0])
	mturk_assignment_id=str(row[1])
	
	mturk_status="Approved"
	status="Closed"
	
	logging.info("approving assignment %s" % (mturk_assignment_id))
	try:
		mturk_conn.approve_assignment(mturk_assignment_id, feedback=settings["vocabulary_approve_feedback"])
	except boto.mturk.connection.MTurkRequestError, err:
		print "mturk api error while approving assignment"

	#update assignment mturk_status and status based on local vars in database
	sql2="UPDATE assignments SET mturk_status=%s, status=%s WHERE id=%s;"
	cur2.execute(sql2, (mturk_status, status, assignment_id))
	conn.commit()
	logging.debug("assignment %s processed in full" % (assignment_id))
	

conn.close()


logging.info("FINISH")


