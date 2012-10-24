from settings import settings
import psycopg2
import json
import logging
import argparse
import datetime
import mturk
import boto.mturk.connection

FREEBIES = 10
GOODSCORE = 0.75
BADSCORE = 0.4

#compare control sentence changes against workers corrections assign a score as % of errors that were fixed
def grade_controls(hit, assignment, worker):
	totalpts = 0
	total = 0
	oracle = getoracle(assignment)
	turker = getturker(assignment)
	for sent in oracle:
		if(sent in turker):
			for oe in oracle[sent]:
				for te in turker[sent]:
					total += 1
				#	print oe['idx'] == te['idx'], correctionpoints(oe, te)
					totalpts += correctionpoints(oe, te)
	updatedb(worker, totalpts, total)

def getoracle(assignment):
	conn = psycopg2.connect("dbname='"+settings["esl_dbname"]+"' user='"+settings["user"]+"' host='"+settings["host"]+"'")
	cur = conn.cursor()
	sql="select * from assignments where id=%s;"
	cur.execute(sql, (assignment, ))
	row = cur.fetchone()
	hitid = str(row[2])
	#get the errors that were added intentionally
	sql = "select * from esl_controls where hit_id=%s;"
	cur.execute(sql, (hitid, ))
	oracle = cur.fetchall()
	oracleidx = {}
	for e in oracle:
		sent =str(e[0])
		idx = e[2]
		mod = e[5]
		word = e[3]
		if(not(sent in oracleidx)):
			oracleidx[sent] = [{'idx' : idx, 'mod' : mod, 'word' : word}]
		else:
			oracleidx[sent].append({'idx' : idx, 'mod' : mod, 'word' : word})
	return oracleidx

def getturker(assignment):
	conn = psycopg2.connect("dbname='"+settings["esl_dbname"]+"' user='"+settings["user"]+"' host='"+settings["host"]+"'")
	cur = conn.cursor()
	#get the errors that were fixed by turker
	sql = "select * from esl_edits where assignment_id=%s;"
	cur.execute(sql, (assignment, ))
	turker = cur.fetchall()
	turkeridx = {}
	for e in turker:
		sent = str(e[3])
		idx = e[4]
		mod = e[8]
		word = e[7]
		if(not(sent in turkeridx)):
			turkeridx[sent] = [{'idx' : idx, 'mod' : mod, 'word' : word}]
		else:
			turkeridx[sent].append({'idx' : idx, 'mod' : mod, 'word' : word})
	return turkeridx


def correctionpoints(mistake, fix):
	points = 0
	inverses = {'insert' : 'delete', 'delete' : 'insert', 'change' : 'change'}
	sameidx = mistake['idx'] == fix['idx']
	sameword = mistake['word'] == fix['word']
	samemode = inverses[mistake['mod']] == fix['mod']	
	if(sameidx and samemode):
		points += 0.5 
		if(sameword):
			points += 0.5
	return points

def updatedb(worker, correct, total):
	conn = psycopg2.connect("dbname='"+settings["esl_dbname"]+"' user='"+settings["user"]+"' host='"+settings["host"]+"'")
	cur = conn.cursor()
	sql = "select * from esl_workers where worker_id=%s;"
	cur.execute(sql, (worker, ))
	result = cur.fetchone()
	numhits = result[2]
	currstatus = result[5]
	currcorrect = result[3]
	currtotal = result[7]
	newcorrect = currcorrect + correct
	newtotal = currtotal + total
	newavg = float(newcorrect)/newtotal
	sql = "UPDATE esl_workers SET num_correct_controls=%s, num_controls=%s, average=%s where worker_id=%s" 	
	cur.execute(sql, (newcorrect, newtotal, newavg, worker))
	if(numhits <= FREEBIES):
		sql = "UPDATE esl_workers SET status='APPROVE',statusdesc='PREAPPROVAL' where worker_id=%s" 	
		cur.execute(sql, (worker, ))
	else:
		if(currstatus == "PENDING" or currstatus == "PREAPPROVAL"):
			if(newavg > GOODSCORE):
				sql = "UPDATE esl_workers SET status='APPROVE',statusdesc='APPROVED' where worker_id=%s" 	
			if(newavg < BADSCORE):
				sql = "UPDATE esl_workers SET status='REJECT',statusdesc='BLOCKED' where worker_id=%s" 	
			if(newavg >= BADSCORE and newavg <= GOODSCORE):
				tempavg = float(correct) / total
				if(tempavg >= 0.4):
					sql = "UPDATE esl_workers SET status='APPROVE',statusdesc='PENDING' where worker_id=%s" 	
				else:
					sql = "UPDATE esl_workers SET status='REJECT',statusdesc='PENDING' where worker_id=%s" 	
			cur.execute(sql, (worker, ))
	
	conn.commit()

def appall(assignment, worker):
	mturk_conn=mturk.conn()
	conn = psycopg2.connect("dbname='"+settings["esl_dbname"]+"' user='"+settings["user"]+"' host='"+settings["host"]+"'")
	cur = conn.cursor()
        sql="select * from assignments where id=%s;"
        cur.execute(sql, (assignment, ))
	row = cur.fetchone()
	mturk_id = row[1]
	paystatus = row[8]
	sql = "select * from esl_workers where worker_id=%s;"
	cur.execute(sql, (worker, ))
	status = cur.fetchone()[4]
	print paystatus
	if(paystatus == "Rejected"):
		if(status == "REJECT"):
                        try:
                                mturk_conn.reject_assignment(mturk_id, feedback=settings["esl_approve_feedback"])
				sql = "update assignments set mturk_status='Approved' where id=%s;"
        			cur.execute(sql, (assignment, ))
                        except boto.mturk.connection.MTurkRequestError, err:
                                print "mturk api error while approving assignment"

def apprej(assignment, worker):
	mturk_conn=mturk.conn()
	conn = psycopg2.connect("dbname='"+settings["esl_dbname"]+"' user='"+settings["user"]+"' host='"+settings["host"]+"'")
	cur = conn.cursor()
        sql="select * from assignments where id=%s;"
        cur.execute(sql, (assignment, ))
	row = cur.fetchone()
	mturk_id = row[1]
	paystatus = row[8]
	sql = "select * from esl_workers where worker_id=%s;"
	cur.execute(sql, (worker, ))
	status = cur.fetchone()[4]
	if(paystatus == "Submitted"):
		print status
		if(status == "APPROVE"):
			print "approving assignment", assignment
                        try:
                                mturk_conn.approve_assignment(mturk_id, feedback=settings["esl_approve_feedback"])
				sql = "update assignments set mturk_status='Approved' where id=%s;"
        			cur.execute(sql, (assignment, ))
                        except boto.mturk.connection.MTurkRequestError, err:
                                print "mturk api error while approving assignment"
		if(status == "REJECT"):
			print "rejecting assignment", assignment
                        try:
                                mturk_conn.reject_assignment(mturk_id, feedback=settings["esl_reject_feedback"])
				sql = "update assignments set mturk_status='Rejected' where id=%s;"
        			cur.execute(sql, (assignment, ))
                        except boto.mturk.connection.MTurkRequestError, err:
                                print "mturk api error while rejecting assignment"
	conn.commit()		







	
