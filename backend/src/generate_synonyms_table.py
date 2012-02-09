# -*- coding: utf-8 -*-


from settings import settings
import psycopg2

from nltk.corpus import wordnet
from nltk.corpus import brown # some random corpus...

import random


def syn():
	
	while True:
		#syns=wordnet.synsets(brown.words()[random.randint(1, len(brown.words())-1)].lower())
		syns=wordnet.synsets(brown.words()[random.randint(1, 1000000)].lower())
		try:
			word=syns[0].lemmas[0].name
			#print "word: ", word
			for syn in syns:
				for l in syn.lemmas:
					word2=l.name
					#print "word2: ", word2
					#not(word.search("_")>0 or len(word)<4) and not( word2.search("_")>0 or len(word2)<4) and 
					if not (word==word2) and not(word.find("_")>0 or len(word)<4) and not( word2.find("_")>0 or len(word2)<4):
						return (word,word2)
		except Exception:
			continue

# basic logging setup for console output
import logging
logging.basicConfig(
	format='%(asctime)s %(levelname)s %(message)s', 
	datefmt='%m/%d/%Y %I:%M:%S %p',
	level=logging.INFO)

logging.info("synonyms generation pipeline - START")

target_language = settings["target_language"]
logging.info("target language: %s" % (target_language))


lang="en"


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


# iterate over each language individually
for i in range(settings["number_of_synonyms"]):
	
	cur2 = conn.cursor()

	word, synonym=syn()
	
	print i, word, synonym
	
	sql="INSERT INTO synonyms (word, synonym, language_id) VALUES (%s, %s, %s);"
	cur2.execute(sql,(word, synonym,lang_id))

	conn.commit()
conn.close()
	

logging.info("synonyms generation pipeline - FINISH")
