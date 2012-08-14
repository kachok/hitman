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
METADATA = "/Users/epavlick/hitman/esl/data/ur-en/ur-en.metadata.short"
MAXLEN = 30
MINLEN = 5

reg = re.compile('(.)*(\[((.)*)\])(\((.)*\))(.)*')

def touni(x, enc='utf8', err='strict'):
#	if(isinstance(x, unicode)):
	return unicode(x, encoding='utf-8')
#	else:
#		return None

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

def best_control(origs, allsents, dfs, nbest=1):
	best = [("", 0)]*nbest
	#best = ""
	tfs = term_freq(origs)
	#maxx = 0
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
			#	print best
				best[nbest-1] = (s, tfidf)
				best.sort(key=lambda s : s[1], reverse=True)
			#	print best
#				maxx = tfidf	
#				best = s
#				overlapw = soverlapw
	return best

def insert_into_db(control_sent, cur):
#	conn = psycopg2.connect("dbname='"+settings["esl_dbname"]+"' user='"+settings["user"]+"' host='"+settings["host"]+"'")
#	cur = conn.cursor()
	print control_sent
	sql="INSERT INTO esl_sentences(sentence, language_id, doc_id, qc, doc )VALUES (%s,%s,%s,%s,%s) RETURNING id;"
        cur.execute(sql, (control_sent, 23, 'control', 1, 'control'))
        insid = cur.fetchone()[0]
	sql="INSERT INTO esl_controls(esl_sentence_id, sentence, err_idx, oldwd, newwd, mode)VALUES (%s,%s,%s,%s,%s) RETURNING id;"
        cur.execute(sql, (insid, control_sent[0], control_sent[1]['idx'], control_sent[1]['old'], control_sent[1]['new'], control_sent[1]['mode']))
	return insid

	
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
	if(touni(ur_name)):
		if(wikipydia.query_exists(touni(ur_name), language='ur')):
			links = wikipydia.query_language_links(touni(ur_name), language='ur')
			if('en' in links):
				return links['en']
			else:
				return "" 

def get_sentences(page_title):
#	tbank_productions = set(production for sent in treebank.parsed_sents() for production in sent.productions())
#	g = ContextFreeGrammar(Nonterminal('S'), list(tbank_productions))
	all_sents = []
	txt = wikipydia.query_text_rendered(page_title)
	parse = BeautifulSoup(txt['html'])
	justtext = parse.get_text()
	justtext = justtext.encode('utf-8')
	tok = nltk.tokenize.PunktSentenceTokenizer()
	sents0 = tok.tokenize(justtext)
	#sents = [s.replace('\n', ' ') for s in sents0]
	#sents = nltk.pos_tag(sents1)
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
#				poss = nltk.pos_tag(ss)
#				for tag in [p[1] for p in poss]:
#					if(tag[0] == 'V'):
#						verbfound = True
#						break
				tree = chunker.parse(nltk.pos_tag(ss))
#				print tree
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
				#print remove_hlinks(s)
				all_sents.append(remove_hlinks(s))
#				if(not(verbfound)):
#					print s
		#		trees = chunker.parse(nltk.pos_tag(ss)).leaves() #subtrees()
		#		for tree in trees:	
		#			print tree
#					if(not(verbfound)):
#						for tag in [p[1] for p in tree.pos()]:
#							print tag, tag[0] == 'V'
#							if(tag[0] == 'V'):
#								verbfound = True
#								break
#				if(not(verbfound)):
#					print s 							
#					all_sents.append(remove_hlinks(s))
	return all_sents

###########STOLEN CODE##############
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


###########STOLEN CODE##############
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
	if docid in qterms:
		enpg = get_en_page(qterms[docid])
		if(not(enpg == "")):
			candidates = get_sentences(enpg)
	#print candidates
	return candidates

#def cache_pages(candidates):
#	widgets = ['Writing page data to cache: ', progressbar.Percentage(), ' ', progressbar.Bar(marker='=',left='[',right=']'), ' ', progressbar.ETA()]
#	pbar = progressbar.ProgressBar(widgets=widgets, maxval=len(candidates))
#	pbar.start()
#	record = codecs.open("sentences.log", encoding='utf-8', mode='w+')
#	i = 0
#	for sid in candidates:
#		pbar.update(i)
#		i += 1
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




