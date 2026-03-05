"""
Smart College Student Assistance Portal
Database Models
"""
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import json
import pickle

db = SQLAlchemy()


class Admin(UserMixin, db.Model):
    """Admin user model for authentication"""
    __tablename__ = 'admin'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verify password"""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<Admin {self.username}>'


class Student(db.Model):
    """Student model with all academic and personal details"""
    __tablename__ = 'student'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    roll_no = db.Column(db.String(20), unique=True, nullable=False)
    department = db.Column(db.String(50), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    email = db.Column(db.String(100), unique=True)
    phone = db.Column(db.String(15))
    
    # JSON stored fields
    _skills = db.Column('skills', db.Text, default='[]')
    _projects = db.Column('projects', db.Text, default='[]')
    _internships = db.Column('internships', db.Text, default='[]')
    
    # Image and embeddings
    image_path = db.Column(db.String(200))
    _face_embedding = db.Column('face_embedding', db.LargeBinary)
    _text_embedding = db.Column('text_embedding', db.LargeBinary)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Properties for JSON fields
    @property
    def skills(self):
        return json.loads(self._skills) if self._skills else []
    
    @skills.setter
    def skills(self, value):
        self._skills = json.dumps(value) if value else '[]'
    
    @property
    def projects(self):
        return json.loads(self._projects) if self._projects else []
    
    @projects.setter
    def projects(self, value):
        self._projects = json.dumps(value) if value else '[]'
    
    @property
    def internships(self):
        return json.loads(self._internships) if self._internships else []
    
    @internships.setter
    def internships(self, value):
        self._internships = json.dumps(value) if value else '[]'
    
    # Properties for embeddings
    @property
    def face_embedding(self):
        return pickle.loads(self._face_embedding) if self._face_embedding else None
    
    @face_embedding.setter
    def face_embedding(self, value):
        self._face_embedding = pickle.dumps(value) if value is not None else None
    
    @property
    def text_embedding(self):
        return pickle.loads(self._text_embedding) if self._text_embedding else None
    
    @text_embedding.setter
    def text_embedding(self, value):
        self._text_embedding = pickle.dumps(value) if value is not None else None
    
    def to_dict(self):
        """Convert student to dictionary for API responses"""
        return {
            'id': self.id,
            'name': self.name,
            'roll_no': self.roll_no,
            'department': self.department,
            'year': self.year,
            'email': self.email,
            'phone': self.phone,
            'skills': self.skills,
            'projects': self.projects,
            'internships': self.internships,
            'image_path': self.image_path,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def to_text(self):
        """Convert student data to text for RAG embedding"""
        text_parts = [
            f"Name: {self.name}",
            f"Roll Number: {self.roll_no}",
            f"Department: {self.department}",
            f"Year: {self.year}",
            f"Email: {self.email or 'N/A'}",
            f"Phone: {self.phone or 'N/A'}",
            f"Skills: {', '.join(self.skills) if self.skills else 'None'}",
            f"Projects: {', '.join(self.projects) if self.projects else 'None'}",
            f"Internships: {', '.join(self.internships) if self.internships else 'None'}"
        ]
        return '\n'.join(text_parts)
    
    def __repr__(self):
        return f'<Student {self.name} ({self.roll_no})>'


class Job(db.Model):
    """Job posting model for job application assistance"""
    __tablename__ = 'job'
    
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(100), nullable=False)
    job_description = db.Column(db.Text)
    requirements = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert job to dictionary"""
        return {
            'id': self.id,
            'company_name': self.company_name,
            'role': self.role,
            'job_description': self.job_description,
            'requirements': self.requirements,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<Job {self.role} at {self.company_name}>'


class AssistantConversation(db.Model):
    """Voice-enabled Personal Assistant Conversation Hub"""
    __tablename__ = 'assistant_conversation'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), default="Neural Dialogue")
    summary = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship to messages
    messages = db.relationship('AssistantMessage', backref='conversation', lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'summary': self.summary,
            'created_at': self.created_at.isoformat(),
            'message_count': len(self.messages)
        }


class AssistantMessage(db.Model):
    """Dialogue units for the Personal Assistant"""
    __tablename__ = 'assistant_message'
    
    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('assistant_conversation.id'), nullable=False)
    role = db.Column(db.String(20), nullable=False) # 'user' or 'assistant'
    content = db.Column(db.Text, nullable=False)
    voice_path = db.Column(db.String(255)) # For future voice storage if needed
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'role': self.role,
            'content': self.content,
            'timestamp': self.timestamp.isoformat()
        }
