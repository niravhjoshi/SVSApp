from flask import Flask,render_template,current_app
from flask.ext.bootstrap import Bootstrap
from flask.ext.mail import Mail
from flask.ext.moment import Moment
from flask.ext.sqlalchemy import SQLAlchemy
from config import config
from flask.ext.login import LoginManager
from celery import Celery
from datetime import datetime
from cryptography.fernet import Fernet
from config import config, Config
from Shared import db
from celery import Celery

bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
#db = SQLAlchemy()
celery = Celery(__name__, broker=Config.CELERY_BROKER_URL)
#This is login manager for creating flask login
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    celery.conf.update(app.config)
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    from .cam import cam as cam_blueprint
    app.register_blueprint(cam_blueprint,url_prefix='/cam')
    from .FD import FD as FD_blueprint
    app.register_blueprint(FD_blueprint,url_prefix='/FD')
    return app


