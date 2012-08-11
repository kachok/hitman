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

outfile = codecs.open('bestctrls.3sentwindow.out', encoding='utf-8', mode='w+')
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

	sql="SELECT * from esl_sentences order by doc_id"
	cur.execute(sql)
	rows = cur.fetchall()

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
		i = 0
		sents = []
		docs = []
		ids = []
		for item in batchiter:
			doc_id = item[4]
			dbid = item[0]
			doc = item[4].split('_')[0]
			if(not(doc in docs)):
				docs.append(doc)
			if(not(dbid in ids)):
				ids.append(dbid)
			candidates = controls.pull_candidates(doc_id.split('_')[0])			
			idsql = 'SELECT sentence from esl_sentences where doc_id=%s;'
			cur2.execute(idsql, (doc_id,))
			sents.append(cur2.fetchone()[0])	
		print ids
		augment_ids = []
		ids = sorted(ids)
		for nid in range(ids[0] - 3, ids[len(ids)-1] + 3):
			augment_ids.append(nid)
		docsents = []
		#for d in docs:
		#	idsql = 'SELECT sentence from esl_sentences where doc=%s;'
		#	cur2.execute(idsql, (d,))
		#	print d
		#	docsents += [row[0] for row in cur2.fetchall()]	
		for i in augment_ids:
			idsql = 'SELECT sentence from esl_sentences where id=%s;'
			cur2.execute(idsql, (i,))
		#	print i
			docsents += [row[0] for row in cur2.fetchall()]	
	
#		control = controls.get_raw_control(sents, candidates, dfs)
		print len(docsents)
        	b = controls.best_control(docsents, candidates, dfs)
		print b
		for s in sents:
			outfile.write(s+'\n')
        	outfile.write("Control: "+b+'\n')
        	outfile.write('\n')

conn.close()
	

logging.info("esl hit creation pipeline - FINISH")

