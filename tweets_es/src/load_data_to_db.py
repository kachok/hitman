# -*- coding: utf-8 -*-

from settings import settings
import wikilanguages
import pickle
import psycopg2

# basic logging setup for console output
import logging
logging.basicConfig(
	format='%(asctime)s %(levelname)s %(message)s', 
	datefmt='%m/%d/%Y %I:%M:%S %p',
	level=logging.INFO)

logging.info("load data to db pipeline - START")

# generate list of languages to process
#TODO: for now just load this list from data/languages/languages.txt (list of wikipedia languages with 10,000+ articles)

target_language = settings["target_language"]
target_language_name = settings["target_language_name"]
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

#adding target language separately
sql="SELECT add_language (%s, %s);"
logging.info("adding language %s(%s)" % (target_language_name, target_language))
try:
	cur.execute(sql,(target_language_name,target_language))
except:
	print "error"

print langs

for lang in langs:
	print lang
	sql="SELECT add_language (%s, %s);"
	logging.info("adding language %s(%s)" % (lang, langs_properties[lang]["name"]))
	try:
		cur.execute(sql,(langs_properties[lang]["name"], lang))
	except:
		print "error"

conn.commit()

logging.info("languages table is loaded")


lang="es"

logging.info("processing spanish tweets ")

cur = conn.cursor()

sql="SELECT id from languages where prefix=%s;"
cur.execute(sql, (lang,))
rows = cur.fetchall()

lang_id=0
for row in rows:
	lang_id=row[0]
conn.commit()

# step #1 unpickle vocabulary

cur = conn.cursor()

f=open("../data/spanish-mitre-2009-04.txt")

count=0

for line in f:
	line.replace("		","	")
	t=line.strip().split("	",1)
	count=count+1
	if count==1:
		continue
	
	tweetid=t[0]
	tweet=t[1]

	sql="INSERT INTO tweets (tweetid, tweet, language_id) VALUES (%s,%s,%s);"
	try:
		cur.execute(sql,(tweetid, tweet, lang_id))
	except Exception, ex:
		print "voc error"
		print ex

conn.commit()

logging.info("tweets table is loaded")

logging.info("processing spanish tweets translations")

f=open("../data/tweets_translate_2.txt", 'U')

count=0

for line in f:
	line.replace("		","	")
	t=line.strip().split("	",5)
	count=count+1
	if count==1:
		continue
	
	tweetid=t[0]
	tweet=t[1].decode('unicode_escape')
	translation=t[2].decode('unicode_escape')
	google=t[4]
	bing=t[5]
	

	sql="INSERT INTO translations (tweetid, tweet, translation, google, bing, language_id) VALUES (%s,%s,%s,%s,%s,%s);"
	try:
		cur.execute(sql,(tweetid, tweet, translation, google, bing, lang_id))
	except Exception, ex:
		print "voc error"
		print ex

conn.commit()

logging.info("translations table is loaded")
		
conn.close()
		
logging.info("load data to db pipeline - FINISH")

