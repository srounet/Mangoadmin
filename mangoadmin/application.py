#!/usr/bin/env python

from flask import Flask, g

from views.frontend import frontend
from views.server import server
from views.collection import collection

from pymongo import Connection

app = Flask(__name__)
app.debug = True
#change on production
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

#views
app.register_blueprint(frontend)
app.register_blueprint(server, url_prefix='/servers')
app.register_blueprint(collection, url_prefix='/collection')


@app.before_request
def before_request():
    g.db = Connection()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3300)
