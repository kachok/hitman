from settings import settings
import codecs
import psycopg2
import json
import logging
import argparse
import datetime
import mturk
import boto.mturk.connection
import extract_data
import edit_graph
import datetime

FREEBIES = 5 
GOODSCORE = 0.99 #75
BADSCORE = 0.4


#compare control sentence changes against workers corrections assign a score as % of errors that were fixed
def grade_sent1(assignment):
	ref = getoracle(assignment)
	candidate = getturker(assignment)
        totalpts = 0
        total = 0
        edits = {}
        for sent in ref:
             	for edit in ref[sent]:
			total += 1
                	#edits[edit['idx']] = edit
                	edits[edit.sp_start] = edit
	print edits
	print candidate
        for sent in candidate:
             	for cedit in candidate[sent]:
			#idx = cedit['idx']
			idx = cedit.sp_start
                	if(idx in edits):
                        	totalpts += correctionpoints(edits[idx], cedit)
                        	edits.pop(idx)

        return totalpts, total

#compare control sentence changes against workers corrections assign a score as % of errors that were fixed
def grade_sent(assignment): # log=None):
	log = codecs.open("apprej.log", mode='a', encoding='utf-8', errors='ignore')
        total = errcount(assignment)
	ref = getoracle(assignment)
	candidate = getturker(assignment)
	if(candidate == {}):
		sent = get_raw_sents(assignment)
		s = sent[sent.keys()[0]]
		add_sent_to_db(s, assignment)
		return 0, total
        totalpts = 0
	rawsents = get_raw_sents(assignment)
	#build sentence data structure to track edits
        for sent in rawsents:
		sentence = rawsents[sent]
		log.write(str(datetime.datetime.now().strftime("%Y-%m-%d_%H:%M"))+" "+str(assignment)+" "+sentence.decode('utf-8')+'\n')
		s = edit_graph.initialize_sentence(sentence)
		errors = sorted(candidate[sent], key = lambda e : e.seq_id)
		for e in errors:
			s.revise(e)
		add_sent_to_db(s.plain_str(), assignment)
		#s.print_ultimate()
		for e in ref[sent]:
			pts = correctionpoints(e, s, log=log) 
	#		if(pts == 0 and (e.mode == "insert" or e.mode == "delete")):
	#			ref[sent] = update_indicies(ref[sent], e.sp_start, e.mode)
			totalpts += pts 
	return totalpts, total

def add_sent_to_db(sent, assign):
	conn = psycopg2.connect("dbname='"+settings["esl_dbname"]+"' user='"+settings["user"]+"' host='"+settings["host"]+"'")
	cur = conn.cursor()
	sql = "INSERT INTO esl_corrected_sents (assign_id, sentence) VALUES(%s, %s);"
	cur.execute(sql, (assign, sent.decode('utf-8', errors='replace')))
	conn.commit()

def update_indicies(errs, idx, mode):
	#print errs
	for e in errs:
		if(e.sp_start >= idx):
			if(mode == "insert"):
				e.sp_start += 1
			if(mode == "delete"):
				e.sp_start -= 1
	#print errs
	return errs

#compare control sentence changes against workers corrections assign a score as % of errors that were fixed
def grade_controls(hit, assignment, worker): #, log=None):
	points, total = grade_sent(assignment) #, log)
	ret = bufferupdatedb(worker, points, total)
	return ret

def errcount(assignid):
	conn = psycopg2.connect("dbname='"+settings["esl_dbname"]+"' user='"+settings["user"]+"' host='"+settings["host"]+"'")
	cur = conn.cursor()
	sql="SELECT c.* FROM esl_controls c,esl_sentences s,esl_assignments a,esl_hits_data h WHERE a.id=%s AND a.hit_id=h.hit_id AND s.id=h.esl_sentence_id AND s.qc=1 AND c.esl_sentence_id=s.id::text;"
	cur.execute(sql, (assignid, ))
	return cur.rowcount

def get_raw_sents(assignid):
	sents = {}
	conn = psycopg2.connect("dbname='"+settings["esl_dbname"]+"' user='"+settings["user"]+"' host='"+settings["host"]+"'")
	cur = conn.cursor()
	sql="SELECT s.id,s.sentence FROM esl_sentences s,esl_assignments a,esl_hits_data h WHERE a.id=%s AND a.hit_id=h.hit_id AND s.id=h.esl_sentence_id AND s.qc=1;"
	cur.execute(sql, (assignid, ))
	rows = cur.fetchall()	
	for row in rows:
		sents[str(row[0])] = row[1]
	return sents

def getoracle(assignment):
	conn = psycopg2.connect("dbname='"+settings["esl_dbname"]+"' user='"+settings["user"]+"' host='"+settings["host"]+"'")
	cur = conn.cursor()
	sql="select * from esl_assignments where id=%s;"
	cur.execute(sql, (assignment, ))
	row = cur.fetchone()
	hitid = str(row[2])
	#get the errors that were added intentionally
	sql = "select * from esl_controls where hit_id=%s ORDER BY seq_num;"
	cur.execute(sql, (hitid, ))
	oracle = cur.fetchall()
	oracleidx = {}
	i = 0
	for e in oracle:
		sent =str(e[0])
		start = int(e[2])
		end = int(start) + 1
		old = e[3]
		new = e[4]
		mode = e[5]
		if(not(sent in oracleidx)):
			oracleidx[sent] = [extract_data.Edit(i, start, end, old, new , mode)]
			#[{'idx' : idx, 'mod' : mod, 'word' : word}]
		else:
			oracleidx[sent].append(extract_data.Edit(i, start, end, old, new , mode))
			#oracleidx[sent].append({'idx' : idx, 'mod' : mod, 'word' : word})
		i += 1
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
		start = int(e[4])
		end = int(e[5])
		old = e[6]
		new = e[7]
		mode = e[8]
		i = e[2]	
		if(not(sent in turkeridx)):
			turkeridx[sent] = [extract_data.Edit(i, start, end, old, new , mode)]
			#turkeridx[sent] = [{'idx' : idx, 'mod' : mod, 'word' : word}]
		else:
			turkeridx[sent].append(extract_data.Edit(i, start, end, old, new , mode))
			#turkeridx[sent].append({'idx' : idx, 'mod' : mod, 'word' : word})
		i += 1
	return turkeridx

def correctionpoints(error, s, log=None): 
	finals = s.get_ultimate_fates()
#	print [str(f)+": "+finals[f].text for f in finals]
	if(error.mode == "change"):
		if(log):
			log.write("CHANGED"+" "+str(error)+" ")
		#check if word was eventually changed to original word
		#original word positions map to odds only, since spaces are added between all words in data structure
        	if(finals[(2*error.sp_start)+1].text == error.old_wd):
			if(log):
				log.write("TRUE"+'\n')
			return 1
		else:
			if(log):
				log.write("FALSE "+str(finals[(2*error.sp_start)+1].text)+" "+str(error.old_wd)+" "+str((2*error.sp_start)+1)+'\n')
			return 0
	else:
		if(error.mode == "delete"):
			if(log):
				log.write("DELETED"+" "+str(error)+" ")
			#check if word was eventually deleted
			if((2*error.sp_start + 1) in s.deleted_nodes()):
				if(log):
					log.write("TRUE"+'\n')
				return 1
			else:
				if(log):
					log.write("FALSE "+str((2*error.sp_start)+1)+" "+str(s.deleted_nodes())+'\n')
				return 0
		else:
			if(error.mode == "insert"):
				if(log):
					log.write("INSERTED"+" "+str(error)+" ")
        			if(finals[(2*error.sp_start)].text == error.old_wd):
					if(log):
						log.write("TRUE"+'\n')
					return 1
				else:
					if(log):
						log.write("FALSE "+str(finals[(2*error.sp_start)].text)+" "+str(error.old_wd)+" "+str((2*error.sp_start))+'\n')
					return 0
	if(log):
		log.write("FALSE"+'\n')
	return 0

def correctionpoints2(mistake, fix):
	inverses = {'insert' : 'delete', 'delete' : 'insert', 'change' : 'change'}
        #if(not(mistake['idx'] == fix['idx'])):
        if(not(mistake.sp_start == fix.sp_start)):
                return None
        #if(inverses[mistake['mod'].strip()] == fix['mod']):
        if(inverses[mistake.mode.strip()] == fix.mode.strip()):
		print "APPROVED", mistake, fix
                return 1
	print "REJECTED", mistake, fix
        return 0

def correctionpoints1(mistake, fix):
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

def bufferupdatedb(worker, correct, total):
	conn = psycopg2.connect("dbname='"+settings["esl_dbname"]+"' user='"+settings["user"]+"' host='"+settings["host"]+"'")
	cur = conn.cursor()
	sql = "SELECT * from esl_appr_buffer where worker_id=%s;"
	cur.execute(sql, (worker, ))
	if(cur.rowcount == 0): #copy row from esl_workers into esl_appr_buffer	
		sql = "select * from esl_workers where worker_id=%s;"
		cur.execute(sql, (worker, ))
		result = cur.fetchone()
		worker = result[1]
		numhits = result[2]
		currcorrect = result[3]
		currstatus = result[4]
		currstatusdesc = result[5]
		curravg = result[6]
		currtotal = result[7]	
		currapp = result[8]
		sql = "INSERT INTO esl_appr_buffer(worker_id,num_hits,num_correct_controls,status,statusdesc,average,num_controls,num_approved) VALUES (%s,%s,%s,%s,%s,%s,%s,%s);" 	
		cur.execute(sql, (worker, numhits, currcorrect, currstatus, currstatusdesc, curravg, currtotal, currapp))
	else:	
		sql = "select * from esl_appr_buffer where worker_id=%s;"
		cur.execute(sql, (worker, ))
		result = cur.fetchone()
		worker = result[1]
		numhits = result[2]
		currcorrect = result[3]
		currstatus = result[4]
		currstatusdesc = result[5]
		curravg = result[6]
		currtotal = result[7]	
		currapp = result[8]
	newcorrect = currcorrect + correct
	newtotal = currtotal + total
	newavg = float(newcorrect)/newtotal
	sql = "UPDATE esl_appr_buffer SET num_correct_controls=%s, num_controls=%s, average=%s WHERE  worker_id=%s;"
	cur.execute(sql, (newcorrect, newtotal, newavg, worker))
	if(currapp <= FREEBIES):
		print "Free"
		sql = "UPDATE esl_appr_buffer SET status='APPROVE',statusdesc='PREAPPROVAL', num_approved=%s where worker_id=%s" 	
		cur.execute(sql, (currapp + 1, worker, ))
		ret=1
	else:
		print currstatusdesc
		if(currstatusdesc == "PENDING" or currstatusdesc == "PREAPPROVAL"):
			if(newavg > GOODSCORE):
				sql = "UPDATE esl_appr_buffer SET status='APPROVE',statusdesc='APPROVED', num_approved=%s where worker_id=%s" 	
				cur.execute(sql, (currapp+1, worker, ))
				ret=1
			if(newavg < BADSCORE):
				sql = "UPDATE esl_appr_buffer SET status='REJECT',statusdesc='BLOCKED' where worker_id=%s" 	
				cur.execute(sql, (worker, ))
				ret=1
			if(newavg >= BADSCORE and newavg <= GOODSCORE):
				tempavg = float(correct) / total
				if(tempavg >= 0.4):
					sql = "UPDATE esl_appr_buffer SET status='APPROVE',statusdesc='PENDING',num_approved=%s where worker_id=%s"
					cur.execute(sql, (currapp+1, worker, ))
					ret=1
				else:
					sql = "UPDATE esl_appr_buffer SET status='REJECT',statusdesc='PENDING' where worker_id=%s" 	
					ret=0
		else:
			if(currstatusdesc =="APPROVE"):
				sql = "UPDATE esl_appr_buffer SET num_approved=%s where worker_id=%s"		
    			        cur.execute(sql, (currapp+1, worker, ))
				ret = 1
			else:
				ret = 0	
	conn.commit()
	return ret

def updatedb(worker):
	conn = psycopg2.connect("dbname='"+settings["esl_dbname"]+"' user='"+settings["user"]+"' host='"+settings["host"]+"'")
	cur = conn.cursor()
	sql = "select * from esl_appr_buffer where worker_id=%s;"
	cur.execute(sql, (worker, ))
	if(cur.rowcount > 0):
		result = cur.fetchone()
		worker = result[1]
		numhits = result[2]
		currcorrect = result[3]
		currstatus = result[4]
		currstatusdesc = result[5]
		curravg = result[6]
		currtotal = result[7]	
		currapp = result[8]
		sql = "UPDATE esl_workers SET num_hits=%s, num_correct_controls=%s, status=%s, statusdesc=%s, average=%s, num_controls=%s, num_approved=%s WHERE worker_id=%s;"
		cur.execute(sql, (numhits,currcorrect,currstatus,currstatusdesc,curravg,currtotal,currapp,worker))
		conn.commit()	
		sql = "DELETE FROM esl_appr_buffer WHERE worker_id=%s;"
		cur.execute(sql, (worker,))
		conn.commit()

def updatedb1(worker, correct, total):
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
        sql="select * from esl_assignments where id=%s;"
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
				sql = "update esl_assignments set mturk_status='Approved' where id=%s;"
        			cur.execute(sql, (assignment, ))
                        except boto.mturk.connection.MTurkRequestError, err:
                                print "mturk api error while approving assignment"

def apprej(assignment, worker):
	updatedb(worker)
	mturk_conn=mturk.conn()
	conn = psycopg2.connect("dbname='"+settings["esl_dbname"]+"' user='"+settings["user"]+"' host='"+settings["host"]+"'")
	cur = conn.cursor()
        sql="select * from esl_assignments where id=%s;"
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
                           	approve_feedback=get_feedback(worker, assignment)
                                mturk_conn.approve_assignment(mturk_id, feedback=approve_feedback)
				sql = "update esl_assignments set mturk_status='Approved' where id=%s;"
        			cur.execute(sql, (assignment, ))
                        except boto.mturk.connection.MTurkRequestError, err:
                                print "mturk api error while approving assignment"
		if(status == "REJECT"):
			print "rejecting assignment", assignment
                        try:
                           	reject_feedback=get_feedback(worker, assignment)
				mturk_conn.reject_assignment(mturk_id, feedback=reject_feedback)
				sql = "update esl_assignments set mturk_status='Rejected' where id=%s;"
        			cur.execute(sql, (assignment, ))
				repost_hit(assignment)
                        except boto.mturk.connection.MTurkRequestError, err:
                                print "mturk api error while rejecting assignment"
	conn.commit()		

def repost_hit(assignment):
	conn = psycopg2.connect("dbname='"+settings["esl_dbname"]+"' user='"+settings["user"]+"' host='"+settings["host"]+"'")
	cur = conn.cursor()
	sql = "SELECT hit_id from esl_assignments where id=%s;"
	cur.execute(sql, (assignment, ))
	hit_id = cur.fetchone()[0]
	sql = "INSERT INTO esl_rejected_hits (hit_id, status) VALUES (%s, %s);"
        cur.execute(sql, (hit_id, "WAITING"))
	conn.commit()	

def get_feedback(worker, assignment):
	conn = psycopg2.connect("dbname='"+settings["esl_dbname"]+"' user='"+settings["user"]+"' host='"+settings["host"]+"'")
	cur = conn.cursor()
	sql = "SELECT * from esl_workers WHERE worker_id=%s;"
	cur.execute(sql, (worker, ))
	row = cur.fetchone()
	status = row[4]
	desc = row[5]
	if(status == "REJECT" and desc == "PENDING"):
		return reject_pending_feedback(assignment, worker)
	if(status == "APPROVE" and desc == "PENDING"):
		return approve_feedback()
	if(status == "APPROVE" and desc == "PREAPPROVAL"):
		return preapprove_feedback(assignment, worker)
	if(status == "REJECT" and desc == "BLOCKED"):
		return reject_blocked_feedback(assignment, worker)
	if(status == "APPROVE" and desc == "APPROVED"):
		return approve_feedback()

def reject_pending_feedback(assignment, worker):
	conn = psycopg2.connect("dbname='"+settings["esl_dbname"]+"' user='"+settings["user"]+"' host='"+settings["host"]+"'")
	cur = conn.cursor()
	sql = "SELECT sentence from esl_corrected_sents WHERE assign_id=%s;"
        cur.execute(sql, (str(assignment), ))
	their_sent = cur.fetchone()[0]
	sql = "SELECT s.sentence from esl_sentences s, esl_assignments a, esl_hits_data h WHERE a.id=%s AND h.hit_id = a.hit_id AND h.esl_sentence_id=s.id AND s.qc=1;"
        cur.execute(sql, (str(assignment), ))
	our_sent = cur.fetchone()[0]
	sql = "SELECT c.sentence from esl_controls c, esl_assignments a, esl_hits_data h WHERE a.id=%s AND h.hit_id = a.hit_id AND h.esl_sentence_id::text=c.esl_sentence_id;"
        cur.execute(sql, (str(assignment), ))
	orig_sent = cur.fetchone()[0]
	sql = "SELECT average from esl_workers where worker_id=%s;"
        cur.execute(sql, (str(worker), ))
	avg = int(100*cur.fetchone()[0])
	print avg
	reject_feedback="We are sorry, but your responses did not meet our quality control requirement. Our control sentence was: %s Your correction was: %s We were looking for: %s Currently, your average accuracy on our controls is %s%%. If it falls below 40%% we will stop accepting your hits. Next time, be sure to read all the sentences carefully before submitting. We appreciate your effort." % (our_sent,their_sent,orig_sent,str(avg))
	return reject_feedback

def accept_feedback():
	return "Thank you!!"

def preapprove_feedback(assignment, worker):
	conn = psycopg2.connect("dbname='"+settings["esl_dbname"]+"' user='"+settings["user"]+"' host='"+settings["host"]+"'")
	cur = conn.cursor()
	sql = "SELECT average from esl_workers where worker_id=%s;"
        cur.execute(sql, (str(worker), ))
	avg = int(100*cur.fetchone()[0])
	print avg
	reject_feedback="Thank you! Currently, over the past HITs you have submitted to us, your average accuracy on our controls has been %s%%. We will accept your first 10 HITs for free; after that, we cannot accept HITs from workers with averages below 40%%." % (str(avg))
	return reject_feedback

def reject_blocked_feedback(assignment, worker):
	conn = psycopg2.connect("dbname='"+settings["esl_dbname"]+"' user='"+settings["user"]+"' host='"+settings["host"]+"'")
	cur = conn.cursor()
	sql = "SELECT average from esl_workers where worker_id=%s;"
        cur.execute(sql, (str(worker), ))
	avg = int(100*cur.fetchone()[0])
	print avg
	reject_feedback="We are sorry, but your responses did not meet our quality control requirement. Over the past HITs you have submitted to us, your average accuracy on our controls has been %s%%. We cannot accepted averages below 40%%." % (str(avg))
	return reject_feedback




	
