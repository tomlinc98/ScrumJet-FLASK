import jwt
from time import time
from app import db, login
from datetime import datetime
from flask import current_app
from flask_login import UserMixin
from flask_login import LoginManager # new code entry
from werkzeug.security import generate_password_hash, check_password_hash

# timestamp to be inherited by other class models
class TimestampMixin(object):
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

@login.user_loader  # new code entry
def load_user(id):  # new code entry
    return User.query.get(int(id)) # new code entry --- # slightly modified such that the user is loaded based on the id in the db

# user class
class User(db.Model, TimestampMixin, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    email = db.Column(db.String(80), nullable=False, unique=True)
    password_hash = db.Column(db.String(128))
    first_name = db.Column(db.String(20), nullable=False)
    last_name = db.Column(db.String(20), nullable=False)
    admin = db.Column(db.Integer, default=0)
    reviews = db.relationship('Review', backref='user', lazy='dynamic')
    courses = db.relationship('Course', backref='user', lazy='dynamic')

    # print to console username created
    def __repr__(self):
        return f'<User {self.username}>'

    # generate user password i.e. hashing
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    # check user password is correct
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    # for reseting a user password
    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'],
            algorithm='HS256').decode('utf-8')

    # verify token generated for resetting password
    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)

# announcements class
class Announcement(TimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    body = db.Column(db.String, nullable=False)

    def __repr__(self):
        return f'<Announcement "{self.title}">'

# course category class (certified/non-certified)
# has many courses
class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False, unique=True)
    courses = db.relationship('Course', backref='category', lazy='dynamic')

    def __repr__(self):
        return f'<Category {self.name}>'

# course class
# belongs to category
class Course(TimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False, unique=True)
    summary = db.Column(db.Text)
    image = db.Column(db.String(30))
    price = db.Column(db.Float, default=99.99)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    reviews = db.relationship('Review', backref='course', lazy='dynamic')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f'<Course {self.title}>'

# review class
# belongs to user and course
class Review(TimestampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text)
    rating = db.Column(db.Float, default=0.0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))

@login.user_loader
def load_user(id):
    return User.query.get(int(id))