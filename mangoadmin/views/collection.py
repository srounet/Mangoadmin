#!/usr/bin/env python

from flask import Blueprint, g, render_template
from pymongo import Connection
from pymongo.objectid import ObjectId


collection = Blueprint('collection', __name__)


@collection.route('/view/<path:server_oid>/<path:database_name>/<path:collection_name>')
def view(server_oid, database_name, collection_name):
    server = g.db['mangoadmin']['servers'].find_one({
        '_id': ObjectId(server_oid)
    })
    if not server:
        flash('Server %s not found' % server_oid)
        return redirect('/servers')
    connection = Connection(host=server['address'], port=int(server['port']))
    db = connection[database_name]
    col = db[collection_name]
    indexes = col.index_information()
    stats = db.command('collstats', collection_name)
    documents = col.find().limit(5)
    return render_template(
        'collection_view.html',
        database_name=database_name,
        collection_name=collection_name,
        indexes=indexes,
        stats=stats,
        server_oid=server_oid,
        documents=documents
    )
