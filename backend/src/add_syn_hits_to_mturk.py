# -*- coding: utf-8 -*-


import mturk
from settings import settings


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

logging.info("synonyms hit creation pipeline in MTurk- START")

target_language = settings["target_language"]
logging.info("target language: %s" % (target_language))

# generate list of languages to process
#TODO: for now just load this list from data/languages/languages.txt (list of wikipedia languages with 10,000+ articles)


logging.info("generating HITTypes for each language")

lang="en"
# step #1 register HIT type for current language

operation="RegisterHITType"

parameters2=settings["synonymsHITtype"]


output=mturk.call_turk(operation, parameters2)
logging.debug("RegisterHITType response: %s" % (output))
hittype_id= mturk.get_val(output, "HITTypeId")
logging.info("HIT type for language: %s created with id: %s" % (lang, hittype_id))


try:
	conn = psycopg2.connect("dbname='"+settings["dbname"]+"' user='"+settings["user"]+"' host='"+settings["host"]+"'")
	logging.info("successfully connected to database")
except:
	logging.error("unable to connect to the database")


cur = conn.cursor()

#getting language_id from database
sql="SELECT id from languages where prefix=%s;"
cur.execute(sql, (lang,))
rows = cur.fetchall()

lang_id=0
for row in rows:
	lang_id=str(row[0])



#getting hittype_id from database
sql="SELECT id, mturk_hittype_id from hittypes where language_id=%s and typename='synonyms';"
cur.execute(sql, (lang_id,))
rows = cur.fetchall()

hittype_id=0
mturk_hittype_id=""

for row in rows:
	hittype_id=str(row[0])
	mturk_hittype_id=str(row[1])


	hittype_id= mturk_hittype_id
	print hittype_id, lang
	#break

cur = conn.cursor()
cur2 = conn.cursor()



sql="SELECT * from syn_hits WHERE language_id=%s and mturk_hit_id = '';"
cur.execute(sql, (lang_id,))
rows = cur.fetchall()

web_endpoint='http://'+settings["web_enpoint_domain"]+settings["web_endpoint_synonyms_hit_path"]

for row in rows:

	timeout=5
	passed=False
	
	while not passed:
		#fetching unique UUID for hit to be created in MTurk
		guid=row[2]
		operation="CreateHIT"
		parameters2={
			"HITTypeId":hittype_id,
			'Question':'<ExternalQuestion xmlns="http://mechanicalturk.amazonaws.com/AWSMechanicalTurkDataSchemas/2006-07-14/ExternalQuestion.xsd"><ExternalURL>'+web_endpoint+'</ExternalURL><FrameHeight>800</FrameHeight></ExternalQuestion>',
			"Title":"Mark pairs of words as synonyms or not in English",
			'LifetimeInSeconds':settings["lifetimeinseconds"],
			"MaxAssignments":settings["max_assignments"],
			"UniqueRequestToken":guid,
		}
		output= mturk.call_turk(operation, parameters2)
		try:
			mturk_hit_id=mturk.get_val(output, "HITId")
			passed=True
		except:
			passed=False
			timeout=timeout*2
			print "Sleep for %s seconds " % (timeout)
			sleep(timeout)

		logging.info("new HIT created with id: %s" % (mturk_hit_id))
	
	
		sql="UPDATE hits SET mturk_hit_id=%s, assignments="+str(settings["max_assignments"])+" WHERE uuid=%s;"
		cur2.execute(sql,(mturk_hit_id, guid))
		conn.commit()
	

conn.close()
	

logging.info("synonyms hit creation pipeline - FINISH")
