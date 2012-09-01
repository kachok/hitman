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

data_file.close()
sent_file.close()




