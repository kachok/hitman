import bottle

app = bottle.Bottle()
plugin = bottle.ext.sqlite.Plugin(dbfile='/tmp/test.db')
app.install(plugin)


@app.route('/show/:item')
def show(item, db):
    row = db.execute('SELECT * from items where name=?', item).fetchone()
    if row:
        return template('showitem', page=row)
    return HTTPError(404, "Page not found")