from flask import Flask, session, request
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_babel import Babel, locale_selector
from flask_babel import _

app = Flask(__name__)
app.config['SECRET_KEY'] = '092b93416967f9fec0c22c76420ed834'
app.config['BABEL_DEFAULT_LOCALE'] = 'fr'
app.config['BABEL_TRANSLATION_DIRECTORIES'] = './translations'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://phpmyadmin:12345678@localhost/agrimar'

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_PASSWORD'] = "nruj ryjk xgzj scgm"

babel = Babel(app)
@locale_selector
def get_locale():
    return session.get('lang', request.accept_languages.best_match(['en', 'fr', 'ar']))


babel.init_app(app, locale_selector=get_locale)

from agrimar import routes
