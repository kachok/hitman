#select h.id, h.mturk_hit_id, count(*) from similar_hits h, assignments a where a.hit_id=h.id and a.data_status=1 group by h.id, h.mturk_hit_id;

# this query will show all unbalanced similar HITs:
#select h.id, h.mturk_hit_id, count(*) from similar_hits h, assignments a where a.hit_id=h.id and a.data_status=1 group by h.id, h.mturk_hit_id having count(*)<3;

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




logging.info("adjust Similar HITs assignments - START")

target_language = settings["target_language"]
logging.info("target language: %s" % (target_language))

try:
	conn = psycopg2.connect("dbname='"+settings["dbname"]+"' user='"+settings["user"]+"' host='"+settings["host"]+"'")
	logging.info("successfully connected to database")
except:
	logging.error("unable to connect to the database")

cur=conn.cursor()
cur2=conn.cursor()


mturk_conn=mturk.conn()

#select all Graded assignment (with any  status including Approved/Rejected mturk_status) and pay workers and Approve/Reject them in MTurk
sql="""select h.id, h.mturk_hit_id, count(*) from similar_hits h, assignments a where a.hit_id=h.id and a.data_status=1 group by h.id, h.mturk_hit_id;"""
cur.execute(sql)
rows=cur.fetchall()

for row in rows:
	hit_id=str(row[0])
	mturk_hit_id=str(row[1])
	count=int(row[2])
	
	if count<3:
		try:
			#pass
			print mturk_hit_id, count
			mturk_conn.extend_hit(mturk_hit_id, assignments_increment=3-count)
		except boto.mturk.connection.MTurkRequestError, err:
				print "mturk api error while adjusting assignment"
conn.close()

logging.info("FINISH")


