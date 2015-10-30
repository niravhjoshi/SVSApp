from flask.ext.sqlalchemy import SQLAlchemy
from flask import Flask,render_template

#app = Flask(__name__)
#db = SQLAlchemy(app,session_options={'expire_on_commit':False})
db = SQLAlchemy()