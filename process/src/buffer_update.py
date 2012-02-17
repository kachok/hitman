# -*- coding: utf-8 -*-
from settings import settings
import psycopg2

import json

import logging
import argparse

import datetime


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

conn = psycopg2.connect("dbname='"+settings["dbname"]+"' user='"+settings["user"]+"' host='"+settings["host"]+"'")

cur=conn.cursor()
sql="SELECT * from  buffer_assignments;"
cur.execute(sql)
rows=cur.fetchall()

total=0

for row in rows:
	cp1=datetime.datetime.now()
	total=total+1
	if total % 100==0:
		print "processed %s records from buffer" % (total)
		
	mturk_assignment_id=str(row[1])
	hit_id=str(row[2])
	mturk_worker_id=str(row[3])
	
	accept_time=str(row[4])
	submit_time=str(row[5])
	results_json=str(row[6])
	mturk_status=str(row[7])
		
	#print results_json
	results=json.loads(results_json)


	#print "assignment ", mturk_assignment_id, " mturk_status ", mturk_status

	cp2=datetime.datetime.now()
		
	cur2=conn.cursor()
	sql2="SELECT add_worker(%s, %s);"
	cur2.execute(sql2,(mturk_worker_id, "unknown"))
	db_worker_id = cur2.fetchone()[0]
	conn.commit()

	cp3=datetime.datetime.now()

	#print "hit_id: ",hit_id

	sql2="SELECT add_assignment(%s, %s, %s, %s, %s, %s, %s);"
	cur2.execute(sql2,(mturk_assignment_id, hit_id, mturk_worker_id, accept_time, submit_time, results_json, mturk_status))
	assignment_id = cur2.fetchone()[0]	
	conn.commit()

	cp4=datetime.datetime.now()

	#print "assignment_id: ",assignment_id
	sql2="SELECT typename from assignments a, hits h, hittypes ht where a.hit_id=h.id and h.hittype_id=ht.id and a.id=%s;"
	cur2.execute(sql2,(assignment_id, ))
	typename = cur2.fetchone()[0]	

	#print "typename: ",typename
	
	if typename=="vocabulary":
		#for i in range(settings["num_knowns"]+settings["num_unknowns"]):
		for key in results.keys():
			if key.find("word")==0:
				wordnum=key
				num=wordnum[4:5]
				word_id=wordnum[6:15]
				is_control=wordnum[15:16]=="0"
				translation=results[key]
				reason=results["reason"+num]

				sql2="SELECT add_voc_hits_result(%s, %s, %s, %s, %s);"
				cur2.execute(sql2,(assignment_id, int(word_id), translation, reason, int(is_control)))
				result_id = cur2.fetchone()[0]
				conn.commit()					
	
	if typename=="synonyms":
	
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

				#print assignment_id, int(pair_id), are_synonyms, misspelled, is_control

				sql2="SELECT add_syn_hits_result(%s, %s, %s, %s, %s);"
				cur2.execute(sql2,(assignment_id, int(pair_id), are_synonyms, misspelled, is_control))
				result_id = cur2.fetchone()[0]
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

	sql2="SELECT add_location(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
	cur2.execute(sql2,(assignment_id, db_worker_id, ip, city, region, country, zipcode, lat, lng, timestamp))

	#sql="SELECT add_foreignenglishspeakingsurvey(%s, %s, %s, %s, %s);"
	#cur.execute(sql,(db_worker_id, timestamp, native_speaker, years_speaking_foreign, native_english_speaker, years_speaking_english, country, born_country, language, language_id))

	conn.commit()
	cp6=datetime.datetime.now()
	
	print cp6-cp1, " start to finish"
	print cp3-cp2, " add assignment"
	print cp4-cp3, " add assignment"
	print cp5-cp4, " add results"
	print cp6-cp5, " add location"
	print "---"

conn.commit()



logging.info("FINISH")











