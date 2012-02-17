# -*- coding: utf-8 -*-

import mturk
import boto.mturk.connection
from settings import settings

import psycopg2

import json

import logging
import argparse

import uuid

# command line parameters parsing
# loading proper settings file
# basic logging setup for console output

parser = argparse.ArgumentParser(description='Generate Synonyms HITs in database based on Vocabulary HIT results',epilog="And that's how you'd do it")

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


logging.info("Generate Synonyms HITs in database based on Vocabulary HIT results - START")

target_language = settings["target_language"]
logging.info("target language: %s" % (target_language))

try:
	conn = psycopg2.connect("dbname='"+settings["dbname"]+"' user='"+settings["user"]+"' host='"+settings["host"]+"'")
	logging.info("successfully connected to database")
except:
	logging.error("unable to connect to the database")


from itertools import islice, chain

def batch(iterable, size):
	sourceiter = iter(iterable)
	while True:
		batchiter = islice(sourceiter, size)
		yield chain([batchiter.next()], batchiter)


cur = conn.cursor()


#getting language_id from database
sql="SELECT id from languages where prefix=%s;"
cur.execute(sql, (target_language,))
target_lang_id = cur.fetchone()[0]

print "target language id: ", target_lang_id

#get hittype_id for Synonyms HIT
sql="SELECT * from hittypes where typename=%s;"
cur.execute(sql,("synonyms",))
hittype_id = cur.fetchone()[0]

print "HIT Type ID: ", hittype_id


"""

--all vocabulary control results
select * from voc_hits_results where is_control=0

--all pairs of words to run as synonyms
select vhr.*, d.translation as wikilinks_translation from voc_hits_results vhr, dictionary d where d.id=vhr.word_id and is_control=0

-- all pairs with exact values (case insensitive and with trimmed spaces
select vhr.*, d.translation as wikilinks_translation 
from voc_hits_results vhr, dictionary d 
where d.id=vhr.word_id and is_control=0
and
upper(trim(both ' ' from vhr.translation))=upper(trim(both ' ' from d.translation))

--all pairs that were not run through Synonyms HITs

select * from
(
select vhr.translation, d.translation as wikilinks_translation , d.language_id
from voc_hits_results vhr, dictionary d 
where d.id=vhr.word_id and is_control=0
and
upper(trim(both ' ' from vhr.translation))!=upper(trim(both ' ' from d.translation))
) t where not exists (select * from syn_hits_data shd where shd.translation=t.translation and shd.synonym=t.wikilinks_translation);



"""

sql="""select * from
	(
	select vhr.translation, d.translation as wikilinks_translation , d.language_id
	from voc_hits_results vhr, dictionary d 
	where d.id=vhr.word_id and is_control=0
	and
	upper(trim(both ' ' from vhr.translation))!=upper(trim(both ' ' from d.translation))
	) t where not exists (select * from syn_hits_data shd where shd.translation=t.translation and shd.synonym=t.wikilinks_translation);"""

cur.execute(sql)
rows=cur.fetchall()
for row in rows:
	translation=str(row[0])
	synonym=str(row[1])
	language_id=str(row[2])
	
	#skip empty translations (just in case)
	if translation=='':
		continue
	
	print "processing - ", translation,synonym,language_id
	
	#insert new control pair into syn_hits_data
	is_control=0
	cur2 = conn.cursor()
	sql2="INSERT INTO syn_hits_data (translation, synonym, is_control, language_id) VALUES (%s, %s, %s, %s)"
	cur2.execute(sql2, (translation, synonym, is_control, language_id ))
	conn.commit()

#sql="select vhr.translation, d.translation, assignment_id, word_id from voc_hits_results vhr, dictionary d where reason='' and is_control='0' and d.id=vhr.word_id and language_id=%s"
sql="select translation, synonym, id from syn_hits_data where hit_id is null"
cur.execute(sql)
rows = cur.fetchall()

for batchiter in batch(rows, settings["synonyms_num_unknowns"]):

	guid=str(uuid.uuid4())

	sql="SELECT add_hit(%s, %s, %s, %s, %s, %s, %s);"
	cur2.execute(sql,("", guid, hittype_id, target_lang_id, 0, 0, 0))
	hit_id = cur2.fetchone()[0]

	logging.info("Batch ")
	for item in batchiter:
		#word_id=item[3]
		translation=item[0]
		synonym=item[1]
		data_id=item[2]
		#assignment_id=item[2] #this assignment id traced to vocabulary HITs assignments table primary key (so we can traverse back from QA)
		
		
		#sql="INSERT INTO syn_hits_data (hit_id, word_id, synonym, translation, voc_assignment_id, is_control) VALUES (%s, %s, %s, %s, %s, %s);"
		sql="UPDATE syn_hits_data SET hit_id=%s where id=%s;"
		cur2.execute(sql,(hit_id, data_id))
		#tied data to specific HIT


conn.commit()

	

conn.close()
	

logging.info("synonyms hit creation pipeline - FINISH")
