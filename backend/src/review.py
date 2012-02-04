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


def grade_syn(conn, assignment_id, worker_id):
	#grade assignment's results
	
	cur = conn.cursor()

	#grade controls first
	sql="SELECT * FROM syn_hits_results WHERE assignment_id=%s and is_control=1;"
	
	cur.execute(sql, (assignment_id,))
	rows=cur.fetchall()
	overall_quality=0 #sum of quality of controls
	total_controls=0 #number of controls
	#grading controls automatically
	for row in rows:
		result_id=str(row[0])
		are_synonyms=str(row[3])
		#misspelled=str(row[4])

		data_quality=0
		if are_synonyms=='yes':
			data_quality=1
		
		#TODO: adjust quality if misspelled
		#if misspelled='':
		#	quality=quality-0.1
	
		sql2="UPDATE syn_hits_results SET quality=%s WHERE id=%s;"
		cur.execute(sql2, (data_quality,result_id,))
		print "updated syn_hits_results with quality", result_id, data_quality
	
	
		overall_quality=overall_quality+data_quality
		total_controls=total_controls+1
	

	sql="SELECT * from syn_workers_performance WHERE worker_id=%s;"
	
	cur.execute(sql, (worker_id,))
	rows=cur.fetchall()

	print "looking at worker performance"

	worker_quality="1"
	worker_total="0"	
	for row in rows:
		worker_quality=str(row[1])
		worker_total=str(row[2])	
		
	if worker_quality=="None":
		worker_quality="1"


	#calculating data_quality of results based on controls from the same assignment
	data_quality=worker_quality
	if float(worker_total)>0:
		data_quality=float(overall_quality)/float(total_controls)

	print "data_quality ", data_quality, " worker_quality/total ",worker_quality, worker_total
	
	sql="SELECT * FROM syn_hits_results WHERE assignment_id=%s and is_control=0;"
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
		sql2="UPDATE syn_hits_results SET quality=%s WHERE id=%s;"
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


logging.info("select all submitted assignements of syn type")
sql="SELECT * from syn_assignments_submitted;"

cur.execute(sql)
rows=cur.fetchall()

for row in rows:
	assignment_id=str(row[0])
	worker_id=str(row[3])
	
	print "processing assignment_id, worker_id- ", assignment_id, worker_id
	
	#mark assignment as under review
	cur2 = conn.cursor()
	sql2="UPDATE assignments SET status='Under Review' WHERE id=%s;"
	cur2.execute(sql2, (assignment_id,))
	conn.commit()
	print "marked assignment as Under Review"
	
	print "grading this assignment:"
	grade_syn(conn, assignment_id, worker_id)



"""
#TODO: check all graded assignments and mark them as "Reviewed" (it is already done for Syn HITs)
logging.info("select all under review assignements of syn type")
sql="SELECT * from syn_assignments_underreview;"

cur.execute(sql)
rows=cur.fetchall()

for row in rows:
	assignment_id=str(row[0])
	worker_id=str(row[3])
"""

	
logging.info("select all reviewed assignements of syn type")
sql="SELECT * from syn_assignments_reviewed;"

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
	if data_quality>=0.5:
		sql2="update hits SET approved=approved+1 where id=%s"
		cur2.execute(sql2, (hit_id,))
	elif data_quality<0.5:
		#adding extra mturk assignment
		logging.info("incrementing assignments for HIT %s" % (mturk_hit_id))
		mturk_conn.extend_hit(mturk_hit_id, assignments_increment=1)

		sql2="update hits SET assignments=assignments+1, rejected=rejected+1 where id=%s"
		cur2.execute(sql2, (hit_id,))
		rows2=cur2.fetchall()

	# approving/rejecting assignment in MTurk
	if mturk_status=="approved":
		logging.info("approving assignment %s" % (mturk_assignment_id))
		try:
			mturk_conn.approve_assignment(mturk_assignment_id, feedback=settings["synonyms_approve_feedback"])
		except boto.mturk.connection.MTurkRequestError, err:
			pass
			
			
	elif mturk_status=="rejected":
		logging.info("rejecting assignment %s" % (mturk_assignment_id))
		mturk_conn.reject_assignment(mturk_assignment_id, feedback=settings["synonyms_reject_feedback"])
	
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
sql="SELECT * from syn_hits_completed;"
cur.execute(sql )


rows=cur.fetchall()

for row in rows:
	hit_id=str(row[0])
	
	print "reviewing HIT ",hit_id
	
	cur2=conn.cursor()
	#select all data inputs (without controls, for this HIT and iterate over them while matching outputs to inputs
	sql2="select * from syn_hits_data where hit_id=%s and is_control=0" #is_control not needed (no controls in this table at all)
	cur2.execute(sql2, (hit_id,))
	rows2=cur2.fetchall()
	for row2 in rows2:
		input_id=str(row2[0])
		print "input_id ", input_id
		
		cur3=conn.cursor()
		sql3="select * from syn_hits_results shr, assignments a,syn_hits_workers_performance w where shr.assignment_id=a.id and a.hit_id=%s and is_control=0 and pair_id=%s and w.id=a.worker_id"
		cur3.execute(sql3, (hit_id, input_id))
		rows3=cur3.fetchall()
		
		results=[]
		for row3 in rows3:
			#input_id=str(row3[0])
			val=str(row3[3])
			q=str(row3[6])
			results.append({"value":val, "quality":q})
			
		yes=0.0
		yescount=0
		no=0.0
		nocount=0
		
		#calculate weighted averages and select best output-input match
		#calcualte if synonyms or not based on weighted averages
		for el in results:
			if el["value"]=="yes":
				yes=yes+float(el["quality"])
				yescount=yescount+1
			if el["value"]=="no":
				no=no+float(el["quality"])
				nocount=nocount+1
		
		if yescount>0:
			yes=float(yes)/float(yescount)
		if nocount>0:
			no=float(no)/float(nocount)
		
		print "yes/no ", yes,no
		#update HITs input with matched output
		if yes>=no:
			sql3="UPDATE syn_hits_data SET output='yes', data_quality=%s WHERE hit_id=%s and id=%s"
			cur3.execute(sql3, (yes, hit_id, input_id))
			conn.commit()			
		if yes<no:
			sql3="UPDATE syn_hits_data SET output='no', data_quality=%s WHERE hit_id=%s and id=%s"
			cur3.execute(sql3, (no, hit_id, input_id))
			conn.commit()			

	print "close hit ", hit_id
	sql2="UPDATE hits SET status='Closed' WHERE id=%s"
	cur2.execute(sql2, (hit_id,))
	conn.commit()	
	
	#TODO: do we need to close this HIT in MTurk?		

	conn.commit()

logging.info("review pipeline - FINISH")

