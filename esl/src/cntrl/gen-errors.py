import nltk
import random
import sys
import re

def deterr(words, idx):
	pos = nltk.pos_tag(words)
	if(idx > 0 and pos[idx - 1][1] == 'DT'):
		if(random.getrandbits(1)):
			return changedet(words, idx - 1)
		else:
			#words[idx - 1] = '[]'
			error = {'idx' : idx, 'old' : words[idx - 1], 'new' : "", 'mode' : "delete"}
			words[idx - 1] = ''
			return (words, error)
	else:
		return adddet(words, idx)

def adddet(words, idx):
	dets = ['a', 'an', 'the']
	newwds = words[:idx]
	newd = dets[random.randint(0, len(dets) -1)]
	#newwds.append('['+newd+']')
	newwds.append(newd)
	newwds += words[idx:]
	error = {'idx' : idx, 'old' : "", 'new' : newd, 'mode' : "insert"}
	return (newwds, error)

def changedet(words, idx):
	dets = ['a', 'an', 'the']
	word = words[idx]
	newd = random.randint(0, len(dets) - 1)
	while(dets[newd] == word):
		newd = random.randint(0, len(dets) - 1)
	#words[idx] = '['+dets[newd]+']'
	words[idx] = dets[newd]
	error = {'idx' : idx, 'old' : word, 'new' : newd, 'mode' : "change"}
	return (words, error)

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

def spellerr(words, idx):
	word = words[idx]
	w = ""
	chars = list(word)
	if(len(chars) > 4):
		swapidx = random.randint(1, len(chars)-1)	
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
	print words, idx
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
			words[idx] = '['+m.group(1) + nend+']'
			return words
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
	errors = []
	alteredidx = []
	words = sent.split()
	if(len(words) > 0):
		pos = getpos(sent)
		verb = pos['verb']
		prep = pos['prep']
		noun = pos['noun']
		#introduce preposition errors
		timeout = 0
		print words
		if(len(prep) > 0):
			pidx = random.randint(0, len(prep) -1)
			while(timeout < 50 and pidx in alteredidx):
				timeout += 1
				pidx = random.randint(0, len(prep) -1)
			r = preperr(words, prep[pidx])
			errors.append(r)
			words = r[0]
			alteredidx.append(pidx)
		#introduce determiner errors
		timeout = 0
		print words
		if(len(noun) > 0):
			nidx = random.randint(0, len(noun) -1)
			while((timeout < 50 and nidx in alteredidx) or (nidx >= len(words))):
				timeout += 1
				nidx = random.randint(0, len(noun) -1)
			r = deterr(words, noun[nidx])
			errors.append(r)
			words = r[0]
			alteredidx.append(nidx)
		#introduce verb errors
		timeout = 0
		print words
		if(len(verb) > 0):
			vidx = random.randint(0, len(verb) -1)
			while((timeout < 50 and vidx in alteredidx) or (vidx >= len(words))):
				timeout += 1
				vidx = random.randint(0, len(verb) - 1)
			r = verberr(words, verb[vidx])
			errors.append(r)
			words = r[0]
		#introduce spelling errors
		timeout = 0
		print words
		sidx = random.randint(0, len(words) - 1)
		while((timeout < 50 and sidx in alteredidx) or (sidx >= len(words))):
				timeout += 1
				sidx = random.randint(0, len(words) -1)
		r = spellerr(words, sidx)
		errors.append(r)
		words = r[0]
	
	s = ""
	for w in words:
		s += w + " "
	return s




