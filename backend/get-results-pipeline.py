# -*- coding: utf-8 -*-


import mturk
from settings import settings

from scripts import languages

import pickle
import json

import psycopg2



# basic logging setup for console output
import logging
logging.basicConfig(
	format='%(asctime)s %(levelname)s %(message)s', 
	datefmt='%m/%d/%Y %I:%M:%S %p',
	level=logging.INFO)

logging.info("getting vocabulary HITs result pipeline - START")

# generate list of languages to process
#TODO: for now just load this list from data/languages/languages.txt (list of wikipedia languages with 10,000+ articles)

langs={} #list of languages represented as wikipedia prefixes e.g. xx - xx.wikipedia.org
print type(languages)
print type(languages.getlist)
langs=languages.getlist(settings["languages_file"])

logging.info("list of languages is loaded")
logging.info("# of languages: %s" %(len(langs)))
if len(langs)<=5:
	logging.info("languages are: %s" %(langs))


# iterate over each language individually
for i, lang in enumerate(langs):
	
	logging.info("processing language: %s (#%s out of %s) " %(lang,i+1,len(langs)))
	
	# step #1 unpickle vocabulary
	
	f=open(settings["input_folder"]+lang+"_vocabulary.pickle","r")
	voc=pickle.load(f)
	f.close()
	
	logging.info("loaded %s words from language: %s vocabulary" %(len(voc),lang))
	
	try:
		conn = psycopg2.connect("dbname='postgres' user='dkachaev' host='localhost'")
		logging.info("successfully connected to database")
	except:
		logging.error("unable to connect to the database")
	
	cur = conn.cursor()

	
	for word in voc:
		#print word, voc[word]
		#print type(word)
		if len(word)>0:
			sql="INSERT INTO vocabulary (word, sentences, language_id) VALUES (%s, %s,1);"
			cur.execute(sql,(word, voc[word][0]))
	
	conn.commit()
	
	logging.info("vocabulary table is loaded")
	
	#load language links
	
	
	conn.close()

	"""
	cur.execute("SELECT * from test")
	
	rows = cur.fetchall()
	
	print "\nShow me the databases:\n"
	for row in rows:
	    print "   ", row[0]
	"""	
		
logging.info("getting vocabulary HITs result  pipeline - FINISH")

