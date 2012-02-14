# -*- coding: utf-8 -*-


import workerpool


import mturk
from settings import settings

from langlib import get_languages_list

import threading
import psycopg2

from psycopg2.pool import ThreadedConnectionPool

import json



# basic logging setup for console output
import logging
logging.basicConfig(
	format='%(asctime)s %(levelname)s %(message)s', 
	datefmt='%m/%d/%Y %I:%M:%S %p',
	level=logging.INFO)



class GetAssignmentsJob(workerpool.Job):
	def __init__(self, mturk_hit_id, typename):
		self.mturk_hit_id = mturk_hit_id 
		self.typename = typename
		
	def run(self):
		#TODO: code to get assignments for HIT
				
		mturk_conn=mturk.conn()
		conn=conn_pool.getconn()
		cur=conn.cursor()
		
		assignments=mturk_conn.get_assignments(hit_id=mturk_hit_id)
		
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

			
			lock.acquire()
			sql="SELECT add_worker(%s, %s);"
			cur.execute(sql,(mturk_worker_id, "unknown"))
			db_worker_id = cur.fetchone()[0]
			conn.commit()
			lock.release()

			sql="SELECT add_assignment(%s, %s, %s, %s, %s, %s, %s);"
			cur.execute(sql,(mturk_assignment_id, hit_id, mturk_worker_id, status, submit_time, result, mturk_status))
			
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

						sql="SELECT add_voc_hits_result(%s, %s, %s, %s, %s);"
						cur.execute(sql,(assignment_id, int(word_id), translation, reason, int(is_control)))
						result_id = cur.fetchone()[0]
						conn.commit()					
					
			
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
						print "pair ", pair_id, " are_synonyms ", are_synonyms

						sql="SELECT add_syn_hits_result(%s, %s, %s, %s, %s);"
						cur.execute(sql,(assignment_id, int(pair_id), are_synonyms, misspelled, is_control))
						result_id = cur.fetchone()[0]
						conn.commit()					
				

			ip=results.get("ip","")
			city=results.get("city","")
			region=results.get("region","")
			country=results.get("country","")
			zipcode=results.get("zipcode","")
			lat=results.get("lat","")
			lng=results.get("lng","")
			timestamp=submit_time
			sql="SELECT add_location(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
			cur.execute(sql,(assignment_id, db_worker_id, ip, city, region, country, zipcode, lat, lng, timestamp))

			#sql="SELECT add_foreignenglishspeakingsurvey(%s, %s, %s, %s, %s);"
			#cur.execute(sql,(db_worker_id, timestamp, native_speaker, years_speaking_foreign, native_english_speaker, years_speaking_english, country, born_country, language, language_id))

			conn.commit()
			
			conn_pool.putconn(conn)

			print mturk_worker_id, assignment_id, submit_time
			print "answers ", len(assgnmnt.answers)
			print result
		
	

		




logging.info("get assignments (multithreaded) from MTurk - START")

target_language = settings["target_language"]
logging.info("target language: %s" % (target_language))


lock = threading.RLock()

conn_pool=ThreadedConnectionPool(10, 20,database=settings["dbname"], user=settings["user"], host=settings["host"])

# Initialize a pool, 5 threads in this case
pool = workerpool.WorkerPool(size=10)


try:
	conn = psycopg2.connect("dbname='"+settings["dbname"]+"' user='"+settings["user"]+"' host='"+settings["host"]+"'")
	logging.info("successfully connected to database")
except:
	logging.error("unable to connect to the database")



# Loop over HITs and create a job to get assignments 
cur=conn.cursor()
sql="SELECT mturk_hit_id, h.id, typename from hits h, hittypes ht where h.hittype_id=ht.id;" # and assignments>(rejected+approved)
cur.execute(sql)
rows = cur.fetchall()

for row in rows:
	mturk_hit_id=str(row[0])
	hit_id=str(row[1])
	typename=str(row[2])

	job = GetAssignmentsJob(mturk_hit_id, typename)
	pool.put(job)

conn.close()

# Send shutdown jobs to all threads, and wait until all the jobs have been completed
pool.shutdown()
pool.wait()



logging.info("get assignments from MTurk - FINISH")

