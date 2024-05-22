from flask import Flask, session, request
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_babel import Babel
import os
app = Flask(__name__)
babel = Babel(app)
# app.config.from_object('config.Config')
app.config['SECRET_KEY'] = '092b93416967f9fec0c22c76420ed834'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://phpmyadmin:12345678@localhost/agrimar'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_PASSWORD'] = "nruj ryjk xgzj scgm"



from agrimar import routes