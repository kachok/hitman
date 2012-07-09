# -*- coding: utf-8 -*-

from apiclient.discovery import build
import settings

# -*- coding: utf-8 -*-


import mturk
from settings import settings

import wikilanguages

import psycopg2

from itertools import islice, chain

from time import sleep

import urllib2

# basic logging setup for console output
import logging
logging.basicConfig(
	format='%(asctime)s %(levelname)s %(message)s', 
	datefmt='%m/%d/%Y %I:%M:%S %p',
	level=logging.INFO)

logging.info("google translation of spanish tweets- START")

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
	conn = psycopg2.connect("dbname='"+settings["dbname"]+"' user='"+settings["user"]+"' host='"+settings["host"]+"'")
	logging.info("successfully connected to database")
except:
	logging.error("unable to connect to the database")

cur = conn.cursor()

#getting language_id from database
sql="SELECT id, tweet from tweets where google='' or google is null order by id;"
cur.execute(sql)
rows = cur.fetchall()


for row in rows:
	tweet_id=str(row[0])
	tweet=str(row[1])

	# Build a service object for interacting with the API. Visit
	# the Google APIs Console <http://code.google.com/apis/console>
	# to get an API key for your own application.
	service = build('translate', 'v2',
	developerKey=settings["google_translate_key"])

	tweet=unicode(tweet, 'utf-8')

	print tweet
	#tweet=urllib2.quote(tweet)

	print type(tweet)
	#tweet= tweet.decode('unicode_escape')


	translation= service.translations().list(
	source='es',
	target='en',
	q=[tweet]
	).execute()['translations'][0]['translatedText']
	print tweet_id, translation

	cur2=conn.cursor()
	#getting hittype_id from database
	sql="UPDATE tweets SET google=%s where id=%s;"
	cur2.execute(sql, (translation, tweet_id))
	conn.commit()
	

		
conn.close()

logging.info("google translation of spanish tweets - FINISH")


