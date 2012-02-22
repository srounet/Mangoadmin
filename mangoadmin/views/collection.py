#!/usr/bin/env python

from flask import Blueprint, flash, g, render_template, redirect
from pymongo import Connection
from pymongo.objectid import ObjectId
import pymongo


collection = Blueprint('collection', __name__)


@collection.route('/view/<path:server_oid>/<path:database_name>/<path:collection_name>')
def view(server_oid, database_name, collection_name):
    server = g.db['mangoadmin']['servers'].find_one({
        '_id': ObjectId(server_oid)
    })
    if not server:
        flash('Server %s not found' % server_oid, 'error')
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

@collection.route('/view/<path:server_oid>/<path:database_name>/<path:collection_name>/drop_index/<path:index_name>')
def drop_index(server_oid, database_name, collection_name, index_name):
    server = g.db['mangoadmin']['servers'].find_one({
        '_id': ObjectId(server_oid)
    })
    if not server:
        flash('Server %s not found' % server_oid, 'error')
        return redirect('/servers')
    connection = Connection(host=server['address'], port=int(server['port']))
    db = connection[database_name]
    col = db[collection_name]
    try:
        col.drop_index(index_name)
    except pymongo.errors.OperationFailure as e:
        flash(e, 'error')
    else:
        flash('Successfully deleted: %s' % index_name, 'success')
    return redirect('/collection/view/%s/%s/%s' % (server_oid, database_name, collection_name))


@collection.route('/view/<path:server_oid>/<path:database_name>/<path:collection_name>/reindex')
def reindex(server_oid, database_name, collection_name):
    server = g.db['mangoadmin']['servers'].find_one({
        '_id': ObjectId(server_oid)
    })
    if not server:
        flash('Server %s not found' % server_oid, 'error')
        return redirect('/servers')
    connection = Connection(host=server['address'], port=int(server['port']))
    db = connection[database_name]
    col = db[collection_name]
    col.reindex()
    flash('Reindexing %s, blocks all other operations and will be slow for large collections.' % collection_name, 'success')
    return redirect('/collection/view/%s/%s/%s' % (server_oid, database_name, collection_name))


@collection.route('/view/<path:server_oid>/<path:database_name>/<path:collection_name>/drop_indexes')
def drop_indexes(server_oid, database_name, collection_name):
    server = g.db['mangoadmin']['servers'].find_one({
        '_id': ObjectId(server_oid)
    })
    if not server:
        flash('Server %s not found' % server_oid, 'error')
        return redirect('/servers')
    connection = Connection(host=server['address'], port=int(server['port']))
    db = connection[database_name]
    col = db[collection_name]
    col.drop_indexes()
    flash('%s index dropped' % collection_name, 'success')
    return redirect('/collection/view/%s/%s/%s' % (server_oid, database_name, collection_name))


@collection.route('/view/<path:server_oid>/<path:database_name>/<path:collection_name>/drop')
def drop(server_oid, database_name, collection_name):
    server = g.db['mangoadmin']['servers'].find_one({
        '_id': ObjectId(server_oid)
    })
    if not server:
        flash('Server %s not found' % server_oid, 'error')
        return redirect('/servers')
    connection = Connection(host=server['address'], port=int(server['port']))
    db = connection[database_name]
    col = db[collection_name]
    col.drop()
    flash('Collection %s dropped' % collection_name, 'success')
    return redirect('/servers/view/%s' % server_oid)
