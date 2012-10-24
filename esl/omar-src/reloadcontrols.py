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

DATA_PATH = "data-dump-2012-09-02_17:57/cntrl_data"

try:
	conn = psycopg2.connect("dbname='"+settings["esl_dbname"]+"' user='"+settings["user"]+"' host='"+settings["host"]+"'")
	print settings["esl_dbname"]
	logging.info("successfully connected to database")
except:
	logging.error("unable to connect to the database")

cur = conn.cursor()

eslReader = open(DATA_PATH).readlines()

sql = "INSERT INTO esl_controls(esl_sentence_id,sentence,err_idx,oldwd,newwd,mode,hit_id,seq_num) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"

for csvline in eslReader:
	line = csvline.split(',')
	iline = [l.strip() for l in line]
	try:
		cur.execute(sql, (iline[0],iline[1],int(iline[2]),iline[3],iline[4],iline[5],iline[6],int(iline[7])))
	except:
		print "skipping a line"
		pass
conn.commit()

logging.info("esl sentences table is loaded")

conn.close()
		
logging.info("load data to db pipeline - FINISH")
