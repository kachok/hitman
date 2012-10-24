"""
Script for removing all hits from mturk (expiring them early)
"""

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

#getting hittype_id from database
#sql="SELECT mturk_hit_id from hits;"
sql="SELECT mturk_hit_id from esl_hits;"
cur.execute(sql, )
print(cur.rowcount)
rows = cur.fetchall()

#rows = ["29DGULF395SW6AFA8XUN1NJB4R3QC7"]

conn=mturk.conn()

for row in rows:
	hitid= str(row[0])#row
	print hitid
	try:
		conn.expire_hit(hitid)
	except:
		pass	

conn.close()
	

logging.info("esl HITs creation in MTurk - FINISH")


