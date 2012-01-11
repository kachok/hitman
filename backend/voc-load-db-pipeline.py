# -*- coding: utf-8 -*-


import mturk
from settings import settings

from langlib import get_languages_list, get_languages_properties


import pickle
import json

import psycopg2



# basic logging setup for console output
import logging
logging.basicConfig(
	format='%(asctime)s %(levelname)s %(message)s', 
	datefmt='%m/%d/%Y %I:%M:%S %p',
	level=logging.INFO)

logging.info("vocabulary load to db pipeline - START")

# generate list of languages to process
#TODO: for now just load this list from data/languages/languages.txt (list of wikipedia languages with 10,000+ articles)

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

try:
	conn = psycopg2.connect("dbname='hitman' user='dkachaev' host='localhost'")
	logging.info("successfully connected to database")
except:
	logging.error("unable to connect to the database")

cur = conn.cursor()

for lang in langs:
	sql="INSERT INTO languages (name, prefix) VALUES (%s, %s);"
	print langs_properties[lang]["name"], lang
	try:
		cur.execute(sql,(langs_properties[lang]["name"], lang))
	except:
		print "error"

conn.commit()

logging.info("languages table is loaded")


# iterate over each language individually
for i, lang in enumerate(langs):
	
	logging.info("processing language: %s (#%s out of %s) " %(lang,i+1,len(langs)))
	
	
	
	try:
		conn = psycopg2.connect("dbname='hitman' user='dkachaev' host='localhost'")
		logging.info("successfully connected to database")
	except:
		logging.error("unable to connect to the database")
	
	cur = conn.cursor()

	sql="SELECT id from languages where prefix=%s;"
	cur.execute(sql, (lang,))
	rows = cur.fetchall()

	lang_id=0
	for row in rows:
		lang_id=row[0]
	conn.close()
	
	# step #1 unpickle vocabulary
	
	f=open(settings["input_folder"]+settings["run_name"]+"_"+lang+"_vocabulary.pickle","r")
	voc=pickle.load(f)
	f.close()
	
	logging.info("loaded %s words from language: %s vocabulary" %(len(voc),lang))
	
	try:
		conn = psycopg2.connect("dbname='hitman' user='dkachaev' host='localhost'")
		logging.info("successfully connected to database")
	except:
		logging.error("unable to connect to the database")
	
	cur = conn.cursor()
	
	for word in voc:
		#print word, voc[word]
		#print type(word)
		if len(word)>0:
			sql="INSERT INTO vocabulary (word, sentences, language_id) VALUES (%s, %s,%s);"
			#print word, voc[word]["context"], lang_id
			try:
				cur.execute(sql,(word, voc[word]["context"], lang_id))
			except:
				print "error"
	
	conn.commit()
	
	logging.info("vocabulary table is loaded")
	
	#load language links

	filename=settings["input_folder"]+settings["run_name"]+"_"+lang+"_links.pickle"
	logging.info("loaded from %s " %(filename))
	f=open(filename,"r")
	links=pickle.load(f)
	f.close()
	
	logging.info("loaded %s words from english - language: %s dictionary" %(len(voc),lang))
	
	cur2 = conn.cursor()

	for word in links:
		#print word, voc[word]
		#print type(word)
		if len(word)>0:
			sql="INSERT INTO dictionary (word, translation, sentences, language_id) VALUES (%s, %s, %s, %s);"
			#print word.lower(), links[word]["translation"].lower(), links[word]["context"], lang_id
			try:
				cur2.execute(sql,(word.lower(), links[word]["translation"].lower(), links[word]["context"], lang_id))
			except:
				print "error"
				
	
	conn.commit()
	
	logging.info("dictionary table is loaded")
		
	conn.close()
		
logging.info("vocabulary load to db  pipeline - FINISH")

