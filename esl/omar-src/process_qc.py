# -*- coding: utf-8 -*-
from settings import settings
import psycopg2
import json
import logging
import codecs
import argparse
import datetime
import qc

# command line parameters parsing
# loading proper settings file
# basic logging setup for console output

parser = argparse.ArgumentParser(description='Get buffered assignments and results from Mechanical Turk into database',epilog="And that's how you'd do it")

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
	settings_module = __import__(args.settings) 
	settings=settings_module.settings
except ImportError: 
	import sys
	sys.stderr.write("Error: Can't find the file '%r.py' in the directory containing %r.\n" % (args.settings, args.settings))
	sys.exit(1)

	
logging.info("insert buffered assignments from MTurk into database - START")


target_language = settings["target_language"]
logging.info("target language: %s" % (target_language))

conn = psycopg2.connect("dbname='"+settings["esl_dbname"]+"' user='"+settings["user"]+"' host='"+settings["host"]+"'")

cur=conn.cursor()
sql="SELECT * from esl_assignments where status='Open';"
cur.execute(sql)
rows=cur.fetchall()

#gradelog = codecs.open("apprej.log", encoding='utf-8', mode='w+', errors='replace')
appr = 0
rej = 0
for row in rows:
		
	assign_id = row[0]
	hit_id = row[2]
	worker_id = row[3]

	sql = "SELECT worker_id from esl_workers WHERE id=%s;"
	cur.execute(sql, (worker_id, ))
	worker = cur.fetchone()[0]
	
#	logging.info("Grading assignment %s in hit %s by worker %s" % (assign_id, hit_id, worker))

	result = qc.grade_controls(hit_id, assign_id, worker) #, log=gradelog)
	if(result == 0):
		rej += 1
	else:
		appr += 1
	cur.execute(sql, (assign_id, ))
	
conn.commit()
#gradelog.close()

#sql = "SELECT * from esl_appr_buffer WHERE status='APPROVE'"
#cur.execute(sql)
#appr = cur.rowcount
#sql = "SELECT * from esl_appr_buffer WHERE status='REJECT'"
#cur.execute(sql)
#rej = cur.rowcount

logging.info("Set to APPROVE %s assignments and REJECT %s assignments. See apprej.log to confirm approvals and rejects before running approverej.py" %(str(appr), str(rej)))

# cleanup
logging.info("FINISH")

