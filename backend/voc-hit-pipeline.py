# -*- coding: utf-8 -*-


import mturk
from settings import settings

from langlib import get_languages_list, get_languages_properties

import psycopg2

from itertools import islice, chain

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

logging.info("vocabulary hit creation pipeline - START")

target_language = settings["target_language"]
logging.info("target language: %s" % (target_language))

# generate list of languages to process
#TODO: for now just load this list from data/languages/languages.txt (list of wikipedia languages with 10,000+ articles)

langs=[] #list of languages represented as wikipedia prefixes e.g. xx - xx.wikipedia.org
langs=get_languages_list(settings["languages_file"], target_language)

logging.info("# of languages loaded: %s" %(len(langs)))
if len(langs)<=5:
	logging.info("languages are: %s" %(langs))

langs_properties={} #list of languages' properties (e.g. LTR vs RTL script, non latin characters, etc) 
langs_properties=get_languages_properties(settings["languages_properties_file"], target_language)


logging.info("generating HITTypes for each language")
# iterate over each language individually
for i, lang in enumerate(langs):
	
	logging.info("processing language: %s (#%s out of %s) " %(lang,i+1,len(langs)))
	
	# step #1 register HIT type for current language

	operation="RegisterHITType"
	parameters2=settings["vocabularyHITtype"]
	output=mturk.call_turk(operation, parameters2)
	logging.debug("RegisterHITType response: %s" % (output))
	hittype_id= mturk.get_val(output, "HITTypeId")
	logging.info("HIT type for language: %s created with id: %s" % (lang, hittype_id))


	#get all words from vocabulary
	try:
		conn = psycopg2.connect("dbname='hitman' user='dkachaev' host='localhost'")
		logging.info("successfully connected to database")
	except:
		logging.error("unable to connect to the database")
	
	cur = conn.cursor()
	sql="INSERT INTO hittypes (mturk_hittype_id, name) VALUES (%s, %s);"
	cur.execute(sql,(hittype_id, "Vocabulary HIT for "+langs_properties[lang]["name"]))
	conn.commit()
	langs_properties[lang]["mturk_hittype_id"]=hittype_id


# iterate over each language individually
for i, lang in enumerate(langs):
	
	logging.info("processing language: %s (#%s out of %s) " %(lang,i+1,len(langs)))
	
	hittype_id= langs_properties[lang]["mturk_hittype_id"]


	#get all words from vocabulary
	try:
		conn = psycopg2.connect("dbname='hitman' user='dkachaev' host='localhost'")
		logging.info("successfully connected to database")
	except:
		logging.error("unable to connect to the database")
	
	cur = conn.cursor()
	cur2 = conn.cursor()

	cur.execute("SELECT * from vocabulary order by random()")
	rows = cur.fetchall()

	web_endpoint='http://'+settings["web_enpoint_domain"]+settings["web_endpoint_dictionary_hit_path"]+"/"+lang

	for batchiter in batch(rows, settings["num_unknowns"]):

		guid=str(uuid.uuid4())

		operation="CreateHIT"
		parameters2={
			"HITTypeId":hittype_id,
			'Question':'<ExternalQuestion xmlns="http://mechanicalturk.amazonaws.com/AWSMechanicalTurkDataSchemas/2006-07-14/ExternalQuestion.xsd"><ExternalURL>'+web_endpoint+'</ExternalURL><FrameHeight>800</FrameHeight></ExternalQuestion>',
			"Title":"Translate "+str(settings["num_unknowns"]+settings["num_knowns"])+" words from Foreign language to English",
			'LifetimeInSeconds':settings["lifetimeinseconds"],
			"MaxAssignments":settings["max_assignments"],
			"UniqueRequestToken":guid,
		}
		output= mturk.call_turk(operation, parameters2)
		hit_id=mturk.get_val(output, "HITId")
		logging.info("new HIT created with id: %s" % (hit_id))
		
		sql="INSERT INTO vocabularyhits (mturk_hit_id, mturk_hittype_id, uuid) VALUES (%s, %s, %s);"
		cur2.execute(sql,(hit_id, hittype_id, guid))
		conn.commit()

		print "Batch: ",
		for item in batchiter:
			word_id=item[0]
			
			
			sql="INSERT INTO vocabularyhitsdata (mturk_hit_id, word_id) VALUES (%s, %s);"
			cur2.execute(sql,(hit_id, word_id))
			conn.commit()

	conn.close()
	

logging.info("vocabulary hit creation pipeline - FINISH")

#import uuid
#str(uuid.uuid1())

'''
parameters2 = {
#	'HITId':'2H9YNJ92NJKMBTZA8VLH1W2GWO67CE',
#	'HITId':'2YQMZ9O9Z6KWFNAYOJ8RULFQ3NKB2V',
	'AssignmentDurationInSeconds':'600',
	'Description':'Simple External HIT 4',
	'LifetimeInSeconds':'6000',
	
	'Question':'<ExternalQuestion xmlns="http://mechanicalturk.amazonaws.com/AWSMechanicalTurkDataSchemas/2006-07-14/ExternalQuestion.xsd"><ExternalURL>http://mturk-one.appspot.com/tasks</ExternalURL><FrameHeight>400</FrameHeight></ExternalQuestion>',
	'Reward.1.Amount':'0.01',
	'Reward.1.CurrencyCode':'USD',
	'Title':'Simple HIT 4',
	'MaxAssignments':'15',
    }
'''
