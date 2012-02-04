# -*- coding: utf-8 -*-


import mturk
from settings import settings


import psycopg2


# basic logging setup for console output
import logging
logging.basicConfig(
	format='%(asctime)s %(levelname)s %(message)s', 
	datefmt='%m/%d/%Y %I:%M:%S %p',
	level=logging.INFO)

logging.info("review step 2  pipeline- START")

target_language = settings["target_language"]
logging.info("target language: %s" % (target_language))

	
try:
	conn = psycopg2.connect("dbname='"+settings["dbname"]+"' user='"+settings["user"]+"' host='"+settings["host"]+"'")
	logging.info("successfully connected to database")
except:
	logging.error("unable to connect to the database")

cur = conn.cursor()

#logging.info("passing/failing step 2 assignments")
#sql="SELECT review_synonymsassignments();"

logging.info("grading all syn HITs results")
sql="SELECT grade_syn_hits_results();"

cur.execute(sql)
conn.commit()

logging.info("grading all syn assignments one-by-one")

sql="SELECT * from syn_hits_assignments_pending;"
cur.execute(sql)
rows=cur.fetchall()

for row in rows:
	assignment_id=str(row[0])
	
	#grade assignment
	cur2 = conn.cursor()
	sql2="SELECT grade_syn_assignment(%s)"
	cur2.execute(sql, (assignment_id,))
	rows2=cur2.fetchall()
	conn.commit()

	#get results of grading
	cur2 = conn.cursor()
	sql2="select a.*, h.mturk_hit_id from assignments a, hits h where a.hit_id=h.id and a.id=%s;"
	cur2.execute(sql2, (assignment_id,))
	rows2=cur2.fetchall()
	
	mturk_assignment_id=""
	mturk_status=""
	mturk_hit_id=""
	data_status=""
	hit_id=""
	for row2 in rows2:
		print row2
		mturk_assignment_id=row2[1]
		mturk_status=row2[8]
		mturk_hit_id=row2[9]
		data_status=row2[7]
		hit_id=row2[2]

	mturk_conn=mturk.conn()

	# if low data quality adding another assignment in MTurk and increment counter in database
	if data_status<=0.5:
		logging.info("incrementing assignments for HIT %s" % (mturk_hit_id))
		mturk_conn.extend_hit(mturk_hit_id, assignments_increment=1)
		sql2="update hits SET assignments=assignments+1 where id=%s"
		cur2.execute(sql2, (hit_id,))
		rows2=cur2.fetchall()

	# approving/rejecting assignment in MTurk
	if mturk_status=="approved":
		logging.info("approving assignment %s" % (mturk_assignment_id))
		mturk_conn.approve_assignment(mturk_assignment_id, feedback=settings["synonyms_approve_feedback"])
	elif mturk_status=="rejected":
		logging.info("rejecting assignment %s" % (mturk_assignment_id))
		mturk_conn.reject_assignment(mturk_assignment_id, feedback=settings["synonyms_reject_feedback"])
	
	# update assignment and update related HIT
	sql2="SELECT close_assignment(%s)"
	cur2.execute(sql2, (assignment_id,))
	rows2=cur2.fetchall()

	conn.commit()

conn.close()
	

logging.info("review of step 2 pipeline - FINISH")

