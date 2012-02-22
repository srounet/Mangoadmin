#!/usr/bin/env python

from flask import Blueprint, flash, g, redirect, render_template, request
from pymongo import Connection
from pymongo.objectid import ObjectId

server = Blueprint('server', __name__)


@server.route('/')
def index():
    servers = g.db['mangoadmin']['servers'].find()
    return render_template('servers.html', servers=servers)


@server.route('/add', methods=['POST'])
def add():
    f = request.form
    if not f.get('address'):
        flash('Missing mongo server "Address".', 'error')
        return redirect('/servers')
    if not f.get('name'):
        flash('Missing mongo server "Name".', 'error')
        return redirect('/servers')
    name = f.get('name')
    address = f.get('address')
    port = f.get('port') or '27017'
    username = f.get('username')
    password = f.get('password')
    g.db['mangoadmin']['servers'].save({
        'address': address,
        'name': name,
        'port': port,
        'username': username,
        # XXX Salt password
        'password': password,
    })
    return redirect('/servers')


@server.route('/remove/<path:server_oid>')
def remove(server_oid):
    g.db['mangoadmin']['servers'].remove({
        '_id': ObjectId(server_oid)
    })
    flash('Server %s deleted' % server_oid, 'success')
    return redirect('/servers')


@server.route('/view/<path:server_oid>')
def view(server_oid):
    server = g.db['mangoadmin']['servers'].find_one({
        '_id': ObjectId(server_oid)
    })
    if not server:
        flash('Server %s not found' % server_oid, 'error')
        return redirect('/servers')
    connection = Connection(host=server['address'], port=int(server['port']))
    server_info = connection.server_info()
    databases = {
        database: {
            collection : {
                'count': connection[database][collection].count(),
                'index_count': len(connection[database][collection].index_information().keys()),
            } for collection in connection[database].collection_names() if not collection == 'system.indexes'
        }
        for database in connection.database_names()
    }
    return render_template(
        'server_view.html',
        server=server,
        server_info=server_info,
        databases=databases
   )

@server.route('/drop/<path:server_oid>/<path:database_name>')
def drop_databae(server_oid, database_name):
    server = g.db['mangoadmin']['servers'].find_one({
        '_id': ObjectId(server_oid)
    })
    if not server:
        flash('Server %s not found' % server_oid, 'error')
        return redirect('/servers')
    connection = Connection(host=server['address'], port=int(server['port']))
    connection.drop_database(database_name)
    flash('%s dropped.' % database_name, 'success')
    return redirect('/servers/view/%s' % server_oid)
