# -*- coding: utf-8 -*-

import workerpool

import mturk
from settings import settings

import threading
import psycopg2

from psycopg2.pool import PersistentConnectionPool

import json

import logging
import argparse

# command line parameters parsing
# loading proper settings file
# basic logging setup for console output

parser = argparse.ArgumentParser(description='Build vocabularies and dictionaries for multiple languages based on Wikipedia',epilog="And that's how you'd do it")

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


class GetAssignmentsJob(workerpool.Job):
	def __init__(self, hit_id, mturk_hit_id, typename, fulltypename):
		self.hit_id = hit_id 
		self.mturk_hit_id = mturk_hit_id 
		self.typename = typename
		self.fulltypename = fulltypename
		
	def run(self):
		#TODO: code to get assignments for HIT
				
		mturk_conn=mturk.conn()
		conn = psycopg2.connect("dbname='"+settings["dbname"]+"' user='"+settings["user"]+"' host='"+settings["host"]+"'")
		#conn=conn_pool.getconn()
		
		logging.info("mturk hit id: "+self.mturk_hit_id+", fulltypename: "+self.fulltypename)

		assignments=mturk_conn.get_assignments(hit_id=self.mturk_hit_id)
		
		for assgnmnt in assignments:
			mturk_worker_id=assgnmnt.WorkerId
			mturk_assignment_id=assgnmnt.AssignmentId
			submit_time=assgnmnt.SubmitTime
			status=assgnmnt.AssignmentStatus
			results={}
			for i in assgnmnt.answers[0]:
				results[i.fields[0][0]]=i.fields[0][1]
				
			result=json.dumps(results)

			mturk_status=""

			print "assignment ", mturk_assignment_id, " status ", status
			
			lock.acquire()
			cur=conn.cursor()
			sql="SELECT add_worker(%s, %s);"
			cur.execute(sql,(mturk_worker_id, "unknown"))
			db_worker_id = cur.fetchone()[0]
			#conn.commit()
			#lock.release()

			sql="SELECT add_assignment(%s, %s, %s, %s, %s, %s, %s);"
			cur.execute(sql,(mturk_assignment_id, self.hit_id, mturk_worker_id, status, submit_time, result, mturk_status))
			
			conn.commit()
			lock.release()
			assignment_id = cur.fetchone()[0]	
			
			if self.typename=="vocabulary":
				#for i in range(settings["num_knowns"]+settings["num_unknowns"]):
				for key in results.keys():
					if key.find("word")==0:
						wordnum=key
						num=wordnum[4:5]
						word_id=wordnum[6:15]
						is_control=wordnum[15:16]=="0"
						translation=results[key]
						reason=results["reason"+num]

						lock.acquire()
						cur=conn.cursor()

						sql="SELECT add_voc_hits_result(%s, %s, %s, %s, %s);"
						cur.execute(sql,(assignment_id, int(word_id), translation, reason, int(is_control)))
						result_id = cur.fetchone()[0]
						conn.commit()					
						lock.release()
			
			if self.typename=="synonyms":
			
				#for i in range(settings["num_knowns"]+settings["num_unknowns"]):
				for key in results.keys():
					if key.find("pair")==0:
						pairnum=key
						pair_id=pairnum[5:14]
						pair_id_with_control=pairnum[5:15]
						is_control=pairnum[14:15]
						are_synonyms=results[key]
						misspelled=""
						try:
							misspelled=results["misspelled_"+pair_id_with_control]
						except KeyError:
							pass

						#debug for misspelled issue, fixed now
						#print "pair ",pair_id ," misspelled ", misspelled
						#print "pair ", pair_id, " are_synonyms ", are_synonyms

						lock.acquire()
						cur=conn.cursor()

						sql="SELECT add_syn_hits_result(%s, %s, %s, %s, %s);"
						cur.execute(sql,(assignment_id, int(pair_id), are_synonyms, misspelled, is_control))
						result_id = cur.fetchone()[0]
						conn.commit()
						lock.release()					
				

			ip=results.get("ip","")
			city=results.get("city","")
			region=results.get("region","")
			country=results.get("country","")
			zipcode=results.get("zipcode","")
			lat=results.get("lat","")
			lng=results.get("lng","")
			timestamp=submit_time
			lock.acquire()
			cur=conn.cursor()

			sql="SELECT add_location(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
			cur.execute(sql,(assignment_id, db_worker_id, ip, city, region, country, zipcode, lat, lng, timestamp))

			#sql="SELECT add_foreignenglishspeakingsurvey(%s, %s, %s, %s, %s);"
			#cur.execute(sql,(db_worker_id, timestamp, native_speaker, years_speaking_foreign, native_english_speaker, years_speaking_english, country, born_country, language, language_id))

			conn.commit()
			lock.release()			

			#try:
			#	conn_pool.putconn(conn)
			#except:
			#	print "conn pool error"

			#print mturk_worker_id, assignment_id, submit_time
			#print "answers ", len(assgnmnt.answers)
			#print result
		
		conn.close()

		




logging.info("get assignments (multithreaded) from MTurk - START")

target_language = settings["target_language"]
logging.info("target language: %s" % (target_language))


lock = threading.RLock()

conn_pool=PersistentConnectionPool(10, 20,database=settings["dbname"], user=settings["user"], host=settings["host"])

# Initialize a pool, 5 threads in this case
pool = workerpool.WorkerPool(size=10)


try:
	conn = psycopg2.connect("dbname='"+settings["dbname"]+"' user='"+settings["user"]+"' host='"+settings["host"]+"'")
	logging.info("successfully connected to database")
except:
	logging.error("unable to connect to the database")



# Loop over HITs and create a job to get assignments 
cur=conn.cursor()
sql="SELECT mturk_hit_id, h.id, typename, ht.name from hits h, hittypes ht where h.hittype_id=ht.id;" # and assignments>(rejected+approved)
if args.coverage=='OPENONLY':
	sql="SELECT mturk_hit_id, h.id, typename, ht.name from hits h, hittypes ht where h.hittype_id=ht.id and assignments>(rejected+approved);"
	
cur.execute(sql)
rows = cur.fetchall()

for row in rows:
	mturk_hit_id=str(row[0])
	hit_id=str(row[1])
	typename=str(row[2])
	fulltypename=str(row[3])
	
	logging.debug("mturk hit id: "+mturk_hit_id+", fulltypename: "+fulltypename+" *")

	if typename=="synonyms" and args.hittype!='VOCABULARY':
		job = GetAssignmentsJob(hit_id, mturk_hit_id, typename, fulltypename)
		pool.put(job)
	if typename=="vocabulary" and args.hittype!='SYNONYMS':
		job = GetAssignmentsJob(hit_id, mturk_hit_id, typename, fulltypename)
		pool.put(job)

conn.close()

# Send shutdown jobs to all threads, and wait until all the jobs have been completed
pool.shutdown()
pool.wait()

logging.info("get assignments from MTurk - FINISH")


