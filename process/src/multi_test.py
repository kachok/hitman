# -*- coding: utf-8 -*-
from settings import settings
import psycopg2

from psycopg2.pool import PersistentConnectionPool
from psycopg2.pool import ThreadedConnectionPool


import json

import logging
import argparse

import mturk

import threading

import Queue




# command line parameters parsing
# loading proper settings file
# basic logging setup for console output

parser = argparse.ArgumentParser(description='Get completed assignments and results from Mechanical Turk',epilog="And that's how you'd do it")

parser.add_argument('--settings', default='settings', help='filename of settings file to use: settings (.py) will be used by default')
parser.add_argument('--level',default='INFO', choices=["DEBUG","INFO","WARNING","ERROR","CRITICAL"],help='logging level: e.g. DEBUG, INFO, etc.')
parser.add_argument('--hittype',default='ALL', choices=["ALL","VOCABULARY", "SYNONYMS"], help='get assignments for HITs of specific types: VOCABULARY, SYNONYMS or ALL')
parser.add_argument('--coverage',default='ALL', choices=["ALL","OPENONLY"], help='get assignment for all or just open HITs: ALL/OPENONLY')

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




def do_work(conn, item):
	cur=conn.cursor()
	mturk_conn=mturk.conn()
	
	assignments=mturk_conn.get_assignments(hit_id=item["mturk_hit_id"])
	
	for assgnmnt in assignments:
		mturk_worker_id=assgnmnt.WorkerId
		mturk_assignment_id=assgnmnt.AssignmentId
		submit_time=assgnmnt.SubmitTime
		accept_time=assgnmnt.AcceptTime
		mturk_status=assgnmnt.AssignmentStatus
		
		results={}
		for i in assgnmnt.answers[0]:
			results[i.fields[0][0]]=i.fields[0][1]
			
		result=json.dumps(results)

		print "assignment ", mturk_assignment_id, " mturk_status ", mturk_status
		
		sql="INSERT INTO buffer_assignments (assignment_id, hit_id, worker_id, accept_time, submit_time, result, status) VALUES (%s, %s, %s, %s, %s, %s, %s);"
		cur.execute(sql,(mturk_assignment_id, item["hit_id"], mturk_worker_id, accept_time, submit_time, result, mturk_status))
		
		conn.commit()



def worker():
	while True:
		item = q.get()
		
		#print "thread: ", threading.currentThread().name
		
		conn=conn_pool.getconn()
		do_work(conn, item)
		q.task_done()



logging.info("get assignments (multithreaded) from MTurk - START")

num_worker_threads=10

q = Queue.Queue()
mturk_conn=mturk.conn()
conn_pool=PersistentConnectionPool(num_worker_threads, num_worker_threads+5,database=settings["dbname"], user=settings["user"], host=settings["host"])

target_language = settings["target_language"]
logging.info("target language: %s" % (target_language))

conn = psycopg2.connect("dbname='"+settings["dbname"]+"' user='"+settings["user"]+"' host='"+settings["host"]+"'")

#create workers pool
for i in range(num_worker_threads):
	t = threading.Thread(target=worker)
	t.daemon = True
	t.start()


# Loop over HITs and create a job to get assignments 
cur=conn.cursor()
sql="SELECT mturk_hit_id, h.id, typename, ht.name from hits h, hittypes ht where h.hittype_id=ht.id;" # and assignments>(rejected+approved)
if args.coverage=='OPENONLY':
	sql="SELECT mturk_hit_id, h.id, typename, ht.name from hits h, hittypes ht where h.hittype_id=ht.id and status!='Closed';"
	
cur.execute(sql)
rows = cur.fetchall()

for row in rows:
	mturk_hit_id=str(row[0])
	hit_id=str(row[1])
	typename=str(row[2])
	fulltypename=str(row[3])
	
	logging.debug("mturk hit id: "+mturk_hit_id+", fulltypename: "+fulltypename+" *")

	if typename=="synonyms" and args.hittype!='VOCABULARY':
		item={"hit_id":hit_id, "mturk_hit_id":mturk_hit_id, "typename":typename, "fulltypename":fulltypename}
		q.put(item)

	if typename=="vocabulary" and args.hittype!='SYNONYMS':
		item={"hit_id":hit_id, "mturk_hit_id":mturk_hit_id, "typename":typename, "fulltypename":fulltypename}
		q.put(item)

conn.close()

q.join()       # block until all tasks are done

logging.info("get assignments from MTurk - FINISH")











