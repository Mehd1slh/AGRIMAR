from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed 
from wtforms import StringField, PasswordField, SubmitField, BooleanField, FloatField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from agrimar.model import User
from agrimar import app , get_locale
from flask_login import current_user
from flask_babel import _,lazy_gettext as _l, gettext

@app.context_processor
def inject_babel():
    return dict(_=gettext)

@app.context_processor
def inject_locale():
    # This makes the function available directly, allowing you to call it in the template
    return {'get_locale': get_locale}

class RegistrationForm(FlaskForm):
    username = StringField(_l(' Username '), validators=[DataRequired(), Length(min=3, max=20)])
    email = StringField(_l(' Email '), validators=[DataRequired(), Email()])
    mdp = PasswordField(_l(' Password '), validators=[DataRequired(), Length(min=6, max=15)])
    con_mdp = PasswordField(_l(' Confirm Password '), validators=[DataRequired(), Length(min=6, max=15), EqualTo('mdp')])
    submit = SubmitField(_l(' Sign Up '))

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError(_(' That username is taken, please choose another one '))

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError(_(' That email is taken, please choose another one '))
    

class LoginForm(FlaskForm):
    email = StringField(_l(' Email '), validators=[DataRequired(), Email()])
    mdp = PasswordField(_l(' Password '), validators=[DataRequired(), Length(min=6, max=15)])
    remember = BooleanField(_l(' Remember Me '))
    submit = SubmitField(_l(' Login '))


class MapForm(FlaskForm):
    lat = FloatField(_l(' Latitude '), validators=[DataRequired()])
    lon = FloatField(_l(' Longitude '), validators=[DataRequired()])
    submit = SubmitField(_l(' Submit '))
    

class UpdateAccountForm(FlaskForm):
    username = StringField(_l(' Username '), validators=[DataRequired(), Length(min=3, max=20)])
    email = StringField(_l(' Email '), validators=[DataRequired(), Email()])
    picture = FileField(_l(' Update Profile Picture '), validators=[FileAllowed(['jpg', 'png', 'jpeg', 'jfif'])])
    submit = SubmitField(_l(' Update '))

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError(_(' That username is taken, please choose another one '))

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError(_(' That email is taken, please choose another one '))
            
class RequestResetForm(FlaskForm):
    email = StringField(_l(' Email '), validators=[DataRequired(), Email()])
    submit = SubmitField(_l(' Request Password Reset '))

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError(_(' There is no account with that email. You should register first '))
    
class ResetPasswordForm(FlaskForm):
    mdp = PasswordField(_l(' Password '), validators=[DataRequired(), Length(min=6, max=15)])
    con_mdp = PasswordField(_l(' Confirm Password '), validators=[DataRequired(), Length(min=6, max=15), EqualTo('mdp')])
    submit = SubmitField(_l(' Reset Password '))
