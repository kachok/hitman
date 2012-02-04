# -*- coding: utf-8 -*-


import mturk
from settings import settings

import boto.mturk.connection

import psycopg2

# basic logging setup for console output
import logging
logging.basicConfig(
	format='%(asctime)s %(levelname)s %(message)s', 
	datefmt='%m/%d/%Y %I:%M:%S %p',
	level=logging.INFO)


def grade_voc(conn, assignment_id, worker_id):
	#grade assignment's results
	print "grading voc assignment ", assignment_id
	
	cur = conn.cursor()

	#grade controls first
	sql="SELECT vhr.*, d.translation, d.language_id FROM voc_hits_results vhr, dictionary d WHERE vhr.word_id=d.id and assignment_id=%s and is_control=0;"
	
	lang_id=0
	
	cur.execute(sql, (assignment_id,))
	rows=cur.fetchall()
	overall_quality=0 #sum of quality of controls
	total_controls=0 #number of controls
	#grading controls automatically
	for row in rows:
		result_id=str(row[0])
		translation=str(row[3]) #this one comes from MTurk results
		synonym=str(row[7]) #this one comes from dictionary
		
		lang_id=str(row[8]) #getting language_id for assignment

		print result_id, translation, synonym

		#two words are equal
		if translation==synonym:
			data_quality=1
		
			sql2="UPDATE voc_hits_results SET quality=%s WHERE id=%s;"
			cur.execute(sql2, (data_quality,result_id,))
			conn.commit()
			print "updated voc_hits_results with quality (words are identical)", result_id, data_quality

		#looking if pair was graded and have results from Step 2
		sql2="SELECT * from syn_hits_data WHERE translation=%s and synonym=%s and output is not NULL;"
		cur.execute(sql2, (translation, synonym,))
		rows=cur.fetchall()
		
		for row in rows:
			output=str(row[8])
			data_quality=str(row[9])
			
			if output=="yes":
				sql2="UPDATE voc_hits_results SET quality=%s WHERE id=%s;"
				cur.execute(sql2, (1,result_id,))
				conn.commit()
				print "updated voc_hits_results with quality 1 (synonyms)", result_id, data_quality
			elif output=="no":
				sql2="UPDATE voc_hits_results SET quality=%s WHERE id=%s;"
				cur.execute(sql2, (0,result_id,))
				conn.commit()
				print "updated voc_hits_results with quality 0 (not synonyms)", result_id, data_quality
			
		conn.commit()

	conn.commit()



	# --- finished grading all completed controls for this assignment

	print "checking if all controls for this assignment are graded ", assignment_id
	sql="select avg(quality), count(quality) from assignments a, voc_hits_results vhr where a.id=vhr.assignment_id and is_control=0 and assignment_id=%s"
	cur.execute(sql, (assignment_id,))
	rows=cur.fetchall()
	avg_quality=0
	count=0
	for row in rows:
		avg_quality=str(row[0])
		count=int(row[1])

	print count, avg_quality

	#if all controls are graded update assignmetn as reviewed
	if count==2:
		sql="UPDATE assignments SET status='Reviewed', data_status=%s WHERE id=%s"
		cur.execute(sql, (avg_quality, assignment_id))

		sql="UPDATE voc_hits_results SET quality=%s WHERE assignment_id=%s and is_control=1"
		cur.execute(sql, (avg_quality, assignment_id))
		print "updating assignments status and quality, and all non-control results"
	

	conn.commit()


	#calculating mturk_status (approved/rejected) based on worker performance, etc
	sql="SELECT * from voc_workers_performance WHERE worker_id=%s and language_id=%s;"
	
	cur.execute(sql, (worker_id,lang_id))
	rows=cur.fetchall()

	print "looking at worker performance for language ", lang_id

	worker_quality="1"
	worker_total="0"	
	for row in rows:
		worker_quality=str(row[1])
		worker_total=str(row[2])	
		
	if worker_quality=="None":
		worker_quality="1"


	#calculating data_quality of results based on controls from the same assignment
	data_quality=avg_quality

	print "data_quality ", data_quality, " worker_quality/total ",worker_quality, worker_total
	
	sql="SELECT * FROM voc_hits_results WHERE assignment_id=%s and is_control=0;"
	cur.execute(sql, (assignment_id,))
	rows=cur.fetchall()
	
	#grading non-controls results based on controls quality and worker past performance
	for row in rows:
		result_id=str(row[0])
		print "result_id ", result_id
		

		if worker_total<settings["mturk_autoapproval_treshold"]:
			mturk_status="approved"
		else:
			if worker_quality>0.75:
				mturk_status="approved"
			elif worker_quality<0.5:
				mturk_status="rejected"
				data_quality=0 #discard calculated data quality
			else:
				if data_quality>=0.5 and data_quality<=0.75:
					mturk_status="approved"
				else:
					mturk_status="rejected"
		
		

		#update result with data quality value		
		sql2="UPDATE voc_hits_results SET quality=%s WHERE id=%s;"
		cur.execute(sql2, (data_quality, result_id,))

		#update assignment with mturk status and data quality value		
		sql2="UPDATE assignments SET data_status=%s, mturk_status=%s, status=%s WHERE id=%s;"
		cur.execute(sql2, (data_quality, mturk_status, 'Reviewed', assignment_id,))
		
		print "mark as reviewed"
	conn.commit()
	
	
logging.info("review pipeline- START")




target_language = settings["target_language"]
logging.info("target language: %s" % (target_language))

	
try:
	conn = psycopg2.connect("dbname='"+settings["dbname"]+"' user='"+settings["user"]+"' host='"+settings["host"]+"'")
	logging.info("successfully connected to database")
except:
	logging.error("unable to connect to the database")

cur = conn.cursor()


logging.info("select all under review assignements of voc type")
sql="SELECT * from voc_assignments_underreview;"

cur.execute(sql)
rows=cur.fetchall()

for row in rows:
	assignment_id=str(row[0])
	worker_id=str(row[3])
	
	print "processing assignment_id, worker_id- ", assignment_id, worker_id
	
	print "grading this assignment:"
	grade_voc(conn, assignment_id, worker_id)



# grading of all assignments is done
#lets check all graded/reviewed assignmetns and close them in MTurk
#and propagate results to HITs

logging.info("select all reviewed assignements of voc type")
sql="SELECT * from voc_assignments_reviewed;"

cur.execute(sql)
rows=cur.fetchall()

for row in rows:
	hit_id=str(row[2])
	assignment_id=str(row[0])
	data_quality=str(row[7])
	mturk_status=str(row[8])

	cur2=conn.cursor()
	mturk_hit_id=""
	sql2="SELECT h.* from hits h, assignments a WHERE h.id=a.hit_id and a.id=%s;"
	cur2.execute(sql2, (assignment_id,))
	rows2=cur2.fetchall()
	for row in rows:
		mturk_hit_id=str(row[1])
	
	mturk_assignment_id=str(row[1])
	
	mturk_conn=mturk.conn()

	#updating counters for HIT based on data_quality of assignment	
	if data_quality>0.5:
		sql2="update hits SET approved=approved+1 where id=%s"
		cur2.execute(sql2, (hit_id,))
		print "approvide assignment, update hit ", assignment_id, hit_id
	elif data_quality<=0.5:
		#adding extra mturk assignment
		logging.info("incrementing assignments for HIT %s" % (mturk_hit_id))
		mturk_conn.extend_hit(mturk_hit_id, assignments_increment=1)

		sql2="update hits SET assignments=assignments+1, rejected=rejected+1 where id=%s"
		cur2.execute(sql2, (hit_id,))
		rows2=cur2.fetchall()
		print "rejected assignment, update hit ", assignment_id, hit_id


	#TODO: add calculation of MTurk status HERE!!!



	# approving/rejecting assignment in MTurk
	if mturk_status=="approved":
		logging.info("approving assignment %s" % (mturk_assignment_id))
		try:
			mturk_conn.approve_assignment(mturk_assignment_id, feedback=settings["vocabulary_approve_feedback"])
		except boto.mturk.connection.MTurkRequestError, err:
			pass
			
			
	elif mturk_status=="rejected":
		logging.info("rejecting assignment %s" % (mturk_assignment_id))
		mturk_conn.reject_assignment(mturk_assignment_id, feedback=settings["vocabulary_reject_feedback"])
	
	# update assignment and update related HIT
	sql2="UPDATE assignments SET status='Closed' WHERE id=%s"
	cur2.execute(sql2, (assignment_id,))

	conn.commit()
		
	mturk_conn.close()


logging.info("select all open HITs and check if they have 3 completed assignments - mark as Completed")
sql="UPDATE hits SET status='Completed' WHERE approved=%s and status<>'Closed';"
cur.execute(sql, (settings["max_assignments"],))
conn.commit()


logging.info("select all completed HITs ")
sql="SELECT * from voc_hits_completed;"
cur.execute(sql )


rows=cur.fetchall()

for row in rows:
	hit_id=str(row[0])
	
	print "reviewing HIT ",hit_id
	
	cur2=conn.cursor()
	#select all data inputs (without controls, for this HIT and iterate over them while matching outputs to inputs
	sql2="select * from voc_hits_data where hit_id=%s"
	cur2.execute(sql2, (hit_id,))
	rows2=cur2.fetchall()
	for row2 in rows2:
		input_id=str(row2[2])
		lang_id=str(row2[5])
		print "input_id (aka word_id), hit_id, lang_id ", input_id, hit_id, lang_id
		
		cur3=conn.cursor()
		sql3="select * from voc_hits_results vhr, assignments a,voc_hits_workers_performance w where vhr.assignment_id=a.id and a.hit_id=%s and is_control=1 and word_id=%s and w.id=a.worker_id and w.language_id=%s"
		cur3.execute(sql3, (hit_id, input_id, lang_id))
		rows3=cur3.fetchall()
		
		#build list of translations
		translation=""
		weight=0			

		
		results=[]
		for row3 in rows3:
			#input_id=str(row3[0])
			val=str(row3[3])
			q=float(row3[6])
			results.append({"value":val, "quality":q})

			#calculate highest averages and select best output-input match
			if weight<q:
				weight=q
				translation=val
			
		
		
		print "translation/val ", translation, weight
		#update HITs input with matched output
		sql3="UPDATE voc_hits_data SET output=%s, data_quality=%s WHERE hit_id=%s and word_id=%s"
		cur3.execute(sql3, (translation, weight, hit_id, input_id))
		conn.commit()			

	print "close hit ", hit_id
	sql2="UPDATE hits SET status='Closed' WHERE id=%s"
	cur2.execute(sql2, (hit_id,))
	conn.commit()	
	
	#TODO: do we need to close this HIT in MTurk?		

	conn.commit()

logging.info("review pipeline - FINISH")

