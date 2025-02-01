import os
from dotenv import load_dotenv
import matplotlib
matplotlib.use('Agg')

from flask import Flask, request, session, g
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_babel import Babel

# Load environment variables from .env file
load_dotenv('variables.env')

def get_locale():
    if 'lang' in request.args:
        lang = request.args.get('lang')
        if lang in ['en', 'fr', 'ar']:
            session['lang'] = lang
            return session['lang']
    elif 'lang' in session:
        return session.get('lang')
    return request.accept_languages.best_match(['en', 'fr', 'ar'])

def get_timezone():
    user = getattr(g, 'user', None)
    if user is not None:
        return user.timezone

app = Flask(__name__)

# Use secret key from .env
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

# Configuring Babel
babel = Babel(app, locale_selector=get_locale, timezone_selector=get_timezone)
app.config['BABEL_DEFAULT_LOCALE'] = 'en'
app.config['BABEL_TRANSLATION_DIRECTORIES'] = './translations'

# Database configuration (PostgreSQL)
host = os.getenv('DB_HOST')
port = os.getenv('DB_PORT', '5432')  # Default PostgreSQL port
user = os.getenv('DB_USER')
password = os.getenv('DB_PASSWORD')
database = os.getenv('DB_NAME')

app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://root:jVaerQkrmjw8LxzT7AgojcaBiQPAVYVF@dpg-cuep5mtumphs73ag0g10-a/agrimar'

# Importing SQLAlchemy with Matplotlib
import matplotlib.pyplot as plt
db = SQLAlchemy(app)

bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

# Use mail password from .env
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')

from agrimar import routes
