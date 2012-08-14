import psycopg2
from settings import settings
import wikipydia
import sys
import os
import nltk
from nltk.corpus import treebank
import re
import time
import math
import argparse
import itertools
#import progressbar
from bs4 import BeautifulSoup
import codecs
from nltk.grammar import ContextFreeGrammar, Nonterminal
import nltk.chunk
import nltk.tag

PATH_TO_DATA = "/home/ellie/Documents/Research/ESL/javascript/working/web/src/input-data/data-20120718"
METADATA = "/Users/epavlick/hitman/esl/data/ur-en/ur-en.metadata"
MAXLEN = 30
MINLEN = 5

reg = re.compile('(.)*(\[((.)*)\])(\((.)*\))(.)*')

#convert string to unicode
def touni(x, enc='utf8', err='strict'):
	return unicode(x, encoding='utf-8')

#compute the average sentence length over a set of sentences
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

#find the nbest sentences in allsents that best match the sentences in origs, return nbest list of (sentence, tfidf score)
def best_control(origs, allsents, dfs, nbest=1):
	best = [("", 0)]*nbest
	tfs = term_freq(origs)
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
					tf = tfs[w]
					soverlapw.append(w)
				if w in dfs:
					df = 1 + dfs[w] 
				tfidf +=  float(tf) / df
			tfidf = float(tfidf) / math.sqrt(len(words))
			maxx = best[nbest-1][1] #tfidf of worst best sentence
			if(tfidf > maxx):
				best[nbest-1] = (s, tfidf)
				best.sort(key=lambda s : s[1], reverse=True)
	return best

#insert control_sent into the database, with one entry per error introduced into the sent
def insert_into_db(hit_id, control_sent, cur):
	sql="INSERT INTO esl_sentences(sentence, language_id, doc_id, qc, doc )VALUES (%s,%s,%s,%s,%s) RETURNING id;"
        print control_sent, isinstance(control_sent[0], unicode)
	cur.execute(sql, (control_sent[0], 23, 'control', 1, 'control'))
        insid = cur.fetchone()[0]
	for e in control_sent[1]:
		sql="INSERT INTO esl_controls(hit_id, esl_sentence_id, err_idx, oldwd, newwd, mode)VALUES (%s,%s,%s,%s,%s,%s);"
	        cur.execute(sql, (hit_id, insid, e['idx'], e['old'], e['new'], e['mode']))
	return insid

#find best control for each set of sentences in allsents, where allsents in of the form {sent_id : [list of sentences]}	
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

#count the number of occurances of each word in docs
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

#get the term_freq for each doc in docs, where docs is in the form{docid : [list of sents]}
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

#count the number of occurances of each word across all docs in docs
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

#get the doc_freq for each doc in docs, where docs is in the form{docid : [list of sents]}
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

#return a list of search terms for wikipedia, read from data at path
def get_query_terms(path):
	query_terms = {} 
	for doc in open(path).readlines():
		toks = doc.split('\t')
		query_terms[toks[0]] = (toks[1])
	return query_terms

#get a list of all the translated sentences taken from each wikipedia document, returned in the form {doc_id: [list of sentences]}
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

#get the English language link from the urdu-titled page, ur_name
def get_en_page(ur_name):
	if(touni(ur_name)):
		if(wikipydia.query_exists(touni(ur_name), language='ur')):
			links = wikipydia.query_language_links(touni(ur_name), language='ur')
			if('en' in links):
				return links['en']
			else:
				return "" 
#get sentences from wikipedia page at page_title, returning only sentences containing both NP and VP
def get_sentences(page_title):
	all_sents = []
	txt = wikipydia.query_text_rendered(page_title)
	parse = BeautifulSoup(txt['html'])
	justtext = parse.get_text()
	justtext = justtext.encode('utf-8')
	tok = nltk.tokenize.PunktSentenceTokenizer()
	sents0 = tok.tokenize(justtext)
	chunker = TagChunker(treebank_chunker())
	i = 0
	for s0 in sents0:
		i += 1
		sents = s0.split('\n')
		for s in sents:
			verbfound = False
			nounfound = False
			ss = s.split()
			if(len(ss) > 0):
				tree = chunker.parse(nltk.pos_tag(ss))
				for tag in [p[1] for p in tree.leaves()]:
					if(tag[0] == 'V'):
						verbfound = True
						break
				if(verbfound):
					for tag in [p[1] for p in tree.pos()]:
						if(tag == 'NP'):
							nounfound = True
							break
			if(verbfound and nounfound):
				all_sents.append(remove_hlinks(s))
	return all_sents

#############################################
# from http://streamhacker.com/tag/chunker/ #
#############################################
class TagChunker(nltk.chunk.ChunkParserI):
    def __init__(self, chunk_tagger):
        self._chunk_tagger = chunk_tagger
 
    def parse(self, tokens):
        # split words and part of speech tags
        (words, tags) = zip(*tokens)
        # get IOB chunk tags
        chunks = self._chunk_tagger.tag(tags)
        # join words with chunk tags
        wtc = itertools.izip(words, chunks)
        # w = word, t = part-of-speech tag, c = chunk tag
        lines = [' '.join([w, t, c]) for (w, (t, c)) in wtc if c]
        # create tree from conll formatted chunk lines
        return nltk.chunk.conllstr2tree('\n'.join(lines))


###################################################################
# http://streamhacker.com/2008/12/29/how-to-train-a-nltk-chunker/ #
###################################################################
def conll_tag_chunks(chunk_sents):
    tag_sents = [nltk.chunk.tree2conlltags(tree) for tree in chunk_sents]
    return [[(t, c) for (w, t, c) in chunk_tags] for chunk_tags in tag_sents]

def treebank_chunker():
    train_chunks = conll_tag_chunks(nltk.corpus.treebank_chunk.chunked_sents())
    chunker = nltk.tag.TrigramTagger(train_chunks)
    return chunker
def stolen_chunk_parse():
	# treebank chunking accuracy test
	treebank_sents = nltk.corpus.treebank_chunk.chunked_sents()
	ubt_conll_chunk_accuracy(treebank_sents[:2000], treebank_sents[2000:]) 

#remove wikipedia markup for hyperlinks -- NOT NECESSARY, using BeautifulSoup instead
def remove_hlinks(sentence):
	sentence = sentence.replace('\n', " ")
	sentence = re.sub('\[(\d)*\]', "", sentence, flags=re.UNICODE)
#	m = reg.match(sentence)
#	while(not(m == None)):
#		if(m):
#			sentence = sentence.replace(m.group(2), m.group(3))
#			sentence = sentence.replace(m.group(5), "")
#		m = reg.match(sentence)
	return sentence

#for debugning, print out text returned from wikipedia
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

#find all the english sentences on wikipedia that correspond to the urdu docids, where all docids are stored in file at path
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
	return candidates

#find all the english sentences on wikipedia that correspond to the urdu docid
def pull_candidates(docid):
	candidates = []
	qterms = get_query_terms(METADATA)
	if docid in qterms:
		enpg = get_en_page(qterms[docid])
		if(not(enpg == "")):
			candidates = get_sentences(enpg)
	return candidates

#write senteces retrieved from wikipedia to file for future reference
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





