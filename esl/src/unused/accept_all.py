"""Not Used"""

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

	cp2=datetime.datetime.now()
	
	cur2=conn.cursor()

	cp3=datetime.datetime.now()

	sql2="SELECT add_assignment(%s, %s, %s, %s, %s, %s, %s);" #, %s, %s, %s);"

	cur2.execute(sql2,(mturk_assignment_id, hit_id, mturk_worker_id, accept_time, submit_time, results_json, mturk_status)); 
	assignment_id = cur2.fetchone()[0]	
	conn.commit()
	

	cp4=datetime.datetime.now()

	sql2="SELECT typename from assignments a, hits h, hittypes ht where a.hit_id=h.id and h.hittype_id=ht.id and a.id=%s;"
#	cur2.execute(sql2,(assignment_id, ))
	typename = 'esl' #cur2.fetchone()[0]	

#  id | assignment_id | edit_num | esl_sentence_id | span_start | span_end | old_word | new_word | edit_type | annotation
	if typename=="esl":
		#for i in range(settings["num_knowns"]+settings["num_unknowns"]):
		for key in results.keys():
			#get each correction in the HIT	
			if key.find("num") > 0:
				#TODO get the sentence for that correction
				#get the span endpoints, old word, new word, edit type, and annotation
				edit_num = results[key]
				snt = int(results["corr."+edit_num+".snt"]) + 1
				span_start = results["corr."+edit_num+".sst"]
				span_end = results["corr."+edit_num+".snd"]
				old_word = results["corr."+edit_num+".old"]
				new_word = results["corr."+edit_num+".new"]
				edit_type = results["corr."+edit_num+".mod"]
				annotation = results["corr."+edit_num+".atn"]

				#print "sst %s snd %s old %s new %s mod %s atn %s" % (span_start, span_end, old_word, new_word, edit_type, annotation)
				sql2="SELECT add_esl_hits_result(%s, %s);"
				cur2.execute(sql2,(assignment_id, 000))	
				sql2="SELECT * from esl_hits_data where hit_id=%s and sentence_num=%s"
				cur2.execute(sql2, (hit_id, snt))
				esl_snt = cur2.fetchone()[6]
				sql2="SELECT add_esl_edit(%s, %s, %s, %s, %s, %s, %s, %s, %s);"
				cur2.execute(sql2,(assignment_id, edit_num, esl_snt, span_start, span_end, old_word, new_word, edit_type, annotation))	
				#result_id = cur2.fetchone()[0]
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
	
	qc.grade_controls(hit_id, assignment_id, mturk_worker_id)
	qc.appall(assignment_id, mturk_worker_id)

	##--- TODO ADD BACK IN BEFORE UPLOADING TO NON-SANDBOX SITE --


	#sql2="SELECT add_esl_location(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
	#cur2.execute(sql2,(assignment_id, db_worker_id, ip, city, region, country, zipcode, lat, lng, timestamp))

	#sql="SELECT add_foreignenglishspeakingsurvey(%s, %s, %s, %s, %s);"
	#cur.execute(sql,(db_worker_id, timestamp, native_speaker, years_speaking_foreign, native_english_speaker, years_speaking_english, country, born_country, language, language_id))

	conn.commit()
	cp6=datetime.datetime.now()
	
	#disabled performance stats
	#print cp6-cp1, " start to finish"
	#print cp3-cp2, " add assignment"
	#print cp4-cp3, " add assignment"
	#print cp5-cp4, " add results"
	#print cp6-cp5, " add location"
	#print "---"

conn.commit()

# cleanup
sql="delete from buffer_assignments;"
cur.execute(sql)
conn.commit()

logging.info("FINISH")











