from agrimar import app, db
from agrimar.model import User
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt(app)  # Initialize Bcrypt with your Flask app

with app.app_context():
    db.drop_all()
    db.create_all()
    
    hashed_password = bcrypt.generate_password_hash('123456').decode('utf-8')
    admin1 = User(username='admin',
                  email='admin@gmail.com',
                  mdp=hashed_password,
                  privilege='admin')
    
    db.session.add(admin1)
    db.session.commit()
