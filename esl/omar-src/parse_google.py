import re
import os
import csv
import nltk
import json
import urllib2
import controls
import httplib2
from httplib2 import Http
from nltk import tokenize
from bs4 import BeautifulSoup
from nltk.corpus import PlaintextCorpusReader

def get_sub_directories(directory):
        subdirs = [d for d in os.listdir(directory) if os.path.isdir(directory+'/'+d)]
        return subdirs

def get_all_files(directory):
        files = [directory+'/'+f for f in os.listdir(directory)]
        return files

def get_link_map(filelist):
	linkmap = {}
	for f in filelist:
		for line in open(f).readlines():
			fields = line.split('\t')
			if(len(fields) > 1):
				key = fields[0].replace('"', '')
				if(not(key in linkmap)):
					linkmap[key] = []
				for link in fields[1:]:
					linkmap[key].append(link.strip('"'))
	return linkmap

def get_sents_by_term(links):
	standard = re.compile('^(\w*\.*\,*\?*)*$')
	tok = nltk.tokenize.PunktSentenceTokenizer()
	sents = {}
	for terms in links:
		print terms
		sents[terms] = []
		for link in links[terms]:
			print link
			link = link.strip('"')
			if(not(re.match('^(\s)*$', link))):
	        		try:
					content = urllib2.urlopen(link)
					page = BeautifulSoup(content.read())
					raw = tok.tokenize(page.get_text())
					for sent in raw:
						print sent
					#	if(re.match(standard, sent)):
						sents[terms].append(sent)	
				except:
					continue
	return sents

if __name__ == '__main__':
	links = get_link_map(get_all_files('caches'))
	keys = links.keys()[:5]
	fewerlinks = {k : links[k] for k in keys}
	print get_sents_by_term(fewerlinks)
