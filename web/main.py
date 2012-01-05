from bottle import route, run, view, debug, static_file, request, response, abort

import settings
from languages import langs

import json
import psycopg2

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
    return static_file(filename, root='./static/')

@route('/static/images/:filename')
def server_static(filename):
    return static_file(filename, root='./static/images')
   
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
	
	sql="select * from vocabularyHITs vh, vocabulary v where vh.hit_id=%s and v.id=vh.word_id order by random()"
	sql="select * from vocabularyhitsdata d, vocabulary v, vocabularyhits h where h.id=d.hit_id and v.id=d.word_id and hitid=%s"
	
	print hitid
	cur.execute(sql, (hitid,))
	
	rows=cur.fetchall()
	
	words=[]
	for row in rows:
		words.append({"word_id":row[2],"word":row[5]})
	
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
		"ipinfodb_key":settings.settings["ipinfodb_key"],
		"hit_type":"vocabulary-ru",
		"assignmentid":assignmentid,
		"hitid":hitid,
		"lang":language,
		"lang_name":langs[language],
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
		"ipinfodb_key":settings.settings["ipinfodb_key"],
		"hit_type":"vocabulary-ru",
		"assignmentid":assignmentid,
		"hitid":hitid,
		"ip":get_client_ip(request),
		#"words":json.dumps(words),
		}
	return dict(params=params)

debug(True)
run(reloader=True, port=8888)
#run(host='localhost', port=8800)