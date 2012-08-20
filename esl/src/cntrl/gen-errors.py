import nltk
import random
import sys
import re

#randomly change, drop, or insert a determiner into words(array) at index idx
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

#randomly insert a determiner into words(array) at index idx
def adddet(words, idx):
	dets = ['a', 'a', 'a', 'an', 'the', 'the', 'the']
	newwds = words[:idx]
	newd = dets[random.randint(0, len(dets) -1)]
	#newwds.append('['+newd+']')
	newwds.append(newd)
	newwds += words[idx:]
	error = {'idx' : idx, 'old' : "", 'new' : newd, 'mode' : "insert"}
	return (newwds, error)
 
#randomly change a determiner in words(array) at index idx
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

#randomly change a preposition in words(array) at index idx
def preperr(words, idx):
	preps = ['in', 'in', 'in', 'on', 'on', 'on', 'at', 'at', 'of', 'for', 'with', 'by']
	word = words[idx]
	newp = random.randint(0, len(preps) - 1)
	while(preps[newp] == word):
		newp = random.randint(0, len(preps) - 1)
	#words[idx] = '['+preps[newp]+']'a
	words[idx] = preps[newp]
	error = {'idx' : idx, 'old' : word, 'new' : preps[newp], 'mode' : "change"}
	return (words, error)

#randomly change spelling of a word in words(array) at index idx
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

#randomly change ending of a verb in words(array) at index idx
def verberr(words, idx):
	beverbs = ['be', 'is', 'am', 'are', 'was', 'were', 'being']
	#print words, idx
	if words[idx] in beverbs:
		return beverberr(words, idx)
	else:
		return otherverberr(words, idx)

#randomly change ending of a verb that is not a form of "to be", in words(array) at index idx
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

#randomly change ending of a verb that is a form of "to be", in words(array) at index idx
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

#read through sentence and determine indecices of locations of verbs, prepositions, and nouns. returns a map containing lists of verb, prep, and noun indicies
def getpos(sent):
	verb = []
	prep = []
	noun = []
	words = sent.split()
	pos = nltk.pos_tag(words)
	for p in enumerate(pos):
		#print p[0]
		ptag = p[1][1]
		prevtag = pos[p[0]-1][1]
		if(ptag[0] == 'V'):
		#	print p[0]
			verb.append(p[0])
		if(ptag[0] == 'N'):
			if(not(prevtag == 'DT')):
				dice = random.randint(0, 2) #too many added determiners looks weird
				if(dice == 0):
					noun.append(p[0]) 
			else:
				noun.append(p[0])
		if(ptag == 'IN'):
			prep.append(p[0])
	return {"verb" : verb, "prep" : prep, "noun" : noun}

#convert a list of words into a space-separated string
def list2str(words):
	s = ""
	for w in words:
		s += w + " "
	return s

#randomly choose a preposition and introduce an error
def ruinprep(words, prep):
#	timeout = 0
	if(len(prep) > 0):
		pidx = random.randint(0, len(prep) -1)
#		while(timeout < 50 and pidx in alteredidx):
		while(pidx >= len(words)):
#			timeout += 1
			pidx = random.randint(0, len(prep) -1)
		return preperr(words, prep[pidx])
 	return None

#randomly choose a determiner and introduce an error
def ruindet(words, noun):
#	timeout = 0
	if(len(noun) > 0):
		nidx = random.randint(0, len(noun) -1)
		#while((timeout < 50 and nidx in alteredidx) or (nidx >= len(words))):
		while(nidx >= len(words)):
#			timeout += 1
			nidx = random.randint(0, len(noun) -1)
		return deterr(words, noun[nidx])
	return None

#randomly choose a verb and introduce an error
def ruinverb(words, verb)	:
#	timeout = 0
	if(len(verb) > 0):
		vidx = random.randint(0, len(verb) -1)
		#while((timeout < 50 and vidx in alteredidx) or (vidx >= len(words))):
		while(vidx >= len(words)):
#			timeout += 1
			vidx = random.randint(0, len(verb) - 1)
			return verberr(words, verb[vidx])
	return None

#randomly choose a word and introduce an error
def ruinspell(words):
#	timeout = 0
	sidx = random.randint(0, len(words) - 1)
#	while((timeout < 50 and sidx in alteredidx) or (sidx >= len(words))):
	while(sidx >= len(words)):
#			timeout += 1
			sidx = random.randint(0, len(words) -1)
	return spellerr(words, sidx)

#debug function, print verb indicies
def allverberrs(sent):
	pos = getpos(sent)
	verbs = pos['verb']
	words = sent.split()
	for v in verbs:
		print v, words[v]

#randomly introduce errors into a sentence. return the erroneous sentence and a list of the errors added
def randerr(sent):
	words = sent.split()
	num_errors = random.randint(0, len(words) / 4 )
	errors = []
	alteredidx = []
	if(len(words) < 0):
		return 
	pos = getpos(sent)
	verb = pos['verb']
	prep = pos['prep']
	noun = pos['noun']
	for i in range(0, num_errors):
		dice = random.randint(0,3)
		if(dice == 0):
			r = ruinprep(words, prep) 
			if(not(r ==None)):
				errors.append(r)
				words = r[0]
#				alteredidx.append(pidx)
		if(dice == 1):
			r = ruindet(words, noun)
			if(not(r ==None)):
				errors.append(r)
				words = r[0]
#				alteredidx.append(nidx)
		if(dice == 2):
			r = ruinverb(words, verb)
			if(not(r ==None)):
				errors.append(r)
				words = r[0]
#				alteredidx.append(vidx)
		if(dice == 3):
			r = ruinspell(words)
			if(not(r==None)):
				errors.append(r)
				words = r[0]
#				alteredidx.append(sidx)

	retval = []
	for e in errors:
		retval.append(e[1])
	return (list2str(words), retval)



#sent = "After Yuan Shikai's death in 1916, China was politically fragmented, with an internationally recognized but virtually powerless national government seated in Beijing."
#allverberrs(sent)
#getpos(sent)
#w = sent.split()
#print nltk.pos_tag(w)
