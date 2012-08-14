# -*- coding: utf-8 -*-


import mturk
from settings import settings

import wikilanguages

import psycopg2

from itertools import islice, chain

from time import sleep

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

# generate list of languages to process
#TODO: for now just load this list from data/languages/languages.txt (list of wikipedia languages with 10,000+ articles)

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


cur=conn.cursor()

"""sql="SELECT * FROM esl_sentences"
cur.execute(sql, )
print(cur.description)
print(cur.rowcount)

sql="DELETE FROM esl_sentences"
cur.execute(sql, )
print(cur.rowcount)

sql="SELECT * FROM esl_sentences"
cur.execute(sql, )
print(cur.description)
print(cur.rowcount)
"""
sql="DELETE FROM esl_sentences"
cur.execute(sql, )
print(cur.rowcount)

sql="DELETE FROM esl_controls"
cur.execute(sql, )
print(cur.rowcount)

sql="DELETE FROM esl_hits_data"
cur.execute(sql, )
print(cur.rowcount)

#sql="DELETE FROM esl_languages"
#cur.execute(sql, )
#print(cur.rowcount)

sql="DELETE FROM hittypes"
cur.execute(sql, )
print(cur.rowcount)

sql="DELETE FROM dictionary"
cur.execute(sql, )
print(cur.rowcount)

#sql="DELETE FROM esl_workers"
#cur.execute(sql, )
#print(cur.rowcount)

sql="DELETE FROM esl_location"
cur.execute(sql, )
print(cur.rowcount)

sql="DELETE FROM esl_assignments"
cur.execute(sql, )
print(cur.rowcount)

sql="DELETE FROM assignments"
cur.execute(sql, )
print(cur.rowcount)

#sql="DELETE FROM esl_edits"
#cur.execute(sql, )
#print(cur.rowcount)

#sql="DELETE FROM esl_hits_results"
#cur.execute(sql, )
#print(cur.rowcount)

conn.commit()
conn.close()

#for row in rows:
#	hitid=str(row[0])
#	print hitid
#	try:
#		conn.expire_hit(hitid)
#	except:
#		pass	

	

logging.info("esl HITs creation in MTurk - FINISH")


