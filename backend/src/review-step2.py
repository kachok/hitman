# -*- coding: utf-8 -*-


import mturk
from settings import settings

from langlib import get_languages_list, get_languages_properties

import psycopg2

from itertools import islice, chain

import uuid
import urllib

import json

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

logging.info("review step 2  pipeline- START")

target_language = settings["target_language"]
logging.info("target language: %s" % (target_language))

	
try:
	conn = psycopg2.connect("dbname='hitman' user='dkachaev' host='localhost'")
	logging.info("successfully connected to database")
except:
	logging.error("unable to connect to the database")

cur = conn.cursor()

logging.info("passing/failing step 2 assignments")
sql="SELECT review_synonymsassignments();"
cur.execute(sql)


sql="SELECT * from mturk_update_pending_synonymassignments;"
cur.execute(sql)
rows=cur.fetchall()

for row in rows:
	mturk_assignment_id=str(row[2])
	mturk_hit_id=str(row[1])
	assignment_id=row[0]
	control=str(row[7])

	mturk_conn=mturk.conn()
	
	if control=="passed":
		logging.info("approving assignment %s" % (mturk_assignment_id))
		mturk_conn.approve_assignment(mturk_assignment_id, feedback=settings["synonyms_approve_feedback"])
	elif control=="failed":
		logging.info("rejecting assignment %s" % (mturk_assignment_id))
		mturk_conn.reject_assignment(mturk_assignment_id, feedback=settings["synonyms_reject_feedback"])
		logging.info("incrementing assignments for HIT %s" % (mturk_hit_id))
		mturk_conn.extend_hit(mturk_hit_id, assignments_increment=1)
	
	sql="SELECT update_synonymassignment(%s);"
	cur.execute(sql,(assignment_id,))
	conn.commit()
	conn.close()
	

logging.info("review of step 2 pipeline - FINISH")

