# -*- coding: utf-8 -*-
import sys
import mturk
from settings import settings
import wikilanguages
import psycopg2
from itertools import islice, chain
import uuid
import random
import controls
import codecs
import generrors
import argparse 
from time import sleep
import datetime

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

logging.info("ESL hit creation pipeline - START")

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

parser = argparse.ArgumentParser()
parser.add_argument('--reload', dest='reload',  help='requery wikipedia for all control sentences', action='store_true', default=False)
args = parser.parse_args()

logging.info("generating HITTypes for each language")
# iterate over each language individually
for i, lang in enumerate(langs):
	
	logging.info("processing language: %s (#%s out of %s) " %(lang,i+1,len(langs)))
	
	# step #1 register HIT type for current language

	operation="RegisterHITType"

	parameters2=settings["eslHITtype"]

	
	output=mturk.call_turk(operation, parameters2)
	logging.debug("RegisterHITType response: %s" % (output))
	mturk_hittype_id= mturk.get_val(output, "HITTypeId")
	logging.info("HIT type for language: %s created with id: %s" % (lang, mturk_hittype_id))


	#get all words from vocabulary
	try:
		conn = psycopg2.connect("dbname='"+settings["esl_dbname"]+"' user='"+settings["user"]+"' host='"+settings["host"]+"'")
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

	
	sql="SELECT add_hittype (%s, %s, %s, %s);"
	cur.execute(sql,("ESL sentences HIT for "+langs_properties[lang]["name"], mturk_hittype_id,  lang_id, "esl"))
	hittype_id = cur.fetchone()[0]
	
	conn.commit()
	langs_properties[lang]["hittype_id"]=hittype_id

sentcounts = [] 

cur0 = conn.cursor()
sql="SELECT sentence from esl_sentences"
cur0.execute(sql)
allsents = [c[0] for c in cur0.fetchall()]
dfs = controls.inv_doc_freq(allsents)

sentfile = open('controls.goog.out', 'w')

# iterate over each language individually
for i, lang in enumerate(langs):

	logging.info("processing language: %s (#%s out of %s) " %(lang,i+1,len(langs)))
	
	hittype_id= langs_properties[lang]["hittype_id"]


	#get all words from vocabulary
	cur = conn.cursor()
	cur2 = conn.cursor()

	sql="SELECT id from languages where prefix=%s;"
	cur.execute(sql, (lang,))
	rows = cur.fetchall()

	lang_id=0
	for row in rows:
		lang_id=row[0]

	web_endpoint='http://'+settings["web_enpoint_domain"]+settings["web_endpoint_esl_hit_path"]+"/"+lang
	check = 0

	sql="SELECT worker from esl_sentences"
	cur.execute(sql)
	allworkers = list(set(cur.fetchall()))
	for worker in allworkers[:10]:
		sql="SELECT * from esl_sentences where worker=%s order by doc_id"
		cur2.execute(sql, (worker,))
		rows = cur2.fetchall()
		for batchiter in batch(rows, settings["num_unknowns"]):
			guid=str(uuid.uuid4())
		        qcnum = random.randint(0, settings["num_unknowns"] + settings["num_knowns"] -1)
        	        try: 
				sql="SELECT add_hit(%s, %s, %s, %s, %s, %s, %s);"
				cur2.execute(sql,("", guid, hittype_id, lang_id, 0, 0, 0))
              	 	except Exception, e:
				print sys.exc_info()[0]
				print e.pgerror
			if(cur2.rowcount > 0):
				hit_id = cur2.fetchone()[0]
        	        	if(not(hit_id in sentcounts)):
                			sentcounts.append(hit_id)
				n = 0
				#Insert 4 non-control sentences
				sents = []
				sentnums = []
				doc = "" 
				for item in batchiter:
					sents.append(item)
					doc = item[6]
					sentnums.append(item[4])
				#Insert 1 control sentence
				for s in sents:
					sentfile.write(str(s[0]) + ' ')
				sentfile.write('\n')
				justsents = [s[1] for s in sents]
				topwords = controls.get_topn(justsents, dfs, 5)
				querywords = [w for w, freq in topwords]
				cachefile = 'caches/controls.cache.'+str(datetime.datetime.now()).replace('\s', "-")
				#candidatecache = controls.pull_all_candidates_goog_cacheresults(querywords, cachefile)
				candidates = controls.pull_all_candidates_from_cache(querywords)
				if(len(candidates) > 0):
					b = controls.best_control(justsents, candidates, dfs)
					for j in justsents:
						print j
						sentfile.write(j+'\n')
					sentfile.write(str(b[0][0])+'\n\n')
					print b[0]
				
conn.commit()

conn.close()

if(args.reload):	
	outfile.close()
logging.info("esl hit creation pipeline - FINISH")

