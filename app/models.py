from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from . import db, login_manager

class User(UserMixin, db.Model):
    """User model for authentication"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    email = db.Column(db.String(120), unique=True, index=True)
    password_hash = db.Column(db.String(256))
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

@login_manager.user_loader
def load_user(user_id):
    """Flask-Login user loader function"""
    return User.query.get(int(user_id))

class Candidate(db.Model):
    """Candidate model for storing CV information"""
    __tablename__ = 'candidates'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, index=True)
    phone = db.Column(db.String(20))
    age = db.Column(db.Integer)
    education = db.Column(db.Text)
    skills = db.Column(db.ARRAY(db.String))  # PostgreSQL array type
    experience = db.Column(db.Text)
    experience_level = db.Column(db.String(20))  # Junior, Mid, Senior
    industry = db.Column(db.String(100))
    certifications = db.Column(db.ARRAY(db.String))  # CA, CIMA, CFA, etc.
    resume_path = db.Column(db.String(255))  # Path to stored resume
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    def to_dict(self):
        """Convert candidate to dictionary for API responses"""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'age': self.age,
            'education': self.education,
            'skills': self.skills,
            'experience': self.experience,
            'experience_level': self.experience_level,
            'industry': self.industry,
            'certifications': self.certifications,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
