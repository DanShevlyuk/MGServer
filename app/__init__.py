from flask.ext.bootstrap import Bootstrap
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.script import Manager
from flask import Flask
import os

app = Flask(__name__)

app.debug = True
manager = Manager(app)

from app import views
