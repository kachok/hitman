import wikipydia
import sys
import os
import nltk
import re
import time
import math
import argparse
#import progressbar
from bs4 import BeautifulSoup
import codecs

PATH_TO_DATA = "/home/ellie/Documents/Research/ESL/javascript/working/web/src/input-data/data-20120718"
METADATA = "/Users/epavlick/hitman/esl/data/ur-en/ur-en.metadata"
MAXLEN = 30
MINLEN = 5

reg = re.compile('(.)*(\[((.)*)\])(\((.)*\))(.)*')

def touni(x, enc='utf8', err='strict'):
	return unicode(x, encoding='utf-8')

def avglen(allsents):
	num_words = 0
	num_sents = 0
	for sent in allsents:
		for s in allsents[sent]:
			num_sents += 1
			words = s.split()
			for w in words:
				num_words += 1
	
	return float(num_words) / num_sents

def best_control(origs, allsents, dfs):
	best = ""
	tfs = term_freq(origs)
	maxx = 0
	overlapw = []
	for s in allsents:
		if(len(s.split()) <= MAXLEN and len(s.split()) >= MINLEN):
			tfidf = 0
			soverlapw = []
			words = s.split()
			for w in words:
				w = w.lower()
				tf = 0 
				df = 1
				if w in tfs:
					#tfidf += tfs[w]
					tf = tfs[w]
					soverlapw.append(w)
				if w in dfs:
					#df = 1 + math.log(float(len(tfs)) / float(dfs[w])) 
					df = 1 + dfs[w] 
				tfidf +=  float(tf) / df
				#tfidf = float(tfidf) / (float(len(words)))
				#if(tfidf > maxx):
			tfidf = float(tfidf) / math.sqrt(len(words))
			if(tfidf > maxx):
				maxx = tfidf	
				best = s
				overlapw = soverlapw
	#print maxx, overlapw, 
	return best

def all_best_control(origs, allsents):
	avg_len = avglen(allsents)
	best = {}
	tfs = term_freq(origs)
	dfs = inv_doc_freq(origs)
	for sent in allsents:
		if((sent in tfs)):	
			maxx = 0
			for s in allsents[sent]:
				tfidf = 0
				words = s.split()
				for w in words:
					tf = 0 
					df = 1
					if w in tfs[sent]:
						tf = tfs[sent][w]
					if w in dfs:
						df = 1 + math.log(float(len(tfs)) / float(dfs[w])) 
					tfidf +=  tf / df
				tfidf = float(tfidf) / (float(len(words)) + avg_len / 2)
				if(tfidf > maxx):
					maxx = tfidf	
					best[sent] = s
	return best

def term_freq(docs):
	tfs = {}
	for sent in docs:
		words = sent.split()
		for w in words:
			w = w.lower()
			if w in tfs:
				tfs[touni(w)] += 1
			else:
				tfs[touni(w)] = 1
	return tfs

def all_term_freq(docs):
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
	idfs = {}
	for sent in docs:
		words = sent.split()
		for w in words:
			w = touni(w.lower())
			if w in idfs:
				idfs[w] += 1
			else:
				idfs[w] = 1
	return idfs

def all_inv_doc_freq(docs):
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
	for doc in open(path).readlines():
		toks = doc.split('\t')
		query_terms[toks[0]] = (toks[1])
	return query_terms

def get_originals():
	by_doc = {}
	path = '/home/ellie/Documents/Research/ESL/javascript/working/web/src/input-data/data-20120718/ur-en/'
	sents = open(path+'training.ur-en.en').readlines()
	segs = open(path+'training.ur-en.seg_ids').readlines()
	for i in range(0, len(segs)):
		docid = segs[i].split('_')[0]
		if(not(docid in by_doc)):
			by_doc[docid] = [sents[i].strip()]
		else:	
			by_doc[docid].append(sents[i].strip())
	return by_doc	

def get_en_page(ur_name):
	if(wikipydia.query_exists(touni(ur_name), language='ur')):
		links = wikipydia.query_language_links(touni(ur_name), language='ur')
		if('en' in links):
			return links['en']
		else:
			return "" 

def get_sentences(page_title):
	all_sents = []
	#tmp = open('cntrl.tmp', 'w')
	txt = wikipydia.query_text_rendered(page_title)
	parse = BeautifulSoup(txt['html'])
	justtext = parse.get_text()
	#os.system("python html2text.py < cntrl.tmp > html.tmp")
	#os.remove('cntrl.tmp')
	html = ""
	#for line in open("html.tmp").readlines():
	#	html += line
	#sents = html.split("\\n")
	tok = nltk.tokenize.PunktSentenceTokenizer()
	sents = tok.tokenize(justtext)
	i = 0
	for s in sents:
		if(not(s == "")):
			all_sents.append(remove_hlinks(s))
		#s = s.strip()
		#ss = tok.tokenize(s)
		#for sss in ss:
		#	all_sents.append(remove_hlinks(sss))
		#i += 1
	return all_sents

def remove_hlinks(sentence):
	sentence = sentence.replace('\n', " ")
	sentence = sentence.replace('\W', "", re.UNICODE)
	m = reg.match(sentence)
	while(not(m == None)):
		if(m):
			sentence = sentence.replace(m.group(2), m.group(3))
			sentence = sentence.replace(m.group(5), "")
		m = reg.match(sentence)
	return sentence

def debug_html(path):
	qterms = get_query_terms(path)
	#tmp = open('cntrl.tmp', 'w')
	k = qterms.keys()[1]
	txt = wikipydia.query_text_rendered(qterms[k])
	parse = BeautifulSoup(txt['html'])
	justtext = parse.get_text()
	#os.system("python html2text.py < cntrl.tmp > html.tmp")
	#os.remove('cntrl.tmp')
	html = ""
	#for line in open("html.tmp").readlines():
	#	html += line
	#sents = html.split("\\n")
	tok = nltk.tokenize.PunktSentenceTokenizer()
	sents = tok.tokenize(justtext)
	i = 0
	for s in range(0, 100):
		print sents[s]
	return
	#	s = s.strip()
	#	ss = tok.tokenize(s)
	#	for sss in ss:
	#		all_sents.append(remove_hlinks(sss))
	#	i += 1
	#return all_sents
#	qterms = get_query_terms(path)
#	sid = qterms.keys()[0]
#	enpg = get_en_page(qterms[sid])	
#	txt = wikipydia.query_text_rendered(enpg)
#	parse = BeautifulSoup(txt['html'])
#	print parse.get_text()
#	for a in parse.find_all('li'):
#		print a

def pull_all_candidates(path):
	candidates = {}
	qterms = get_query_terms(path)
	widgets = ['Loading English page data: ', progressbar.Percentage(), ' ', progressbar.Bar(marker='=',left='[',right=']'), ' ', progressbar.ETA()]
	pbar = progressbar.ProgressBar(widgets=widgets, maxval=len(qterms))
	pbar.start()
	i = 0
	for sid in qterms:
		pbar.update(i)
		i += 1
		enpg = get_en_page(qterms[sid])
		if(not(enpg == "")):
			candidates[sid] = get_sentences(enpg)
       	pbar.finish()
	#print candidates
	return candidates

def pull_candidates(docid):
	candidates = []
	qterms = get_query_terms(METADATA)
	enpg = get_en_page(qterms[docid])
	if(not(enpg == "")):
		candidates = get_sentences(enpg)
	#print candidates
	return candidates

def cache_pages(candidates):
	widgets = ['Writing page data to cache: ', progressbar.Percentage(), ' ', progressbar.Bar(marker='=',left='[',right=']'), ' ', progressbar.ETA()]
	pbar = progressbar.ProgressBar(widgets=widgets, maxval=len(candidates))
	pbar.start()
	record = codecs.open("sentences.log", encoding='utf-8', mode='w+')
	i = 0
	for sid in candidates:
		pbar.update(i)
		i += 1
def cache_pages(candidates):
	widgets = ['Writing page data to cache: ', progressbar.Percentage(), ' ', progressbar.Bar(marker='=',left='[',right=']'), ' ', progressbar.ETA()]
	pbar = progressbar.ProgressBar(widgets=widgets, maxval=len(candidates))
	pbar.start()
	record = codecs.open("sentences.log", encoding='utf-8', mode='w+')
	i = 0
	for sid in candidates:
		pbar.update(i)
		i += 1
		record.write(sid + '\t')
		for s in candidates[sid]:
			record.write(s + '\t')
		record.write('\n')	
       	pbar.finish()
	record.close()

def get_raw_control(translations, candidates, dfs):
	outfile = open('bestctrls.out', 'w')
	b = best_control(translations, candidates, dfs)
	outfile.write(b+'\n')
#	for t in translations:
#		print t	
	outfile.close()

#	origs = get_originals()
#	bests = best_control(origs, candidates)
#
#	out = codecs.open("best.out", encoding='utf-8', mode='w+')
#
#	for sid in bests.keys():
#		out.write(sid+'\nBEST: '+bests[sid]+'\n')
#		for s in origs[sid]:
#			out.write(touni(s)+'\n')
#		out.write('\n')
#	out.close()




