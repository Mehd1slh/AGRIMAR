from datetime import datetime
from flask import render_template, redirect, url_for, flash, request, session, jsonify
from agrimar.chat import CustomChatBot, generate_title, get_address_info_from_coords
from agrimar.forms import RegistartionForm, LoginForm, MapForm, UpdateAccountForm, RequestResetForm, ResetPasswordForm
from agrimar.model import User, Conversation, Message
from agrimar import app, db, bcrypt
from flask_login import login_user, logout_user, login_required, current_user
from PIL import Image
import secrets
import json
import os
import smtplib
from flask_babel import Babel
from flask_babel import lazy_gettext as _l, gettext


@app.route("/", methods=["GET", "POST"])
@app.route("/home", methods=["GET", "POST"])
def home():
    session.pop('lat', None)
    session.pop('lon', None)
    session.pop('full_address', None)
    session.pop('city', None)
    session.pop('region', None)
    session.pop('country', None)
    if request.method == "POST":
        session['lat'] = request.form.get("latitude")
        session['lon'] = request.form.get("longitude")
        if session['lat'] and session['lon']:
            address_info = get_address_info_from_coords(
                session['lat'], session['lon'])
            session['full_address'] = address_info['address']
            session['city'] = address_info['city']
            session['region'] = address_info['region']
            session['country'] = address_info['country']

    img_file = url_for(
        'static',
        filename='profile pics/' +
        current_user.img) if current_user.is_authenticated else url_for(
        'static',
        filename='profile pics/default.jpg')
    if 'conversation_id' in session.keys():
        session.pop('conversation_id')

    return render_template(
        'home.html',
        img_file=img_file,
        form=MapForm(),
        current_locale=get_locale())


@app.route("/get", methods=["GET", "POST"])
def chat():
    if request.method == "POST":
        user_input = request.form["msg"]
        lat = session.get('lat')
        lon = session.get('lon')
        ai_output = CustomChatBot(user_input, lat, lon)

        if current_user.is_authenticated:
            if 'conversation_id' not in session:
                cnv = Conversation(
                    title="",
                    loc_lat=lat,
                    loc_lon=lon,
                    user_id=current_user.id)
                db.session.add(cnv)
                db.session.commit()
                session['conversation_id'] = cnv.id
            else:
                cnv = Conversation.query.get(session['conversation_id'])

            user_message = Message(
                content=user_input,
                role='user',
                convo_id=cnv.id)
            ai_message = Message(
                content=ai_output,
                role='assistant',
                convo_id=cnv.id)
            db.session.add(user_message)
            db.session.add(ai_message)
            db.session.commit()

            cnv.title = generate_title(cnv)
            db.session.commit()

        return ai_output


@app.route("/users")
@login_required
def users():
    if current_user.is_authenticated:
        if current_user.privilege == 'admin':
            users = User.query.filter_by(privilege="user").all()
            return render_template('users.html', title='Users', users=users)
        else:
            flash("You Don't have the admin privilege ", 'warning')
            return redirect(url_for('home'))


@app.route('/delete_user', methods=['POST'])
@login_required
def delete_user():
    user_id = request.form.get('user_id')
    user = User.query.get(user_id)

    if user:
        db.session.delete(user)
        db.session.commit()
        flash('User has been deleted successfully', 'success')
    else:
        flash('User not found', 'danger')

    return redirect(url_for('users'))


@app.route("/chat_history")
@login_required
def chat_history():
    if current_user.is_authenticated:
        conversations = current_user.conversations
    else:
        conversations = []

    return render_template(
        'chat_history.html',
        title='Chat History',
        cnvs=conversations)


def fix_json(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()


@app.route("/conversation/<cnvid>", methods=["POST"])
def conversation_id(cnvid):
    cnv = Conversation.query.get(cnvid).messages
    return json.dumps([c.__dict__ for c in cnv], default=fix_json)


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistartionForm()
    if form.validate_on_submit():
        hash_mdp = bcrypt.generate_password_hash(form.mdp.data).decode('utf-8')
        user = User(
            username=form.username.data,
            email=form.email.data,
            mdp=hash_mdp)
        db.session.add(user)
        db.session.commit()
        flash(
            'Account created successfully! you can now log in to your account',
            'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.mdp, form.mdp.data):
            flash("Welcome Back " + user.username + "!", 'success')
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(
                url_for('home'))
        else:
            flash(
                "Login Unsuccessful, please check your email and password",
                'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    logout_user()
    session.pop('lat', None)
    session.pop('lon', None)
    session.pop('full_address', None)
    session.pop('city', None)
    session.pop('region', None)
    session.pop('country', None)
    return redirect(url_for('home'))


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    f_name, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(
        app.root_path,
        'static/profile pics',
        picture_fn)
    # Delete previous picture if it exists
    if current_user.img:
        prev_picture_path = os.path.join(
            app.root_path, 'static/profile_pics', current_user.img)
        if os.path.exists(prev_picture_path):
            os.remove(prev_picture_path)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_fn


@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.img = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    img_file = url_for('static', filename='profile pics/' + current_user.img)
    return render_template(
        'account.html',
        title='Account',
        img_file=img_file,
        form=form)


def send_reset_email(user):
    email_sender = 'fstbm.agrimar@gmail.com'
    email_password = app.config['MAIL_PASSWORD']
    email_reciever = user.email
    email_server = 'smtp.gmail.com'
    email_port = 587
    token = user.get_reset_token()
    server = smtplib.SMTP(email_server, email_port)
    server.starttls()
    server.login(email_sender, email_password)

    reset_link = url_for('reset_token', token=token, _external=True)
    msg = f'''Subject: Password Reset Request

To reset your password, visit the following link:
{reset_link}

If you did not make this request, then simply ignore this email and no changes will be made.
'''
    server.sendmail(email_sender, email_reciever, msg)
    server.quit()


@app.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password. If you didn`t find it on your inbox check the spam section', 'info')
        return redirect(url_for('login'))
    return render_template(
        'reset_request.html',
        title='Reset password',
        form=form)


@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hash_mdp = bcrypt.generate_password_hash(form.mdp.data).decode('utf-8')
        user.mdp = hash_mdp
        db.session.commit()
        flash(
            'Your password has been updated! you can now log in to your account',
            'success')
        return redirect(url_for('login'))
    return render_template(
        'reset_token.html',
        title='Reset password',
        form=form)

# for the translation of the website


babel = Babel(app)

@app.route('/setlang', methods=['GET'])
def set_language():
    lang = request.args.get('lang')
    if lang:
        app.config['BABEL_DEFAULT_LOCALE'] = lang
        return redirect(request.referrer)
    return redirect(url_for('home'))


@app.context_processor
def inject_babel():
    return dict(_=gettext)

def get_locale():
    if 'lang' in session:
        return session['lang']
    return request.accept_languages.best_match(['en', 'fr'])

@app.context_processor
def inject_locale():
    return {'get_locale': get_locale}


@app.route('/js_translations')
def js_translations():
    translations = {
        'logoutText': gettext('Logout'),
        'accountText': gettext('Account'),
        'successTitle': gettext('Success!'),
        'successText': gettext('You are registered.'),
        'validEmail': gettext('Please enter a valid email address.')
    }
    return jsonify(translations)


def get_locale():
    if 'lang' in session:
        return session['lang']
    return request.accept_languages.best_match(['en', 'fr'])

babel = Babel(app, locale_selector=get_locale)

