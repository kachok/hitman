from bottle import route, run, view, debug, static_file, request, response, abort

from settings import settings

from langlib import get_languages_list, get_languages_properties

import json
import psycopg2


target_language = settings["target_language"]

langs=[] #list of languages represented as wikipedia prefixes e.g. xx - xx.wikipedia.org
langs=get_languages_list(settings["languages_file"], target_language)

langs_properties={} #list of languages' properties (e.g. LTR vs RTL script, non latin characters, etc) 
langs_properties=get_languages_properties(settings["languages_properties_file"], target_language)



# get IP address, including handling of proxies
# based on http://stackoverflow.com/questions/4581789/how-do-i-get-user-ip-address-in-django
def get_client_ip(request):
  x_forwarded_for = request.environ.get('HTTP_X_FORWARDED_FOR')
  if x_forwarded_for:
    ip = x_forwarded_for.split(',')[0] #TODO: check if client IP is at the beginning of the list or at the end ???
  else:
    ip = request.environ.get('REMOTE_ADDR')
  return ip

# handling of all static files (flat files in /static folder)
@route('/static/:filename')
def server_static(filename):
    return static_file(filename, root=settings["code_root"]+'/static/')

@route('/static/images/:path#.+#')
def server_static(path):
    return static_file(path, root=settings["code_root"]+'/static/images/')
   
@route('/')
def index():
    return '<b>Hello World!'

# simple JSON webservice to return client IP address
@route('/ip')
def index():
    response.content_type = 'application/json'
    return {"ip":get_client_ip(request)}

# simple JSON webservice to return words for specific HITId
@route('/words')
def index():
	
	hitid=request.query.hitId
	
	try:
		conn = psycopg2.connect("dbname='hitman' user='dkachaev' host='localhost'")
	except:
		pass
		
	cur = conn.cursor()
	
	#sql="select * from vocabularyHITs vh, vocabulary v where vh.hit_id=%s and v.id=vh.word_id order by random()"
	sql="select * from vocabularyhitsdata d, vocabulary v, vocabularyhits h where h.id=d.hit_id and v.id=d.word_id and h.mturk_hit_id=%s"
	
	print hitid
	cur.execute(sql, (hitid,))
	
	rows=cur.fetchall()
	
	words=[]
	for row in rows:
		word_id=str(row[1]).zfill(9)+"0"
		word=str(row[6])
		words.append({"word_id":word_id,"word":word})


	sql="select * from dictionary d, vocabularyhits h where d.language_id=h.language_id and h.mturk_hit_id=%s order by random() limit 2"

	print hitid
	cur.execute(sql, (hitid,))

	rows=cur.fetchall()

	for row in rows:
		word_id=str(row[0]).zfill(9)+"1"
		word=str(row[1]).lower()
		words.append({"word_id":word_id,"word":word})

	conn.close()


	response.content_type = 'application/json'
	return {"words":words}

@route('/notifications')
def notifications():

	return None



@route('/hits/vocabulary/<language>')
@view('vocabulary')
def vocabulary_hit(language):
    #when page is rendered, get assignmentID/hitID and attach it to displayed results

	assignmentid=request.query.assignmentId
	hitid=request.query.hitId
	
	params={
		"ipinfodb_key":settings["ipinfodb_key"],
		"hit_type":"vocabulary-ru",
		"assignmentid":assignmentid,
		"hitid":hitid,
		"lang":language,
		"lang_name":langs_properties[language]["name"],
		"ip":get_client_ip(request),
		#"words":json.dumps(words),
		}
	return dict(params=params)

@route('/hits/synonyms')
@view('synonyms')
def synonyms_hit():
    #when page is rendered, get assignmentID/hitID and attach it to displayed results

	assignmentid=request.query.assignmentId
	hitid=request.query.hitid

	params={
		"ipinfodb_key":settings["ipinfodb_key"],
		"hit_type":"vocabulary-ru",
		"assignmentid":assignmentid,
		"hitid":hitid,
		"ip":get_client_ip(request),
		#"words":json.dumps(words),
		}
	return dict(params=params)

#debug(True)
#run(reloader=True, port=8889)
#run(host='localhost', port=8800)