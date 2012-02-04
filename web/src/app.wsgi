import os
import bottle

from settings import settings

# Change working directory so relative paths (and template lookup) work again
os.chdir(os.path.dirname(settings["root"]))

from bottle import route, run
from main import *

bottle.TEMPLATE_PATH.insert(0,settings["code_root"])

@route('/hello')
def hello():
	return "Hello World!"

# ... build or import your bottle application here ...# Do NOT use bottle.run() with mod_wsgi
application = bottle.default_app()