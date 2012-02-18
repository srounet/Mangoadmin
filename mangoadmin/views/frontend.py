#!/usr/bin/env python

from flask import Blueprint, render_template

frontend = Blueprint('frontend', __name__)


@frontend.route('/')
@frontend.route('/home')
def index():
    return render_template('home.html')
