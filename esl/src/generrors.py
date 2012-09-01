import itertools
import nltk
import random
import sys
import re
import codecs
#note: errors are stored wrt the final version of the sentence (how they will be corrected) not the original version (how they were generated)

#randomly change or delete a determiner from words
def deterr(words, idx):
	pos = nltk.pos_tag(words)
	if(random.getrandbits(1)):
		return changedet(words, idx)
	else:
		error = {'idx' : idx, 'old' : words[idx], 'new' : "", 'mode' : "insert"}
		words[idx] = ''
		return (words, error)

#randomly add a determiner in from of an NP in chunks
def adddet(words, idx):
	new = []
	dets = ['a', 'an', 'the']
	newd = dets[random.randint(0, len(dets) -1)]
	for w in words[:idx]:
		new.append(w)
	new.append(newd)
	for w in words[idx:]:
		new.append(w)
	error = {'idx' : idx, 'old' : "", 'new' : newd, 'mode' : "delete"}
	return (new, error)

#randomly add a determiner in from of an NP in chunks
def adddet1(chunks, idx):
	dets = ['a', 'an', 'the']
	newd = dets[random.randint(0, len(dets) -1)]
	chunks.insert(idx, (newd, 'ADDED'))
	leaves = chunks.leaves()
	realidx = -1
	for i, leaf in enumerate(leaves):
		if(leaf[1] == 'ADDED'):
			realidx = i
	error = {'idx' : realidx, 'old' : "", 'new' : newd, 'mode' : "delete"}
	return (tree2words(chunks.root), error)

def detidx(chunks, idx):
	chunks.insert(idx, ('ADDED', 'ADDED'))
	leaves = chunks.leaves()
	realidx = -1
	for i, leaf in enumerate(leaves):
		if(leaf[1] == 'ADDED'):
			realidx = i
	return realidx

#randomly change a determiner
def changedet(words, idx):
        dets = ['a', 'an', 'the']
        word = words[idx]
        newd = random.randint(0, len(dets) - 1)
        while(dets[newd] == word):
                newd = random.randint(0, len(dets) - 1)
        words[idx] = dets[newd]
        error = {'idx' : idx, 'old' : word, 'new' : dets[newd], 'mode' : "change"}
        return (words, error)

#convert a sentence in tree form to a string
def tree2sent(tree):
	leaves = tree.leaves()
	s = ""
	for l in leaves:
		s += l[0] + " "
	return s

#convert a sentence in tree for to a list of words
def tree2words(tree):
	leaves = tree.leaves()
	s = []
	for l in leaves:
		s.append(l[0])
	return s

#randomly change a preposition in words
def preperr(words, idx):
	preps = ['in', 'on', 'at', 'of', 'for', 'with', 'by']
	word = words[idx]
	newp = random.randint(0, len(preps) - 1)
	while(preps[newp] == word):
		newp = random.randint(0, len(preps) - 1)
	#words[idx] = '['+preps[newp]+']'a
	words[idx] = preps[newp]
	error = {'idx' : idx, 'old' : word, 'new' : preps[newp], 'mode' : "change"}
	return (words, error)

#randomly change the spelling of a word in words
def spellerr(words, idx):
	word = words[idx]
	w = ""
	chars = list(word)
	if(len(chars) < 4):
		return None
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

#randomly change the form of a verb in words
def verberr(words, idx):
	beverbs = ['be', 'is', 'am', 'are', 'was', 'were', 'being']
	if words[idx] in beverbs:
		return beverberr(words, idx)
	else:
		return otherverberr(words, idx)

#randomly change the form of a verb in words that is not a form of "to be"
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

#randomly change the form of a verb in words that is a form of "to be"
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

#test whether a tree represents a noun phrase
def nounphrase(tree):
	flat = tree.flatten()
	if(flat[0][1] == 'NNP'):
		return True
	return False

#compile index lists for sent, return a list of indicies where verbs, preps, nouns, and dets appear
def getpos(sent, logfile):
	verb = []
	prep = []
	noun = []
	det = []
	words = nltk.word_tokenize(sent) #sent.split()
	pos = nltk.pos_tag(words)
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

#convert a list of words to a string
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

#if a word is inserted, update indicies of index lists to reflect the change
def updateidx(lst, threshold):
	newlst = []
	for pos in lst:
		if(pos > threshold):
			pos += 1
		newlst.append(pos)
	return newlst		

#if a word is inserted, update indicies of index lists to reflect the change
def updateerridx(errs, threshold, mode):
	newlst = []
	for e in errs:
		if(e[1]['idx'] > threshold):
			if(mode == "insert"):
				e[1]['idx'] -= 1
			if(mode == "delete"):
				e[1]['idx'] += 1
		newlst.append(e)
	return newlst		

def randerr(sent):
	logfile = codecs.open("error.log", encoding='utf-8', mode='a')
	print "INITIAL:", sent
	errors = []
	alteredidx = []
	words = nltk.word_tokenize(sent) #sent.split()
	if(len(words) > 0):
		pos = getpos(sent, logfile)
		chunks = pos['chunktree']
		n = 0
		if(len(words)/3 <= 3):
			coin = random.randint(1, len(words) / 3)
		else:
			maxerrs = min(len(words)/3, 5)
			coin = random.randint(3, maxerrs)
		for n in pos['noun']:
			if(n == None):
				pos['noun'].remove(n)
		newnoun = [detidx(chunks, n) for n in pos['noun']]
		errlists = [pos['prep'], pos['det'], newnoun, range(0, len(words) - 1), pos['verb']]
		#errlists = [pos['prep'], pos['det'], pos['noun'], range(0, len(words) - 1), pos['verb']]
		errfuncs = [preperr, deterr, adddet, spellerr, verberr];
		while(coin > 0):
			#print [str(w) for w in words]
			logfile.write(list2str(words)+'\n')
			timeout = 0
			erridx = random.randint(0, len(errlists)-1)
			idxlist = errlists[erridx]
			funct = errfuncs[erridx]
			param = words
#			if(funct == adddet):
#				param = chunks
			if(len(idxlist) > 0):
				logfile.write(str(funct)+" "+str(idxlist)+'\n')
				idx = random.randint(0, len(idxlist) - 1)
			 	while(timeout < 50 and (idxlist[idx] == None or idx >= len(words))):
					timeout += 1
					idx = random.randint(0, len(idxlist) -1)
				if(timeout == 50 or idxlist[idx] == None):
					continue
				chidx = idxlist[idx]
				r = funct(param, chidx)
				if(not(r == None)):
					for lst in errlists:
						if(chidx in lst):
							lst.remove(chidx)
					r[1]['seq'] = n
					errors.append(r)
					words = r[0]
					if(r[1]['mode'] == 'delete'):
						errors = updateerridx(errors, r[1]['idx'], "delete")
						for lst in [0, 1, 2, 4]:
							errlists[lst] = updateidx(errlists[lst], r[1]['idx'])
					if(r[1]['mode'] == 'insert'):
						errors = updateerridx(errors, r[1]['idx'], "insert")
					
					coin -= 1
					n += 1
	print "FINAL: ", list2str(words)
	retval = []
	for e in errors:
		print e[1]
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
