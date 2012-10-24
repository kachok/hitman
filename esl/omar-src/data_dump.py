"""
Script for pulling all data out of esl data tables and dumping it into csv format
"""

import psycopg2
import sys
import os
import datetime
import argparse

def format_csv(string):
    """ Replaces special characters used by comma separated value (CSV) files
    with their HTML equivalents.
    """
    string = string.strip()
    string = string.replace('\n', ' ')
    string = string.replace('&', "&amp;")
    string = string.replace(',', "&#44;")
    string = string.replace('>', "&gt;")
    string = string.replace('<', "&lt;")
    string = string.replace('"', "&quot;")
    string = string.replace("'", "&#39;")
    return string

parser = argparse.ArgumentParser(description='Get buffered assignments and results from Mechanical Turk into database',epilog="And that's how you'd do it")

parser.add_argument('--settings', default='settings', help='filename of settings file to use: settings (.py) will be used by default')
parser.add_argument('--level',default='INFO', choices=["DEBUG","INFO","WARNING","ERROR","CRITICAL"],help='logging level: e.g. DEBUG, INFO, etc.')

args = parser.parse_args()

try:
        settings_module = __import__(args.settings) #, globals={}, locals={}, fromlist=[], level=-1
        settings=settings_module.settings
except ImportError:
        import sys
        sys.stderr.write("Error: Can't find the file '%r.py' in the directory containing %r.\n" % (args.settings, args.settings))
        sys.exit(1)

dirname = "data-dump-"+str(datetime.datetime.now().strftime("%Y-%m-%d_%H:%M"))
os.mkdir(dirname)
sent_file = open(dirname+"/sent_ids", "w")
data_file = open(dirname+"/edit_data", "w")
worker_file = open(dirname+"/worker_data", "w")
ass_file = open(dirname+"/assign_data", "w") #haha. ass file.
eslass_file = open(dirname+"/eslassign_data", "w") #haha. ass file.
control_file = open(dirname+"/cntrl_data", "w")
hit_file = open(dirname+"/hit_data", "w")
hitdata_file = open(dirname+"/hitdata_data", "w")
corrsent_file = open(dirname+"/corrsent_data", "w")
grade_file = open(dirname+"/grade_data", "w")
rej_file = open(dirname+"/rejhit_data", "w")

conn = psycopg2.connect("dbname='"+settings["esl_dbname"]+"' user='"+settings["user"]+"' host='"+settings["host"]+"'")

cur=conn.cursor()
sql="SELECT * from esl_edits;"
cur.execute(sql)
rows = cur.fetchall()

cols = cur.description
print cols
for col in cols:
	data_file.write(col[0]+", ")
data_file.write("\n")

for row in rows:
	for e in row:
		data_file.write(format_csv(str(e).strip())+", ")
	data_file.write("\n")
dt = datetime.datetime.now()
#data_file.write(str(dt))
data_file.write('\n')

sql="SELECT * from esl_sentences;"
cur.execute(sql)
rows = cur.fetchall()

cols = cur.description
print cols
for col in cols:
	sent_file.write(col[0]+", ")
sent_file.write("\n")

for row in rows:
	for e in row:
		sent_file.write(format_csv(str(e).strip())+", ")
	sent_file.write("\n")
dt = datetime.datetime.now()
#sent_file.write(str(dt))

sql="SELECT * from esl_corrected_sents;"
cur.execute(sql)
rows = cur.fetchall()

cols = cur.description
print cols
for col in cols:
        corrsent_file.write(col[0]+", ")
corrsent_file.write("\n")

for row in rows:
        for e in row:
                corrsent_file.write(format_csv(str(e).strip())+", ")
        corrsent_file.write("\n")
dt = datetime.datetime.now()
#sent_file.write(str(dt))


sql="SELECT * from esl_workers;"
cur.execute(sql)
rows = cur.fetchall()

cols = cur.description
print cols
for col in cols:
	worker_file.write(col[0]+", ")
worker_file.write("\n")

for row in rows:
	for e in row:
		worker_file.write(format_csv(str(e).strip())+", ")
	worker_file.write("\n")
dt = datetime.datetime.now()

sql="SELECT * from assignments;"
cur.execute(sql)
rows = cur.fetchall()

cols = cur.description
print cols
for col in cols:
	ass_file.write(col[0]+", ")
ass_file.write("\n")

for row in rows:
	for e in row:
		ass_file.write(format_csv(str(e).strip())+", ")
	ass_file.write("\n")
dt = datetime.datetime.now()

sql="SELECT * from esl_assignments;"
cur.execute(sql)
rows = cur.fetchall()

cols = cur.description
print cols
for col in cols:
        eslass_file.write(col[0]+", ")
eslass_file.write("\n")

for row in rows:
        for e in row:
                eslass_file.write(format_csv(str(e).strip())+", ")
        eslass_file.write("\n")
dt = datetime.datetime.now()


sql="SELECT * from hits;"
cur.execute(sql)
rows = cur.fetchall()

cols = cur.description
print cols
for col in cols:
	hit_file.write(col[0]+", ")
hit_file.write("\n")

for row in rows:
	for e in row:
		hit_file.write(format_csv(str(e).strip())+", ")
	hit_file.write("\n")
dt = datetime.datetime.now()

sql="SELECT * from esl_hits_data;"
cur.execute(sql)
rows = cur.fetchall()

cols = cur.description
print cols
for col in cols:
	hitdata_file.write(col[0]+", ")
hitdata_file.write("\n")

for row in rows:
	for e in row:
		hitdata_file.write(format_csv(str(e).strip())+", ")
	hitdata_file.write("\n")
dt = datetime.datetime.now()

sql="SELECT * from esl_controls;"
cur.execute(sql)
rows = cur.fetchall()

cols = cur.description
print cols
for col in cols:
	control_file.write(col[0]+", ")
control_file.write("\n")

for row in rows:
	for e in row:
		control_file.write(format_csv(str(e).strip())+", ")
	control_file.write("\n")
dt = datetime.datetime.now()

sql="SELECT * from esl_grades;"
cur.execute(sql)
rows = cur.fetchall()

cols = cur.description
print cols
for col in cols:
        grade_file.write(col[0]+", ")
grade_file.write("\n")

for row in rows:
        for e in row:
                grade_file.write(format_csv(str(e).strip())+", ")
        grade_file.write("\n")
dt = datetime.datetime.now()

sql="SELECT * from esl_rejected_hits;"
cur.execute(sql)
rows = cur.fetchall()

cols = cur.description
print cols
for col in cols:
        rej_file.write(col[0]+", ")
rej_file.write("\n")

for row in rows:
        for e in row:
                rej_file.write(format_csv(str(e).strip())+", ")
        rej_file.write("\n")
dt = datetime.datetime.now()

data_file.close()
sent_file.close()
worker_file.close()
ass_file.close()
hit_file.close()
hitdata_file.close()
control_file.close()
