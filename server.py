"""
A Flask server that presents a minimal browsable interface for the Olin course catalog.

author: Oliver Steele <oliver.steele@olin.edu>
date  : 2017-01-18
license: MIT
"""

import os

import pandas as pd
from flask import Flask, redirect, render_template, request, url_for

DEBUG = os.environ.get('ENVIRONMENT', 'dev') == 'dev'

app = Flask(__name__)
# app.config.from_yaml(os.join(app.root_path, 'config.yml'))

ENVIRONMENT = os.environ.get('ENVIRONMENT', 'development')
app.config.from_pyfile(os.path.join('config', ENVIRONMENT + '.py'))

courses = pd.read_csv('./data/olin-courses-16-17.csv')

@app.route('/health')
def health():
    return 'ok'

@app.route('/')
def home_page():
    return render_template('index.html', areas=set(courses.course_area), contacts=set(courses.course_contact.dropna()))

@app.route('/area/<course_area>')
def area_page(course_area):
    return render_template('course_area.html', courses=courses[courses.course_area == course_area].iterrows())

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host=app.config['HOST'], port=port)
