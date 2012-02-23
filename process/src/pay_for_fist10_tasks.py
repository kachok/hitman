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

logging.info("pay for first 10 tasks - START")

target_language = settings["target_language"]
logging.info("target language: %s" % (target_language))

try:
	conn = psycopg2.connect("dbname='"+settings["dbname"]+"' user='"+settings["user"]+"' host='"+settings["host"]+"'")
	logging.info("successfully connected to database")
except:
	logging.error("unable to connect to the database")

cur = conn.cursor()
cur2 = conn.cursor()
cur3 = conn.cursor()
	
# select worker_id total_assignments done worker_id assignments paid
sql="select * from (select worker_id, count(*) from assignments a group by worker_id) as total left join (select worker_id, count(*) from assignments a where a.mturk_status in ('Approved', 'Rejected') group by worker_id) as paid on total.worker_id=paid.worker_id;"
cur.execute(sql)
rows = cur.fetchall()

mturk_conn=mturk.conn()

total_workers_paid=0
total_assignments_paid=0

for row in rows:
	worker_id=str(row[0])
	done=str(row[1])
	paid=str(row[3])

	#print "worker: ", worker_id, " tasks done: ",done, ", tasks paid: ", paid
	
	#if worker was never paid
	if paid=='None':
		paid=0

	#if worker was paid less than 10 times, get his unpaid assignments
	paid=int(paid)
	done=int(done)
	if paid<10 and paid!=done:
		to_pay=min(10, done)-paid
		total_workers_paid=total_workers_paid+1
		print "worker: ", worker_id, " tasks done: ",done, ", tasks paid: ", paid, ", paying for ", to_pay," tasks right now (if available)"

		sql2="select * from assignments where worker_id=%s and mturk_status='Submitted' limit %s;"
		
		cur2.execute(sql2, (worker_id,to_pay,))
		rows2 = cur2.fetchall()
	
		for row2 in rows2:
			assignment_id=str(row2[0])
			mturk_assignment_id=str(row2[1])
			hit_id=str(row2[2])
			total_assignments_paid=total_assignments_paid+1
			
			#TODO: replace feedback with something generic
			try:
				#pass
				mturk_conn.approve_assignment(mturk_assignment_id, feedback=settings["synonyms_approve_feedback"])
			except:
				print "failed to update status in MTurk"
			
			
			sql3="UPDATE assignments SET mturk_status='Approved' WHERE id=%s;"
			cur3.execute(sql3, (assignment_id,))
			conn.commit()

conn.close()
	
print "total workers paid: ",total_workers_paid
print "total assignments paid: ",total_assignments_paid

logging.info("FINISH")
