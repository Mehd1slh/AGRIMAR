import os
from dotenv import load_dotenv
import matplotlib
matplotlib.use('Agg')

from flask import Flask, request, session, g
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_babel import Babel
import pymysql

# Load environment variables from .env file
load_dotenv('variables.env')

def get_locale():
    # Check if the language query parameter is set and valid
    if 'lang' in request.args:
        lang = request.args.get('lang')
        if lang in ['en', 'fr' , 'ar']:
            session['lang'] = lang
            return session['lang']
    # If not set via query, check if we have it stored in the session
    elif 'lang' in session:
        return session.get('lang')
    # Otherwise, use the browser's preferred language
    return request.accept_languages.best_match(['en', 'fr' , 'ar'])

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

# Use database configuration from .env
host = os.getenv('DB_HOST')
user = os.getenv('DB_USER')
password = os.getenv('DB_PASSWORD')
database = os.getenv('DB_NAME')

app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+mysqlconnector://{user}:{password}@{host}/{database}'

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
