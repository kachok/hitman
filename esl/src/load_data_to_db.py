# -*- coding: utf-8 -*-

from settings import settings
import wikilanguages
import pickle
import psycopg2
from operator import itemgetter
import csv

# basic logging setup for console output
import logging
logging.basicConfig(
	format='%(asctime)s %(levelname)s %(message)s', 
	datefmt='%m/%d/%Y %I:%M:%S %p',
	level=logging.INFO)

logging.info("load data to db pipeline - START")

#DATA_PATH = "../data/best-by-doc-20120808.250"
DATA_PATH = "../data/best-by-doc-20120808.50"
CONTROL_PATH = "../data/ctrl-by-doc-20120808.test"

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
	conn = psycopg2.connect("dbname='"+settings["esl_dbname"]+"' user='"+settings["user"]+"' host='"+settings["host"]+"'")
	print settings["esl_dbname"]
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

#print langs

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


lang="en"

logging.info("processing esl sentences")

cur = conn.cursor()

sql="SELECT id from languages where prefix=%s;"
cur.execute(sql, (lang,))
rows = cur.fetchall()
#print len(rows)
#print cur.description

lang_id=0
for row in rows:
	lang_id=row[0]
conn.commit()

# step #1 unpickle vocabulary

cur = conn.cursor()

# f=open("../data/raw.en.final")
f=open(DATA_PATH)

count=0

eslReader = open(DATA_PATH).readlines()

lines = []
count=0
for csvline in eslReader:
	line = csvline.split('\t')
	lines.append(line)
lines = sorted(lines, key=itemgetter(0))
for line in lines:
	print line
	if(not(line == "")):
		count=count+1
	#	print count, line[0], line[1]
		docid = line[0]
		doc = docid.split('_')[0]
		sentence=line[1].strip()
	
		sql="INSERT INTO esl_sentences (sentence, sequence_num, language_id, doc_id, qc, doc) VALUES (%s,%s,%s,%s,%s,%s);"
		try:
			cur.execute(sql,(sentence, count, lang_id, docid, '0', doc))
		except Exception, ex:
			print "voc error"
			print ex
		
conn.commit()

logging.info("esl sentences table is loaded")

#ctrlReader = open(CONTROL_PATH).readlines()
#for csvline in ctrlReader:
#	if(not(csvline == "")):
#		line = csvline.split('\t')
#		count=count+1
#		print line #[0], line[1]
#		doc = line[0]
#		sentence=line[1].strip()
	
#		sql="INSERT INTO esl_sentences (sentence, sequence_num, language_id, doc_id, qc) VALUES (%s,%s,%s,%s,%s);"
#		try:
#			cur.execute(sql,(sentence, count, lang_id, doc+'c', '1'))
#		except Exception, ex:
#			print "voc error"
#			print ex
#		sql="INSERT INTO esl_controls (esl_sentence_id, sentence) VALUES (%s,%s);"
#		try:
#			cur.execute(sql,(doc, sentence))
#		except Exception, ex:
#			print "voc error"
#			print ex
		
conn.commit()
logging.info("esl controls table is loaded")
		
conn.close()
		
logging.info("load data to db pipeline - FINISH")

