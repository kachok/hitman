import wikipydia
import html2text
import sys
import os
import nltk
import re
import urllib
import json as simplejson
import calendar
import datetime
import time
import math
#import progressbar

PATH_TO_DATA = "/home/ellie/Documents/Research/ESL/javascript/working/web/src/input-data/data-20120718"

reg = re.compile('(.)*(\[((.)*)\])(\((.)*\))(.)*')


def touni(x, enc='utf8', err='strict'):
	return unicode(x, encoding='utf-8')

def best_control(allsents):
	best = {}
	tfs = term_freq(allsents)
	dfs = inv_doc_freq(allsents)
	for sent in allsents:
		if(not(sent=="")):	
			maxx = 0
			for s in allsents[sent]:
				tfidf = 0
				words = s.split()
				for w in words:
					tfidf += ( (tfs[sent][w]) / (1 + math.log(float(len(tfs)) / float(dfs[w])) ) )
				if(tfidf > maxx):
					maxx = tfidf	
					best[sent] = s
	for b in best:
		print b, best[b]
	return best

def term_freq(docs):
	print "tfs..."
	all_tfs = {}
	for docid in docs:
		tfs = {}
		for sent in range(0, len(docs[docid])):
			words = docs[docid][sent].split()
			for w in words:
				if w in tfs:
					tfs[w] += 1
				else:
					tfs[w] = 1
		all_tfs[docid] = tfs	
	return all_tfs

def inv_doc_freq(docs):
	print "idfs..."
	idfs = {}
	for docid in docs:
		for sent in range(0, len(docs[docid])):
			words = docs[docid][sent].split()
			for w in words:
				if w in idfs:
					idfs[w] += 1
				else:
					idfs[w] = 1
	return idfs

def get_query_terms(path):
	query_terms = {} 
	for doc in open(path):
		toks = doc.split('\t')
		query_terms[toks[0]] = (toks[1])
	return query_terms

def get_original_ids():
	lookup =  hacky_backfill('/home/ellie/Documents/Research/ESL/javascript/working/web/src/input-data/data-20120718/ur-en/')

def get_en_page(ur_name):
	if(wikipydia.query_exists(touni(ur_name), language='ur')):
		links = wikipydia.query_language_links(touni(ur_name), language='ur')
		if('en' in links):
			return links['en']
		else:
			return "" 

def get_sentences(page_title):
	print page_title
	all_sents = []
	tmp = open('cntrl.tmp', 'w')
	txt = wikipydia.query_text_rendered(page_title)
	tmp.write(str(txt))
	os.system("python html2text.py < cntrl.tmp > html.tmp")
	os.remove('cntrl.tmp')
	html = ""
	for line in open("html.tmp").readlines():
		html += line
	sents = html.split("\\n")
	tok = nltk.tokenize.PunktSentenceTokenizer()
	i = 0
	for s in sents:
		s = s.strip()
		ss = tok.tokenize(s)
		for sss in ss:
			all_sents.append(remove_hlinks(sss))
		i += 1
	return all_sents

def remove_hlinks(sentence):
	sentence = sentence.replace('\n', " ")
	m = reg.match(sentence)
	while(not(m == None)):
		if(m):
			sentence = sentence.replace(m.group(2), m.group(3))
			sentence = sentence.replace(m.group(5), "")
		m = reg.match(sentence)
	return sentence

def hacky_backfill(path):
	revdict = {}
	sents = open(path+'training.ur-en.en').readlines()
	segs = open(path+'training.ur-en.seg_ids').readlines()
	for i in range(0, len(sents)):
		revdict[sents[i].strip()] = segs[i].strip()
	return revdict
	

#----------------------MAIN-------------------------#

candidates = {}

record = open("sentences.log")
for line in record:
	toks = line.split('\t')
	candidates[toks[0]] = toks[1:]



#qterms = get_query_terms(PATH_TO_DATA+"/ur-en/ur-en.metadata")

#for sid in qterms:
#	enpg = get_en_page(qterms[sid])
#	if(not(enpg == "")):
#		tfidfs[sid] = get_sentences(enpg)

#record = open("sentences.log", 'w')
#for sid in tfidfs:
#	record.write(sid + '\t')
#	for s in tfidfs[sid]:
#		record.write(s + '\t')
#	record.write('\n')
#
#record.close()

best_control(candidates)





