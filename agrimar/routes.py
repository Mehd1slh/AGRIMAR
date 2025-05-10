from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from flask import render_template, redirect, url_for, flash, send_file, request, session, jsonify , json
from agrimar.chat import CustomChatBot, generate_title, prepare_prompt, transcribe_audio_with_gpt4o
from agrimar.api_data import get_address_info_from_coords, get_soil_data, get_weather_data ,format_soil_summary , format_weather_summary
from agrimar.forms import RegistrationForm, LoginForm, MapForm, UpdateAccountForm, RequestResetForm, ResetPasswordForm
from agrimar.model import User, Conversation, Message, PDF
from agrimar.report import add_weather_properties_pages ,add_soil_report_pages , send_report_email
from agrimar import app, db, bcrypt , get_locale , babel
from flask_login import login_user, logout_user, login_required, current_user
from PIL import Image
import secrets, os, smtplib , uuid
from flask_babel import Babel, _,lazy_gettext 
from dotenv import load_dotenv


pdf = PDF()
executor = ThreadPoolExecutor()
load_dotenv('variables.env')

# ✅ global temporary store
full_soil_data_store = {}
def fetch_full_soil_data_async(lat, lon, user_id):
    from agrimar.api_data import get_soil_data
    try:
        full_soil_data = get_soil_data(lat, lon, format="full")
        full_soil_data_store[user_id] = full_soil_data
        print(f"[INFO] Full soil data fetched for user {user_id}")
    except Exception as e:
        print(f"[ERROR] Full soil data fetch failed for user {user_id}: {e}")


@app.route('/setlang')
def setlang():
    lang = request.args.get('lang', 'en')
    session['lang'] = lang
    return redirect(request.referrer)

@app.context_processor
def inject_babel():
    return dict(_=lazy_gettext)

@app.context_processor
def inject_locale():
    # This makes the function available directly, allowing you to call it in the template
    return {'get_locale': get_locale}


@app.route("/", methods=["GET", "POST"])
@app.route("/home", methods=["GET", "POST"])
def home():
    session.pop('lat', None)
    session.pop('lon', None)
    session.pop('full_address', None)
    session.pop('city', None)
    session.pop('region', None)
    session.pop('country', None)
    soil_data = {}
    soil_summary = ""
    weather_data = {}
    weather_summary = ""
    if request.method == "POST":
        session['lat'] = request.form.get("latitude")
        session['lon'] = request.form.get("longitude")
        if session['lat'] and session['lon']:
            with ThreadPoolExecutor() as executor:
                future_address = executor.submit(get_address_info_from_coords, session['lat'], session['lon'])
                future_weather = executor.submit(get_weather_data, session['lat'], session['lon'])
                future_soil = executor.submit(get_soil_data, session['lat'], session['lon'])
                if current_user.is_authenticated:
                    executor.submit(fetch_full_soil_data_async, session['lat'], session['lon'], current_user.id)
                try:
                    address_info = future_address.result()
                except Exception as e:
                    flash(f"Geocoding error: {str(e)}", "danger")
                    address_info = {'address': 'Unknown', 'city': '', 'region': '', 'country': ''}

                try:
                    weather_data = future_weather.result()
                    weather_summary = format_weather_summary(weather_data)
                except Exception as e:
                    flash(f"Weather data error: {str(e)}", "danger")
                    weather_summary = "Weather data unavailable."

                try:
                    soil_data = future_soil.result()
                    soil_summary = format_soil_summary(soil_data)
                except Exception as e:
                    flash(f"Soil data error: {str(e)}", "danger")
                    soil_summary = "Soil data unavailable."

            # store in session
            session['full_address'] = address_info['address']
            session['city'] = address_info['city']
            session['region'] = address_info['region']
            session['country'] = address_info['country']
            session['weather_data']=weather_data
            session['weather_summary'] = weather_summary
            session['soil_data']=soil_data
            session['soil_summary'] = soil_summary

    img_file = url_for('static', filename='profile_pics/' + current_user.img) if current_user.is_authenticated else url_for('static', filename='profile_pics/default.jpg')
    if 'conversation_id' in session.keys():
        session.pop('conversation_id')

    return render_template('home.html', img_file=img_file, form=MapForm() , current_locale=get_locale())

@app.route("/send_audio", methods=["POST"])
def send_audio():
    audio_file = request.files['audio']
    uploads_dir = os.path.join(app.root_path, 'uploads')
    os.makedirs(uploads_dir, exist_ok=True)

    filename = f"{uuid.uuid4()}.webm"
    audio_path = os.path.join(uploads_dir, filename)
    audio_file.save(audio_path)

    transcribed_text = transcribe_audio_with_gpt4o(audio_path, language="en")
    os.remove(audio_path)

    if not transcribed_text:
        return jsonify({'error': 'Sorry, I could not understand the audio.'}), 400

    return jsonify({'transcribed_text': transcribed_text})


@app.route("/get", methods=["GET", "POST"])
def chat():
    if request.method == "POST":
        user_input = request.form["msg"]
        lat = session.get('lat')
        lon = session.get('lon')
        if all([session.get('full_address'), session.get('weather_summary'), session.get('soil_summary')]):
            prompt_context = prepare_prompt(
                session['full_address'],
                session['weather_summary'],
                session['soil_summary']
            )
        else:
            # Default general prompt
            prompt_context = (
                "You are an agriculture expert answering farmers' questions "
                "such as crop types, weather advice, and best agricultural practices. "
                "- If users ask about infos that require their adress or weather data or soil data , ask them to fill their coords in the website map ui."
            )
        ai_output = CustomChatBot(user_input, prompt_context)

        if current_user.is_authenticated:
            if 'conversation_id' not in session:
                cnv = Conversation(title="", loc_lat=lat, loc_lon=lon, user_id=current_user.id)
                db.session.add(cnv)
                db.session.commit()
                session['conversation_id'] = cnv.id
            else:
                cnv = Conversation.query.get(session['conversation_id'])

            user_message = Message(content=user_input, role='user', convo_id=cnv.id)
            ai_message = Message(content=ai_output, role='assistant', convo_id=cnv.id)
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
            return render_template('users.html', title=_('Users'), users=users, current_locale=session.get('lang'))
        else:
            flash(_("You Don't have the admin privilege"), 'warning')
            return redirect(url_for('home'))
        
@app.route('/delete_user', methods=['POST'])
@login_required
def delete_user():
    user_id = request.form.get('user_id')
    user = User.query.get(user_id)
    
    if user:
        db.session.delete(user)
        db.session.commit()
        flash(_('User has been deleted successfully'), 'success')
    else:
        flash(_('User not found'), 'danger')
    
    return redirect(url_for('users'))

@app.route("/chat_history")
@login_required
def chat_history():
    if current_user.is_authenticated:
        conversations = current_user.conversations
    else:
        conversations = []

    return render_template('chat_history.html', title=_('Chat History'), cnvs=conversations, current_locale=session.get('lang'))

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
    form = RegistrationForm()
    if form.validate_on_submit():
        hash_mdp = bcrypt.generate_password_hash(form.mdp.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, mdp=hash_mdp)
        db.session.add(user)
        db.session.commit()
        flash(_('Account created successfully! You can now log in to your account'), 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title=_('Register'), form=form, current_locale=session.get('lang'))


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.mdp, form.mdp.data):
            flash(_("Welcome Back %(username)s!", username=user.username), 'success')
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash(_('Login Unsuccessful, please check your email and password'), 'danger')
    return render_template('login.html', title=_('Login'), form=form, current_locale=session.get('lang'))


@app.route("/logout")
def logout():
    if current_user.is_authenticated:
        full_soil_data_store.pop(current_user.id, None)
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
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)
    # Delete previous picture if it exists
    if current_user.img:
        prev_picture_path = os.path.join(app.root_path, 'static/profile_pics', current_user.img)
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
        flash(_('Your account has been updated!'), 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    img_file = url_for('static', filename='profile_pics/' + current_user.img)
    return render_template('account.html', title=_('Account'), img_file=img_file, form=form, current_locale=session.get('lang'))

def send_reset_email(user):
    email_sender = app.config['MAIL_ADRESSE']
    email_password = app.config['MAIL_PASSWORD']
    email_reciever = user.email
    email_server = 'smtp.gmail.com'
    email_port = 587
    token = user.get_reset_token()
    server = smtplib.SMTP(email_server, email_port)
    server.starttls()
    server.login(email_sender, email_password)
     
    reset_link = url_for('reset_token', token=token, _external=True)
    msg = lazy_gettext(f'''Subject: Password Reset Request

To reset your password, visit the following link:
{reset_link}

If you did not make this request, then simply ignore this email and no changes will be made.
''')
    server.sendmail(email_sender, email_reciever, str(msg))
    server.quit()

@app.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash(_('An email has been sent with instructions to reset your password. If you didn`t find it in your inbox, check the spam section.'), 'info')
        return redirect(url_for('login'))
    return render_template('reset_request.html', title=_('Reset password'), form=form, current_locale=session.get('lang'))

@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash(_('That is an invalid or expired token'), 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hash_mdp = bcrypt.generate_password_hash(form.mdp.data).decode('utf-8')
        user.mdp = hash_mdp
        db.session.commit()
        flash(_('Your password has been updated! You can now log in to your account'), 'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', title=_('Reset password'), form=form, current_locale=session.get('lang'))


@app.route("/download")
@login_required
def download_report():
    if 'lat' in session.keys() and 'lon' in session.keys() and session.get('lat') and session.get('lon'):

        full_weather_data = session.get('weather_data')

        soil_data = full_soil_data_store.get(current_user.id)
        if not soil_data:
            # fallback to optimized data stored in session
            soil_data = session.get('soil_data')
            flash("Full soil data not yet ready, using optimized data instead.", "warning")
        else:
            flash("Full soil data used for report!", "success")

        layers = soil_data['properties']['layers']

        pdf.add_first_page("agrimar/static/AGRIMAR 2.png", PDF.get_first_page_text())
        pdf.add_second_page("Contenu", PDF.get_second_page_text())

        add_weather_properties_pages(pdf,full_weather_data)
        add_soil_report_pages(pdf, layers)

        # Save the PDF
        pdf.output('agrimar/data_graphs+pdf/Rapport_AGRIMAR.pdf')
        full_soil_data_store.pop(current_user.id, None)  # clear temporary data after use
        return send_file('data_graphs+pdf/Rapport_AGRIMAR.pdf', as_attachment=True)
    else:
        flash(_('Please insert your coordinates first'), 'warning')
        return redirect(url_for("home"))
    
def generate_and_email_report(user_id, recipient_email, lat, lon):
    try:
        print(f"[INFO] Starting report generation for user {user_id}...")

        report_path = f'agrimar/data_graphs+pdf/Rapport_AGRIMAR_{user_id}.pdf'
        pdf.add_first_page("agrimar/static/AGRIMAR 2.png", "Rapport AGRIMAR")
        pdf.add_second_page(
            "Contenu",
            "Ce rapport présente les résultats météorologiques et pédologiques collectés à partir des coordonnées fournies. Il inclut des graphiques, des analyses et des sections récapitulatives.",
            ""
        )


        # WEATHER SECTION
        try:
            full_weather_data = get_weather_data(lat, lon)
            if full_weather_data and 'daily' in full_weather_data:
                print(f"[INFO] Weather data fetched.")
                add_weather_properties_pages(pdf, full_weather_data)
            else:
                raise Exception("Weather data is empty or malformed.")
        except Exception as weather_error:
            print(f"[WARNING] Weather data fetch failed: {weather_error}")
            pdf.add_page()
            pdf.set_font("Arial", style='B', size=16)
            pdf.multi_cell(0, 10, "ATTENTION Données Météorologiques Indisponibles")
            pdf.set_font("Arial", size=12)
            pdf.multi_cell(0, 10, "Les données météorologiques ne sont actuellement pas disponibles. Veuillez réessayer plus tard pour obtenir un rapport complet.")

        # SOIL SECTION
        soil_data = full_soil_data_store.get(user_id)
        if not soil_data:
            print(f"[WARNING] Full soil data not ready, fetching fallback soil data...")
            try:
                soil_data = get_soil_data(lat, lon)
                if not soil_data or 'properties' not in soil_data or not soil_data['properties'].get('layers'):
                    print("[ERROR] Soil data fetch returned empty or incomplete data.")
                    soil_data = None
            except Exception as soil_error:
                print(f"[ERROR] Soil data fetch failed with exception: {soil_error}")
                soil_data = None

        if soil_data and 'properties' in soil_data and soil_data['properties'].get('layers'):
            layers = soil_data['properties']['layers']
            add_soil_report_pages(pdf, layers)
        else:
            pdf.add_page()
            pdf.set_font("Arial", style='B', size=16)
            pdf.multi_cell(0, 10, "ATTENTION: Données du Sol Indisponibles")
            pdf.set_font("Arial", size=12)
            pdf.multi_cell(0, 10, "Les données du sol ne sont actuellement pas disponibles. Veuillez réessayer plus tard pour obtenir un rapport complet.")

        # SAVE & EMAIL
        pdf.output(report_path)
        print(f"[INFO] PDF report saved at {report_path}.")

        send_report_email(recipient_email, report_path)
        print(f"[INFO] Report email sent to {recipient_email}.")

    except Exception as e:
        print(f"[ERROR] Failed to generate/send report for user {user_id}: {e}")



@app.route("/request_report")
@login_required
def request_report():
    if 'lat' in session and 'lon' in session and session.get('lat') and session.get('lon'):
        recipient_email = current_user.email
        user_id = current_user.id
        lat = session.get('lat')
        lon = session.get('lon')

        executor.submit(generate_and_email_report, user_id, recipient_email, lat, lon)

        flash('✅ Your report is being prepared and will be sent to your email shortly.', 'success')
        return redirect(url_for("home"))
    else:
        flash('ATTENTION Please insert your coordinates first', 'warning')
        return redirect(url_for("home"))
