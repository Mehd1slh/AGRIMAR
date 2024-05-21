from sqlalchemy.orm import relationship
from dataclasses import dataclass
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from datetime import datetime, timezone , timedelta
from agrimar import db , login_manager ,app
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def get_current_date():
    return datetime.now(timezone.utc)+ timedelta(hours=1)

@dataclass
class Message(db.Model):
    id: int
    content: str
    role: str 
    time: datetime
    convo_id: int
    id = db.Column(db.Integer , primary_key=True)
    content = db.Column(db.Text , nullable = False)
    role = db.Column(db.String(20) , nullable = False , default = 'user')
    time = db.Column(db.DateTime, nullable=False, default=get_current_date)
    convo_id = db.Column(db.Integer, db.ForeignKey('conversation.id'), nullable=False)
    def __repr__(self):
        return f"Message('{self.content}' , '{self.role}' , '{self.time}' )"

@dataclass
class Conversation(db.Model):
    id :int
    title :str
    loc_lat :float
    loc_lon :float
    date :datetime
    user_id :int
    # messages :Message
    id = db.Column(db.Integer , primary_key=True)
    title = db.Column(db.String(255) , nullable = False)
    loc_lat = db.Column(db.Float)
    loc_lon = db.Column(db.Float)
    date = db.Column(db.Date , nullable = False , default = lambda:get_current_date().date() )
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    messages = relationship('Message' , backref = 'convo' , lazy = True)

    def __repr__(self):
        return f"Conversation('{self.title}' , '{self.date}' )"


@dataclass
class User(db.Model , UserMixin):
    id :int
    username  :str
    email  :str
    mdp :str
    img  :str
    privilege  :str
    acd :datetime
    # conversations :Conversation
    id = db.Column(db.Integer , primary_key=True)
    username = db.Column(db.String(20) , unique=True , nullable=False)
    email = db.Column(db.String(50) , unique=True , nullable=False)
    mdp = db.Column(db.String(255) , nullable=False)
    img = db.Column(db.String(255) , nullable=False , default = 'default.jpg')
    privilege = db.Column(db.String(15) , nullable=False , default = 'user')
    acd = db.Column(db.DateTime, nullable=False, default=get_current_date)
    conversations = db.relationship('Conversation' , backref = 'author' , lazy = True)

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)
        
    def __repr__(self):
        return f"User('{self.username}' , '{self.email}' , '{self.img}')"



