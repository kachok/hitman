from bottle import route, run, view, debug, static_file, request, response

import settings

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
    
@route('/')
def index():
    return '<b>Hello World! reload %s</b>' % (get_client_ip(request))

# simple JSON webservice to return client IP address
@route('/ip')
def index():
    response.content_type = 'application/json'
    return {"ip":get_client_ip(request)}


@route('/main')
@view('main')
def main(name='World reload'):
    params={
        "ipinfodb_key":settings.settings["ipinfodb_key"],
		"hit_type":"vocabulary-ru"
    }
    return dict(params=params)

debug(True)
run(reloader=True, port=8880)
#run(host='localhost', port=8800)