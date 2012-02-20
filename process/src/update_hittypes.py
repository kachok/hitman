# -*- coding: utf-8 -*-
"""

India - IN

<LocaleValue>
  <Country>US</Country>
</LocaleValue>
    
    
The Locale Qualification
You can create a Qualification requirement based on the Worker's location. The Worker's location is specified by the Worker to Amazon Mechanical Turk when the Worker creates his account.
To create a Qualification requirement based on the Worker's location, specify:
a QualificationTypeId of 00000000000000000071
a Comparator of EqualTo or NotEqualTo
a LocaleValue data structure that corresponds to the desired locale
For more information on the format of a LocaleValue, see Locale data structure.

		"QualificationRequirement.2.QualificationTypeId":"00000000000000000071", # The Locale Qualification
		"QualificationRequirement.2.Comparator":"NotEqualTo",
		"QualificationRequirement.2.LocaleValue.Country":"IN", # Not India
		
		"QualificationRequirement.2.QualificationTypeId":"00000000000000000071", # The Locale Qualification
		"QualificationRequirement.2.Comparator":"EqualTo",
		"QualificationRequirement.2.LocaleValue.Country":"US", # Only US
"""



"""
Here is DB script to finish migration:

-- Update MTurk HITType IDs for old HIT Types (based on new HITTypes)
update hittypes SET mturk_hittype_id=mturk_id FROM 
(select ht1.id as type_id, ht2.mturk_hittype_id as mturk_id from hittypes ht1, hittypes ht2 
where ht1.language_id=ht2.language_id and ht1.typename='synonyms' and ht2.typename='synonyms 2'
) as ht3 where id=ht3.type_id;


-- Delete new HITTypes records from database
delete from hittypes where typename='vocabulary 2';

"""

from settings import settings
import psycopg2

from psycopg2.pool import PersistentConnectionPool
from psycopg2.pool import ThreadedConnectionPool


import mturk

from boto.mturk.connection import MTurkConnection
from boto.mturk.question import ExternalQuestion
from boto.mturk.qualification import Qualifications, PercentAssignmentsApprovedRequirement, Requirement, LocaleRequirement
#from boto.mturk.qualification_type import *

import threading

import Queue


# basic logging setup for console output
import logging
logging.basicConfig(
	format='%(asctime)s %(levelname)s %(message)s', 
	datefmt='%m/%d/%Y %I:%M:%S %p',
	level=logging.INFO)

logging.info("HIT Types migration pipeline - START")

target_language = settings["target_language"]
logging.info("target language: %s" % (target_language))


indic="bn bh or bpy pa bo ks pnb gu te hi ta kn ml mr ms".split(" ")

def do_work(conn, item):
	#get language name/HITType from the queue and modify all HITs with this type
	hittype_id=item["hittype_id"]
	new_mturk_hittype_id=item["new_mturk_hittype_id"]
	#typename=item["typename"]
		
	print item
		
	cur=conn.cursor()
	mturk_conn=mturk.conn()
	
	sql="SELECT * from hits where hittype_id=%s;"
	cur.execute(sql,(hittype_id,))
	rows=cur.fetchall()
	
	for row in rows:
		mturk_hit_id=str(row[1])
		
		print "updating ",mturk_hit_id

		try:
			mturk_conn.change_hit_type_of_hit(mturk_hit_id, new_mturk_hittype_id)
		except:
			print "error in updateing hittype of hit: ", mturk_hit_id

	sql="UPDATE hittypes SET mturk_hittype_id=%s where id=%s"
	cur.execute(sql,(new_mturk_hittype_id, hittype_id))		
	conn.commit()



def worker():
	while True:
		item = q.get()
		
		#print "thread: ", threading.currentThread().name
		
		conn=conn_pool.getconn()
		do_work(conn, item)
		q.task_done()


num_worker_threads=10

q = Queue.Queue()
mturk_conn=mturk.conn()
conn_pool=PersistentConnectionPool(num_worker_threads, num_worker_threads+5,database=settings["dbname"], user=settings["user"], host=settings["host"])

target_language = settings["target_language"]
logging.info("target language: %s" % (target_language))

conn = psycopg2.connect("dbname='"+settings["dbname"]+"' user='"+settings["user"]+"' host='"+settings["host"]+"'")

#create workers pool
for i in range(num_worker_threads):
	t = threading.Thread(target=worker)
	t.daemon = True
	t.start()


# Loop over HITs and create a job to get assignments 
cur=conn.cursor()
sql="SELECT * from hittypes ht, languages l where ht.language_id=l.id;"
cur.execute(sql)
rows = cur.fetchall()

for row in rows:
	hittype_id=str(row[0])
	mturk_hittype_id=str(row[2])
	typename=str(row[4])
	fulltypename=str(row[1])
	language_id=str(row[3])
	language_name=str(row[6])
	language_prefix=str(row[7])
	
	new_mturk_hittype_id=""
	
	if typename=="vocabulary":
		#mturk_conn.register_hit_type(title, description, reward, duration, keywords=None, approval_delay=None, qual_req=None)
		
		operation="RegisterHITType"
		description="Translate 10 words from "+language_name+" to English"
		title="Translate 10 words from "+language_name+" to English"
		keywords="translation, vocabulary, dictionary, "+language_name+", English, language, research, JHU"
		approval_delay=60*60*24*7 #7 days
		reward=0.15
		duration=60*60;

		qualifications = Qualifications()
		qualifications.add(PercentAssignmentsApprovedRequirement(comparator="GreaterThan", integer_value="85"))
		if language_prefix not in indic:
			qualifications.add(LocaleRequirement(comparator="NotEqualTo", locale="IN"))
		
		response= mturk_conn.register_hit_type(title, description, reward, duration, keywords, approval_delay, qualifications)
		new_mturk_hittype_id=response[0].HITTypeId

		item={"hittype_id":hittype_id, "mturk_hittype_id":mturk_hittype_id, "new_mturk_hittype_id":new_mturk_hittype_id, "typename":typename, "fulltypename":fulltypename}
		q.put(item)

	if typename=="synonyms":
		
	
		lang_name="English"
		operation="RegisterHITType"
		description="Do these words have the same meaning?"
		title="Do these words have the same meaning?"
		keywords="synonyms, vocabulary, dictionary, English, language, research, JHU"
		approval_delay=60*60*24*7 #7 days
		reward=0.10
		duration=60*60
		
		qualifications = Qualifications()
		qualifications.add(PercentAssignmentsApprovedRequirement(comparator="GreaterThan", integer_value="85"))
		qualifications.add(LocaleRequirement(comparator="EqualTo", locale="US"))
		
		#  qualifications.add(PercentAssignmentsApprovedRequirement(comparator="GreaterThan", integer_value="90"))
		mturk_conn=mturk.conn()
		response= mturk_conn.register_hit_type(title, description, reward, duration, keywords, approval_delay, qualifications)
		new_mturk_hittype_id=response[0].HITTypeId
		
		item={"hittype_id":hittype_id, "mturk_hittype_id":mturk_hittype_id, "new_mturk_hittype_id":new_mturk_hittype_id, "typename":typename, "fulltypename":fulltypename}
		q.put(item)

conn.close()

q.join()       # block until all tasks are done

logging.info("FINISH")

