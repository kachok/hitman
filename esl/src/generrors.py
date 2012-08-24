import itertools
import nltk
import random
import sys
import re
import codecs

def deterr(words, idx):
	pos = nltk.pos_tag(words)
	if(random.getrandbits(1)):
		return changedet(words, idx)
	else:
		error = {'idx' : idx, 'old' : words[idx], 'new' : "", 'mode' : "delete"}
		print idx, len(words)
		words[idx] = ''
		return (words, error)

def adddet(chunks, idx):
	dets = ['a', 'an', 'the']
	newd = dets[random.randint(0, len(dets) -1)]
	chunks.insert(idx, (newd, 'ADDED'))
	leaves = chunks.leaves()
	realidx = -1
	for i, leaf in enumerate(leaves):
		if(leaf[1] == 'ADDED'):
			realidx = i
	#TODO THIS IDX IS NOT CORRECT##########
	error = {'idx' : realidx, 'old' : "", 'new' : newd, 'mode' : "insert"}
	return (tree2words(chunks.root), error)

def changedet(words, idx):
        dets = ['a', 'an', 'the']
	print idx, len(words)
        word = words[idx]
        newd = random.randint(0, len(dets) - 1)
        while(dets[newd] == word):
                newd = random.randint(0, len(dets) - 1)
        words[idx] = dets[newd]
        error = {'idx' : idx, 'old' : word, 'new' : newd, 'mode' : "change"}
        return (words, error)

def tree2sent(tree):
	leaves = tree.leaves()
	s = ""
	for l in leaves:
		s += l[0] + " "
	return s

def tree2words(tree):
	leaves = tree.leaves()
	s = []
	for l in leaves:
		s.append(l[0])
	return s


def preperr(words, idx):
	preps = ['in', 'on', 'at', 'of', 'for', 'with', 'by']
	print idx, len(words)
	word = words[idx]
	newp = random.randint(0, len(preps) - 1)
	while(preps[newp] == word):
		newp = random.randint(0, len(preps) - 1)
	#words[idx] = '['+preps[newp]+']'a
	words[idx] = preps[newp]
	error = {'idx' : idx, 'old' : word, 'new' : preps[newp], 'mode' : "change"}
	return (words, error)

def spellerr(words, idx):
	print idx, len(words)
	word = words[idx]
	w = ""
	chars = list(word)
	if(len(chars) > 4):
		swapidx = random.randint(2, len(chars)-1)	
		tmp = chars[swapidx]
		chars[swapidx] = chars[swapidx - 1]
		chars[swapidx - 1] = tmp
		for c in chars:
			w += c
		#words[idx] = '['+w+']'
		words[idx] = w
	error = {'idx' : idx, 'old' : word, 'new' : w, 'mode' : "change"}
	return (words, error)

def verberr(words, idx):
	beverbs = ['be', 'is', 'am', 'are', 'was', 'were', 'being']
	print idx, len(words)
	if words[idx] in beverbs:
		return beverberr(words, idx)
	else:
		return otherverberr(words, idx)

def otherverberr(words, idx):
	w = words[idx]
	endings = {'ing' : r'(.*)ing\Z', 'ed' : r'(.*)ed\Z', 'es' : r'(.*)es\Z', 's' : r'(.*)s\Z'}
	for end in endings:
		m = re.match(endings[end], w)
		if(m): 
			nend = endings.keys()[random.randint(0, len(endings.keys()) - 1)]
			while(end == nend):
				nend = endings.keys()[random.randint(0, len(endings.keys()) - 1)]
			words[idx] = m.group(1) + nend
			error = {'idx' : idx, 'old' : w, 'new' : words[idx], 'mode' : "change"}
			return (words, error)
	nend = endings.keys()[random.randint(0, len(endings.keys()) - 1)]
	#words[idx] = '['+words[idx] + nend+']'
	words[idx] = words[idx] + nend
	error = {'idx' : idx, 'old' : w, 'new' : words[idx], 'mode' : "change"}
	return (words, error)

def beverberr(words, idx):
	beverbs = ['be', 'is', 'am', 'are', 'was', 'were', 'being']	
	w = words[idx]
	nbe = beverbs[random.randint(0, len(beverbs) - 1)]
	while(w == nbe):
		nbe = beverbs[random.randint(0, len(beverbs) - 1)]
	#words[idx] = '['+nbe+']'
	words[idx] = nbe
	error = {'idx' : idx, 'old' : w, 'new' : words[idx], 'mode' : "change"}
	return (words, error)

def nounphrase(tree):
	flat = tree.flatten()
	if(flat[0][1] == 'NNP'):
		return True
	return False

def getpos(sent, logfile):
	print "GET POS", sent
	verb = []
	prep = []
	noun = []
	det = []
	words = nltk.word_tokenize(sent) #sent.split()
	print words
	pos = nltk.pos_tag(words)
	print pos
	logfile.write(str(pos)+'\n')
	chunker = TagChunker(treebank_chunker())
	chunks = chunker.parse(pos)
	for i, p in enumerate(pos):
		ptag = p[1]
		if(ptag[0] == 'V'):
			verb.append(i) 
		if(ptag == 'IN'):
			prep.append(i)
		if(ptag == 'DT'):
			det.append(i)
	partree = nltk.tree.ParentedTree.convert(chunks)
	for t in partree.subtrees():
		if(nounphrase(t)):
			noun.append(t.parent_index)
	
	return {"verb" : verb, "prep" : prep, "noun" : noun, "det" : det, "chunktree" : partree, "postags" : pos}
	#return {"verb" : verb, "prep" : prep, "det" : det, "postags" : pos}

def list2str(words):
	s = ""
	for w in words:
		s += w + " "
	return s

#insert determiner errors for every noun phrase
def randerralldet(sent):
	errors = []
	alteredidx = []
	words = sent.split()
	if(len(words) > 0):
		pos = getpos(sent)
		verb = pos['verb']
		prep = pos['prep']
		noun = pos['noun']
		chunks = pos['chunktree']
		#introduce determiner errors
		timeout = 0
		for n in noun:
			if(not(n == None)):
				#r = deterr(words, noun[nidx])
				r = deterr(chunks, n)
				errors.append(r)
				words = r[0]
				alteredidx.append(n)

def updateidx(lst, threshold):
	newlst = []
	for pos in lst:
		if(pos > threshold):
			pos += 1
		newlst.append(pos)
	return newlst		

def randerr(sent):
	logfile = codecs.open("error.log", encoding='utf-8', mode='a')
	errors = []
	alteredidx = []
	words = nltk.word_tokenize(sent) #sent.split()
	if(len(words) > 0):
		pos = getpos(sent, logfile)
		print pos
		chunks = pos['chunktree']
		if(len(words)/3 <= 3):
			coin = random.randint(1, len(words) / 3)
		else:
			coin = random.randint(3, len(words) / 3)
		errlists = [pos['prep'], pos['det'], pos['noun'], range(0, len(words) - 1), pos['verb']]
		errfuncs = [preperr, deterr, adddet, spellerr, verberr];
		#errfuncs = [preperr, deterr, spellerr, verberr];
		#print list2str(words)
		print errlists			
		while(coin > 0):
			#print words
			#logfile.write(str(words)+'\n')
			logfile.write(list2str(words)+'\n')
			timeout = 0
			erridx = random.randint(0, len(errlists)-1)
			idxlist = errlists[erridx]
			funct = errfuncs[erridx]
			param = words
			if(funct == adddet):
				param = chunks
			if(len(idxlist) > 0):
				logfile.write(str(funct)+" "+str(idxlist)+'\n')
				idx = random.randint(0, len(idxlist) - 1)
			 	while(timeout < 50 and (idxlist[idx] == None or idx >= len(words))):
					timeout += 1
					idx = random.randint(0, len(idxlist) -1)
				if(idxlist[idx] == None):
					continue
				r = funct(param, idxlist[idx])
				idxlist.pop(idx)
				errors.append(r)
				words = r[0]
				if(r[1]['mode'] == 'insert'):
					for lst in [0, 1, 2, 4]:
						#print lst, errlists[lst], r[1]['idx']
						errlists[lst] = updateidx(errlists[lst], r[1]['idx'])
						#print lst, errlists[lst], r[1]['idx']
	#				print list2str(words)
	#				print words, len(words)
				coin -= 1

	retval = []
	for e in errors:
		retval.append(e[1])
	logfile.write(list2str(words)+'\n')
	logfile.write('\n')
	return (list2str(words), retval)


############################################################################
# code from http://streamhacker.com/2009/02/23/chunk-extraction-with-nltk/ #
############################################################################
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

#############################################################################
# code from http://streamhacker.com/2008/12/29/how-to-train-a-nltk-chunker/ #
#############################################################################

def treebank_chunker():
	# treebank chunking accuracy test
	train_chunks = nltk.corpus.treebank_chunk.chunked_sents()
	return nltk.tag.TrigramTagger(conll_tag_chunks(train_chunks))
 
def conll_tag_chunks(chunk_sents):
    tag_sents = [nltk.chunk.tree2conlltags(tree) for tree in chunk_sents]
    return [[(t, c) for (w, t, c) in chunk_tags] for chunk_tags in tag_sents] 
