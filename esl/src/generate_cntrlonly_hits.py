# -*- coding: utf-8 -*-
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
sentsql = "SELECT sentence from esl_sentences;"
cur0.execute(sentsql)
allsents = [c[0] for c in cur0.fetchall()]
dfs = controls.inv_doc_freq(allsents)

if(args.reload):
	outfile = codecs.open('controls.log', encoding='utf-8', mode='w+')
	hitslogged = []
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

#	sql="SELECT * from esl_sentences WHERE language_id=%s order by sequence_num;" #random();"
	sql="SELECT * from esl_sentences order by doc_id" #sequence_num;" #random();"
	cur.execute(sql)
	rows = cur.fetchall()
	print len(rows)

	web_endpoint='http://'+settings["web_enpoint_domain"]+settings["web_endpoint_esl_hit_path"]+"/"+lang
	
	for batchiter in batch(rows, settings["num_unknowns"] + settings["num_knowns"]):

		qcnum = random.randint(0, settings["num_unknowns"] + settings["num_knowns"] -1)	
	
		guid=str(uuid.uuid4())

		sql="SELECT add_hit(%s, %s, %s, %s, %s, %s, %s);"
		cur2.execute(sql,("", guid, hittype_id, lang_id, 0, 0, 0))
		hit_id = cur2.fetchone()[0]
		if(not(hit_id in sentcounts)):
			sentcounts.append(hit_id)

		logging.info("Batch added")
		sents = []
		sentids = []
		if(args.reload):
			for item in batchiter:
				doc_id = item[4]
				candidates = controls.pull_candidates(doc_id.split('_')[0])			
				idsql = 'SELECT sentence from esl_sentences where doc_id=%s;'
				cur2.execute(idsql, (doc_id,))
				sents.append(cur2.fetchone()[0])	
				sentids.append(doc_id)
			if(len(candidates) > 0):
				i = 0
        			b = controls.best_control(sents, candidates, dfs, nbest=5)
				for bb in b:
					bbuni = controls.touni(bb[0])
					newb = generrors.randerr(bb[0])
					cid = controls.insert_into_db(hit_id, newb, cur2)
					outfile.write(bbuni+'\t')
					sql="INSERT INTO esl_hits_data(hit_id,esl_sentence_id,language_id,sentence_num)VALUES(%s,%s,%s,%s);"
					cur2.execute(sql,(hit_id, cid, lang_id, i))
					i += 1
				outfile.write('\n')
			conn.commit()
		else:
			cachedsents = open('controls.log')
			for hit in cachedsents.readlines():
				b = hit.split('\t')
				i = 0
				for bb in b:
					bbuni = controls.touni(bb)
					newb = generrors.randerr(bb)
					cid = controls.insert_into_db(hit_id, newb, cur2)
					sql="INSERT INTO esl_hits_data(hit_id,esl_sentence_id,language_id,sentence_num)VALUES(%s,%s,%s,%s);"
					cur2.execute(sql,(hit_id, cid, lang_id, i))
					i += 1
			conn.commit()
					
	#purge HITs with missing sentences or missing controls
	for hit in sentcounts:
		delsql = "select id from esl_hits_data where hit_id=%s;"
		cur2.execute(delsql, (hit,))
		if(cur2.rowcount < 5):
			delsql = "delete from esl_hits_data where hit_id=%s;"
			cur2.execute(delsql, (hit,))
			delsql = "delete from hits where id=%s;"
			cur2.execute(delsql, (hit,))
			if(cur2.rowcount > 0):
				print "purged", hit

	conn.commit()

conn.close()

if(args.reload):	
	outfile.close()
logging.info("esl hit creation pipeline - FINISH")

