"""
Script for taking results out of buffer_assignments table and reading the data into relevant esl2 tables (requires full buffer_assignments, so needs to be run after multitest.py)
"""

# -*- coding: utf-8 -*-
from settings import settings
import psycopg2
import json
import logging
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
	settings_module = __import__(args.settings) #, globals={}, locals={}, fromlist=[], level=-1
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
sql="SELECT * from buffer_assignments;"
cur.execute(sql)
rows=cur.fetchall()

print len(rows)

total=0

for row in rows:
	cp1=datetime.datetime.now()
	total=total+1
	if total % 100==0:
		print "processed %s records from buffer" % (total)

	mturk_assignment_id=str(row[1])
	hit_id=str(row[2])
	mturk_worker_id=str(row[3])

	#results_json=str(row[4])
	results_json=str(row[6])
	#mturk_status=str(row[5])
	#mturk_status=str(row[5])
	mturk_status=str(row[7])
	
	#accept_time=str(row[6])
	#submit_time=str(row[7])
	accept_time=str(row[4])
	submit_time=str(row[5])
	
	autoapproval_time=str(row[10])
	approval_time=str(row[8])
	rejection_time=str(row[9])
	
	if approval_time=="None": approval_time=None
	if rejection_time=="None": rejection_time=None
		
	results=json.loads(results_json)

	print results

	cp2=datetime.datetime.now()
	
	cur2=conn.cursor()

	cp3=datetime.datetime.now()

	sql2 = "SELECT *  from esl_assignments WHERE mturk_assignment_id=%s;"
	cur2.execute(sql2,(mturk_assignment_id, ))
	if(cur2.rowcount == 0):
		sql2 = "SELECT * from esl_workers WHERE worker_id=%s;"
		print mturk_worker_id
		cur2.execute(sql2,(mturk_worker_id, ))
		row = cur2.fetchone()
		worker_id = row[0] 
                numhits = int(row[2])
		
		sql2 = "INSERT into esl_assignments(mturk_assignment_id,hit_id,worker_id,submit_time,result,mturk_status,accept_time)VALUES(%s,%s,%s,%s,%s,%s,%s) RETURNING id;"
		cur2.execute(sql2,(mturk_assignment_id, hit_id, worker_id, submit_time, results_json, mturk_status, accept_time)) 
		assignment_id = cur2.fetchone()[0]	
                sql2 = "UPDATE esl_workers SET num_hits=%s WHERE id=%s;"
                cur2.execute(sql2, (numhits+1, worker_id))
		
		conn.commit()
		
	else:
		assignment_id = cur2.fetchone()[0]

	cp4=datetime.datetime.now()

	sql2="SELECT typename from assignments a, hits h, hittypes ht where a.hit_id=h.id and h.hittype_id=ht.id and a.id=%s;"
	typename = 'esl' #cur2.fetchone()[0]	

	if typename=="esl":
		for key in results.keys():
			#get each correction in the HIT	
			if key.find("num") > 0:
				#TODO get the sentence for that correction
				#get the span endpoints, old word, new word, edit type, and annotation
				edit_num = results[key]
				snt = int(results["corr."+edit_num+".snt"]) 
				span_start = results["corr."+edit_num+".sst"]
				span_end = results["corr."+edit_num+".snd"]
				old_word = results["corr."+edit_num+".old"]
				new_word = results["corr."+edit_num+".new"]
				edit_type = results["corr."+edit_num+".mod"]
				annotation = results["corr."+edit_num+".atn"]
	
				sql2 = "SELECT *  from esl_edits WHERE assignment_id=%s AND edit_num=%s;"
				cur2.execute(sql2,(assignment_id, edit_num))
				if(cur2.rowcount == 0):
					sql2="SELECT add_esl_hits_result(%s, %s);"
					cur2.execute(sql2,(assignment_id, 000))	
					sql2="SELECT * from esl_hits_data where hit_id=%s and sentence_num=%s"
					cur2.execute(sql2, (hit_id, snt))
					print hit_id, snt
					esl_snt = cur2.fetchone()[6]
					sql2="INSERT into esl_edits(assignment_id,edit_num,esl_sentence_id,span_start,span_end,old_word,new_word,edit_type) VALUES (%s, %s, %s, %s, %s, %s, %s, %s);"
					cur2.execute(sql2,(assignment_id, edit_num, esl_snt, span_start, span_end, old_word, new_word, edit_type))	
		conn.commit()					
	
	cp5=datetime.datetime.now()

	ip=results.get("ip","")
	city=results.get("city","")
	region=results.get("region","")
	country=results.get("country","")
	zipcode=results.get("zipcode","")
	lat=results.get("lat","")
	lng=results.get("lng","")
	timestamp=submit_time

#	native = results['survey_is_native_english_speaker']
	
	
#	sql2 = "INSERT INTO esl_location(assignment_id,worker_id,ip,city,region,country,zipcode,lat,lng,timestamp)VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,);"
#	cur2.execute(sql2,(assignment_id, db_worker_id, ip, city, region, country, zipcode, lat, lng, timestamp))

#	sql2 = "INSERT INTO esl_worker_survey(worker_id, native_speaker, years_eng, curr_country, born_country, education)VALUES(%s,%s,%s,%s,%s,%s);"
#	cur2.execute(sql2, (db_worker_id, native, years, curr_cntry, born, edu))
		
#cur.execute(sql,(db_worker_id, timestamp, native_speaker, years_speaking_foreign, native_english_speaker, years_speaking_english, country, born_country, language, language_id))

	conn.commit()

conn.commit()

# cleanup
sql="delete from buffer_assignments;"
cur.execute(sql)
conn.commit()

logging.info("FINISH")

