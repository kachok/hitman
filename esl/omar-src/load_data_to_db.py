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

DATA_PATH = "/Users/epavlick/hitman/esl/data/omar-data.workerids.out"

try:
	conn = psycopg2.connect("dbname='"+settings["esl_dbname"]+"' user='"+settings["user"]+"' host='"+settings["host"]+"'")
	print settings["esl_dbname"]
	logging.info("successfully connected to database")
except:
	logging.error("unable to connect to the database")

lang="en"

logging.info("processing esl sentences")

cur = conn.cursor()

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
	if(not(line == "")):
		count=count+1
		docid = line[0].split('_')
		if(len(docid) > 1):
			doc = docid[0]+'_'+docid[1]
			qc = 0
			if(len(docid) == 3):
				qc = 1
			sentence=line[1].strip()
			worker = line[2].strip()	
			sql="INSERT INTO esl_sentences(sentence, sequence_num, language_id, doc_id, qc, doc, worker) VALUES (%s,%s,%s,%s,%s,%s,%s);"
			try:
				cur.execute(sql,(sentence, count, 23, doc, qc, docid[0], worker))
			except Exception, ex:
				print "voc error"
				print ex
conn.commit()

logging.info("esl sentences table is loaded")
		
conn.close()
		
logging.info("load data to db pipeline - FINISH")

