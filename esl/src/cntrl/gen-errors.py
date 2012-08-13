import nltk
import random
import sys
import re

def deterr(words, idx):
	pos = nltk.pos_tag(words)
	if(idx > 0 and pos[idx - 1][1] == 'DT'):
		if(random.getrandbits(1)):
			return changedet(words, idx)
		else:
			words[idx] = ""
			return words
	else:
		return adddet(words, idx)

def adddet(words, idx):
	dets = ['a', 'an', 'the']
	newwds = words[:idx]
	newwds.append('['+dets[random.randint(0, len(dets) -1)]+']')
	newwds += words[idx:]
	return newwds	

def changedet(words, idx):
	dets = ['a', 'an', 'the']
	word = words[idx]
	newd = random.randint(0, len(dets) - 1)
	while(dets[newd] == word):
		newd = random.randint(0, len(dets) - 1)
	words[idx] = '['+dets[newd]+']'
	return words

def preperr(words, idx):
	preps = ['in', 'on', 'at', 'of', 'for', 'with', 'by']
	word = words[idx]
	newp = random.randint(0, len(preps) - 1)
	while(preps[newp] == word):
		newp = random.randint(0, len(preps) - 1)
	words[idx] = '['+preps[newp]+']'
	return words

def spellerr(words, idx):
	word = words[idx]
	chars = list(word)
	if(len(chars) > 4):
		swapidx = random.randint(1, len(chars)-1)	
		tmp = chars[swapidx]
		chars[swapidx] = chars[swapidx - 1]
		chars[swapidx - 1] = tmp
		w = ""
		for c in chars:
			w += c
		words[idx] = '['+w+']'
	return words

def verberr(words, idx):
	endings = {'ing' : r'(.*)ing\Z', 'ed' : r'(.*)ed\Z', 'es' : r'(.*)es\Z', 's' : r'(.*)s\Z'}
	for end in endings:
		m = re.match(endings[end], words[idx])
		if(m): 
			nend = endings.keys()[random.randint(0, len(endings.keys()) - 1)]
			while(end == nend):
				nend = endings.keys()[random.randint(0, len(endings.keys()) - 1)]
			words[idx] = '['+m.group(1) + nend+']'
			return words
	nend = endings.keys()[random.randint(0, len(endings.keys()) - 1)]
	words[idx] = '['+words[idx] + nend+']'
	return words

def getpos(sent):
	verb = []
	prep = []
	noun = []
	words = sent.split()
	pos = nltk.pos_tag(words)
	for p in enumerate(pos):
		ptag = p[1][1]
		if(ptag[0] == 'V'):
			verb.append(p[0])
		if(ptag[0] == 'N'):
			noun.append(p[0])
		if(ptag == 'IN'):
			prep.append(p[0])
	return {"verb" : verb, "prep" : prep, "noun" : noun}

def randerr(sent):
	words = sent.split()
	if(len(words) > 0):
		pos = getpos(sent)
		verb = pos['verb']
		prep = pos['prep']
		noun = pos['noun']
		sidx = random.randint(0, len(words) - 1)
		ws = spellerr(words, sidx)
		words = ws
		if(len(prep) > 0):
			pidx = random.randint(0, len(prep) -1)
			words = preperr(words, prep[pidx])
		if(len(verb) > 0):
			vidx = random.randint(0, len(verb) -1)
			words = verberr(words, verb[vidx])
	s = ""
	for w in words:
		s += w + " "
	return s

ifile = open(sys.argv[1])
for s in ifile.readlines():
	print s.strip('\n')
	print randerr(s.strip('\n'))
	print




