import sys
import mturk
from settings import settings
import wikilanguages
import psycopg2
from itertools import islice, chain
import uuid
import random
import controls
import codecs
import generrors
import argparse
import re

f = open('controls.goog.out')
outpos = open('foundids', 'w')
outneg = open('notfoundids', 'w')
foundurd = 0
foundbbc = 0
notfoundurd = 0
notfoundbbc = 0

found = []
notfound = []

conn = psycopg2.connect("dbname='"+settings["esl_dbname"]+"' user='"+settings["user"]+"' host='"+settings["host"]+"'")
cur = conn.cursor()

lines = f.readlines()

print len(lines)

for i,line in enumerate(lines):
	if(re.match('^(\d*\s*)*$',line)):
		docs = line.split()
		for d in docs:
			sql="SELECT doc_id from esl_sentences where id=%s;"
        		cur.execute(sql, (d,))
        		rows = cur.fetchall()
			if((i+1 == len(lines)) or re.match('^(\d*\s*)*$',lines[i+1])):
				outneg.write(str(rows[0]) + '\n') 
				if(rows[0][0][0] == 'u'):
					notfoundurd += 1
				else:
					notfoundbbc +=1
			else:
				outpos.write(str(rows[0]) + '\n') 
				j = i+1
				while(not(re.match('^(\d*\s*)*$',lines[j]))):
					outpos.write(str(lines[j]) + '\n') 
					j = j+1
				if(rows[0][0][0] == 'u'):
					foundurd += 1
				else:
					foundbbc +=1
outneg.write('BBC: '+str(notfoundbbc)+' URD: '+str(notfoundurd))
outpos.write('BBC: '+str(foundbbc)+' URD: '+str(foundurd))

		
