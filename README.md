# 🌱 AgriMar — AI Chatbot Assistant for Moroccan Farmers

AgriMar is a multilingual AI-powered chatbot platform that assists Moroccan farmers with personalized support, weather forecasts, soil data insights, and farming best practices. Built using Flask, it integrates geolocation, external APIs, and user-friendly UI to offer an all-in-one digital assistant for agriculture.

---

## 🚀 Key Features

* 🌍 **Multilingual Support** — Arabic, French, and English
* 🤠 **Chatbot AI** — Provides agricultural advice based on location and data
* 📍 **GPS-Based Context** — Advice tailored to user’s coordinates
* 🌤️ **Weather API Integration** — OpenWeatherMap forecasts
* 🦢 **Soil Data Analysis** — ISRIC SoilGrids API
* 💬 **Chat History & PDF Reports** — Save and export conversations
* 🔐 **Authentication System** — Secure login/register, role-based admin panel
* 📧 **Password Recovery via Email**

---

## 🏠 Architecture Overview

```
Flask + SQLAlchemy + Flask-Login + Flask-Babel
│
├── app.py               # Main entry point
├── db.py                # Database setup
├── requirements.txt     # Python dependencies
├── variables.env        # Environment variables
│
├── agrimar/
│   ├── __init__.py         # App initialization, DB, Babel setup
│   ├── api_data.py         # External API (weather, soil, geolocation)
│   ├── chat.py             # Chatbot logic
│   ├── forms.py            # User forms
│   ├── model.py            # ORM models + PDF generator
│   ├── report.py           # Report creation utilities
│   ├── routes.py           # Flask routes and logic
│   └── templates/          # HTML views
│
├── static/              # CSS, JS, images, Lottie animations
├── uploads/             # Uploaded media
├── translations/        # Internationalization (Arabic/French)
└── data_graphs+pdf/     # Soil/weather graphs, example reports
```

---

## ⚙️ Setup & Run

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/agrimar.git
cd agrimar
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure `.env`

Create a `variables.env` file:

```env
SECRET_KEY=your_secret_key
LOCAL_DB_USER=your_db_user
LOCAL_DB_PASSWORD=your_db_password
LOCAL_DB_HOST=localhost
LOCAL_DB_PORT=3306
DB_NAME=agrimar_db
OPENCAGE_API_KEY=your_opencage_key
WEATHER_API_KEY=your_openweather_key
MAIL_ADRESSE=your_email@gmail.com
MAIL_PASSWORD=your_email_password
```

### 5. Run the App

```bash
python app.py
```

Visit: `http://localhost:5000`

---

## 👥 Authors

* El Mehdi SALIH — [elmehdi.salih@usms.ac.ma](mailto:elmehdi.salih@usms.ac.ma)
* Soumia OUZAT — [soumia.ouzat@usms.ac.ma](mailto:soumia.ouzat@usms.ac.ma)

Supervised by **Mr. Abdellatif HAIR** — FST Béni Mellal

---

## 📜 License

This project is licensed under the MIT License.

---

## 📨 Feedback & Contribution

Issues and contributions are welcome! Please open a pull request or contact us directly.

> “Agriculture is the most healthful, most useful and most noble employment of man.” — George Washington
