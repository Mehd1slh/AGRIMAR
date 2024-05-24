from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed 
from wtforms import StringField, PasswordField, SubmitField, BooleanField, FloatField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from agrimar.model import User
from flask_login import current_user
from flask_babel import _

class RegistrationForm(FlaskForm):
    username = StringField(_('Username'), validators=[DataRequired(), Length(min=3, max=20)])
    email = StringField(_('Email'), validators=[DataRequired(), Email()])
    mdp = PasswordField(_('Password'), validators=[DataRequired(), Length(min=6, max=15)])
    con_mdp = PasswordField(_('Confirm Password'), validators=[DataRequired(), Length(min=6, max=15), EqualTo('mdp')])
    submit = SubmitField(_('Sign Up'))

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError(_('That username is taken, please choose another one'))

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError(_('That email is taken, please choose another one'))
    

class LoginForm(FlaskForm):
    email = StringField(_('Email'), validators=[DataRequired(), Email()])
    mdp = PasswordField(_('Password'), validators=[DataRequired(), Length(min=6, max=15)])
    remember = BooleanField(_('Remember Me'))
    submit = SubmitField(_('Login'))


class MapForm(FlaskForm):
    lat = FloatField(_('Latitude'), validators=[DataRequired()])
    lon = FloatField(_('Longitude'), validators=[DataRequired()])
    submit = SubmitField(_('Submit'))
    

class UpdateAccountForm(FlaskForm):
    username = StringField(_('Username'), validators=[DataRequired(), Length(min=3, max=20)])
    email = StringField(_('Email'), validators=[DataRequired(), Email()])
    picture = FileField(_('Update Profile Picture'), validators=[FileAllowed(['jpg', 'png', 'jpeg', 'jfif'])])
    submit = SubmitField(_('Update'))

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError(_('That username is taken, please choose another one'))

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError(_('That email is taken, please choose another one'))
            
class RequestResetForm(FlaskForm):
    email = StringField(_('Email'), validators=[DataRequired(), Email()])
    submit = SubmitField(_('Request Password Reset'))

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError(_('There is no account with that email. You should register first'))
    
class ResetPasswordForm(FlaskForm):
    mdp = PasswordField(_('Password'), validators=[DataRequired(), Length(min=6, max=15)])
    con_mdp = PasswordField(_('Confirm Password'), validators=[DataRequired(), Length(min=6, max=15), EqualTo('mdp')])
    submit = SubmitField(_('Reset Password'))
