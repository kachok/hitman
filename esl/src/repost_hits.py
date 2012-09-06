"""
add assignments to hits to replace rejected assignments
"""

# -*- coding: utf-8 -*-
import sys
import mturk
import boto.mturk.connection as boto
from settings import settings
import wikilanguages
import psycopg2
from itertools import islice, chain
from time import sleep
import uuid

def batch(iterable, size):
	sourceiter = iter(iterable)
	while True:
		batchiter = islice(sourceiter, size)
		yield chain([batchiter.next()], batchiter)

# basic logging setup for console output
import logging
logging.basicConfig(
	format='%(asctime)s %(levelname)s %(message)s', 
	datefmt='%m/%d/%Y %I:%M:%S %p',
	level=logging.INFO)

logging.info("esl HITs creation in MTurk- START")

target_language = settings["target_language"]
logging.info("target language: %s" % (target_language))

langs=[] #list of languages represented as wikipedia prefixes e.g. xx - xx.wikipedia.org
langs=wikilanguages.load(settings["languages_file"])

logging.info("# of languages loaded: %s" %(len(langs)))
if len(langs)<=5:
	logging.info("languages are: %s" %(langs))

langs_properties={} #list of languages' properties (e.g. LTR vs RTL script, non latin characters, etc) 
langs_properties=wikilanguages.langs

try:
	conn = psycopg2.connect("dbname='"+settings["esl_dbname"]+"' user='"+settings["user"]+"' host='"+settings["host"]+"'")
	logging.info("successfully connected to database")
except:
	logging.error("unable to connect to the database")


# iterate over each language individually
for i, lang in enumerate(langs):
	
	logging.info("processing language: %s (#%s out of %s) " %(lang,i+1,len(langs)))

	cur = conn.cursor()

	#getting language_id from database
	sql="SELECT id from languages where prefix=%s;"
	cur.execute(sql, (lang,))
	rows = cur.fetchall()

	lang_id=0
	for row in rows:
		lang_id=str(row[0])


	#getting hittype_id from database
	sql="SELECT id from hittypes where language_id=%s and typename='esl';"
	cur.execute(sql, (lang_id,))
	rows = cur.fetchall()

	hittype_id=0
	for row in rows:
		hittype_id=str(row[0])

	langs_properties[lang]["hittype_id"]=hittype_id

	print hittype_id, lang
	#break


	cur = conn.cursor()
	cur2 = conn.cursor()


	sql="SELECT id from languages where prefix=%s;"
	cur.execute(sql, (lang,))
	rows = cur.fetchall()

	lang_id=0
	for row in rows:
		lang_id=row[0]

	sql = "SELECT h.mturk_hit_id, e.hit_id from esl_rejected_hits e, hits h WHERE e.status='WAITING' AND e.hit_id = h.id;"
	cur.execute(sql)
	reposts = cur.fetchall()
	
	#make copies of rejected hit
	for hit in reposts:
		old_turk_id = hit[0]
		old_id = hit[1]
		try:
			mturk_conn = mturk.conn()
			mturk_conn.extend_hit(old_turk_id, assignments_increment=1)
			logging.info("HIT %s extended by one assignment" % (old_turk_id))
			sql="UPDATE esl_rejected_hits SET status='EXTENDED' WHERE hit_id=%s;"
			cur2.execute(sql,(old_id, ))
		except:
			logging.info("ERROR: HIT %s could not be extended" % (old_id))
		
		conn.commit()
		
conn.close()
	

logging.info("esl HITs extension in MTurk - FINISH")


