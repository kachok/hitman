# -*- coding: utf-8 -*-


import mturk
from settings import settings

from langlib import get_languages_list, get_languages_properties


import psycopg2

from itertools import islice, chain

import codecs

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

logging.info("image creation pipeline - START")

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


# iterate over each language individually
for i, lang in enumerate(langs):
	
	logging.info("processing language: %s (#%s out of %s) " %(lang,i+1,len(langs)))
	
	#get all words from vocabulary
	try:
		conn = psycopg2.connect("dbname='hitman' user='dkachaev' host='localhost'")
		logging.info("successfully connected to database")
	except:
		logging.error("unable to connect to the database")
	
	cur = conn.cursor()


	sentence_file = codecs.open(settings["run_name"]+"sentences.txt", 'a', 'utf-8')	
	segments_file = open(settings["run_name"]+"segments.txt", 'a')

	cur.execute("SELECT * from vocabulary")
	rows = cur.fetchall()

	for row in rows:
		#print row[0], row[1], row[2]
		id=str(row[0]).zfill(9)+'0'
		segments_file.write( id +"-"+ langs_properties[lang]["direction"]+"-"+lang+"-word")
		segments_file.write("\n")
		segments_file.write( id +"_sentences"+"-"+ langs_properties[lang]["direction"]+"-"+lang+"-sentences")
		segments_file.write("\n")
		
		sentence_file.write(row[1].decode('UTF-8'))
		sentence_file.write("\n")
		sentence_file.write(row[2].decode('UTF-8'))
		sentence_file.write("\n")


	cur.execute("SELECT * from dictionary")
	rows = cur.fetchall()

	for row in rows:
		#print row[0], row[1], row[2]
		id=str(row[0]).zfill(9)+'1'
		
		segments_file.write( id +"-"+ langs_properties[lang]["direction"]+"-"+lang+"-word")
		segments_file.write("\n")
		segments_file.write( id +"_sentences"+"-"+ langs_properties[lang]["direction"]+"-"+lang+"-sentences")
		segments_file.write("\n")

		sentence_file.write(row[1].decode('UTF-8'))
		sentence_file.write("\n")
		sentence_file.write(row[2].decode('UTF-8'))
		sentence_file.write("\n")

	sentence_file.close()
	segments_file.close()
	conn.close()
	

logging.info("image creation pipeline - FINISH")

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
