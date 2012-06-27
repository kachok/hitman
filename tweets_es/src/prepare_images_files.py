# -*- coding: utf-8 -*-

from settings import settings

import wikilanguages


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

logging.info("image files creation - START")

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


# iterate over each language individually
for i, lang in enumerate(langs):
	
	logging.info("processing language: %s (#%s out of %s) " %(lang,i+1,len(langs)))
	
	#get all words from vocabulary
	try:
		conn = psycopg2.connect("dbname='"+settings["dbname"]+"' user='"+settings["user"]+"' host='"+settings["host"]+"'")
		logging.info("successfully connected to database")
	except:
		logging.error("unable to connect to the database")
	
	cur = conn.cursor()


	sentence_file = codecs.open(settings["run_name"]+"_sentences.txt", 'a', 'utf-8')	
	segments_file = open(settings["run_name"]+"_segments.txt", 'a')

	sql="SELECT id from languages where prefix=%s;"
	cur.execute(sql, (lang,))
	rows = cur.fetchall()

	lang_id=0
	for row in rows:
		lang_id=row[0]

	sql="SELECT id, tweetid, tweet from tweets WHERE language_id=%s;"
	cur.execute(sql, (lang_id,))
	rows = cur.fetchall()

	for row in rows:
		tweet_id=row[0]
		tweetid=row[1].decode('UTF-8')
		tweet=row[2].decode('UTF-8')

		
		#print row[0], row[1], row[2]
		word_id=str(tweet_id).zfill(9)+'0'
		segments_file.write( word_id +"-"+ langs_properties[lang]["script"]["direction"]+"-"+lang+"-word")
		segments_file.write("\n")
		
		sentence_file.write(tweet)
		sentence_file.write("\n")



	sql="SELECT id, tweetid, tweet  from translations WHERE language_id=%s;"
	cur.execute(sql, (lang_id,))
	rows = cur.fetchall()

	for row in rows:
		tweet_id=row[0]
		tweetid=row[1].decode('UTF-8')
		tweet=row[2].decode('UTF-8')

		
		#print row[0], row[1], row[2]
		word_id=str(tweet_id).zfill(9)+'1'
		segments_file.write( word_id +"-"+ langs_properties[lang]["script"]["direction"]+"-"+lang+"-word")
		segments_file.write("\n")
		
		sentence_file.write(tweet)
		sentence_file.write("\n")
		
	sentence_file.close()
	segments_file.close()
	conn.close()
	

logging.info("image files creation - FINISH")
