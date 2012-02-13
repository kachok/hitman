# -*- coding: utf-8 -*-


from settings import settings
import psycopg2

# basic logging setup for console output
import logging
logging.basicConfig(
	format='%(asctime)s %(levelname)s %(message)s', 
	datefmt='%m/%d/%Y %I:%M:%S %p',
	level=logging.INFO)

logging.info("synonyms generation pipeline - START")

target_language = settings["target_language"]
logging.info("target language: %s" % (target_language))


lang="en"


try:
	conn = psycopg2.connect("dbname='"+settings["dbname"]+"' user='"+settings["user"]+"' host='"+settings["host"]+"'")
	logging.info("successfully connected to database")
except:
	logging.error("unable to connect to the database")


cur = conn.cursor()

#getting language_id from database
sql="SELECT id from languages where prefix=%s;"
cur.execute(sql, (lang,))
rows = cur.fetchall()

lang_id=0
for row in rows:
	lang_id=str(row[0])





f=open("non_synonyms.csv","Ub")
line=f.readline()

print len(line)
print "-----"

while 1:
	line = f.readline()
	#print line
	
	if not line:
		print "break"
		break
	
	#print "lets print"
	#print line
	cur2 = conn.cursor()

	word, synonym= line.split(",")
	
	print word, synonym
	
	sql="INSERT INTO non_synonyms (word, non_synonym, language_id, corpus, active) VALUES (%s, %s, %s, %s, %s);"
	cur2.execute(sql,(word, synonym,lang_id, "random-filtered v1", "true"))

	conn.commit()
conn.close()
	

logging.info("synonyms generation pipeline - FINISH")
