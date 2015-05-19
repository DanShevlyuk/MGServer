from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.script import Manager
from flask import Flask
import os

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] ='sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_DATABASE_URI'] ='mysql://username:password@localhost/db_name'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.debug = True

from app.errors import page_not_found, service_unavailable
#app.register_error_handler(404, page_not_found)
app.register_error_handler(503, service_unavailable)

manager = Manager(app)
db = SQLAlchemy(app, session_options={
    'expire_on_commit': False
})

API_VERSION_MAJOR = 1
API_VERSION_MINOR = 0

PATH = '/api/v%s.%s/' % (API_VERSION_MAJOR, API_VERSION_MINOR)

from app import views, api
