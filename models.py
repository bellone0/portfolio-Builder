from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
import json
from app import db

class User(UserMixin, db.Model):
    """Modèle utilisateur"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    is_email_verified = db.Column(db.Boolean, default=False)
    reset_token = db.Column(db.String(100))
    reset_token_expires = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relation avec le portfolio
    portfolio = db.relationship('Portfolio', backref='user', uselist=False, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

class Portfolio(db.Model):
    """Modèle portfolio"""
    __tablename__ = 'portfolios'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    public_url = db.Column(db.String(100), unique=True, nullable=False, index=True)
    
    # Informations personnelles
    bio = db.Column(db.Text)
    location = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    website = db.Column(db.String(200))
    linkedin = db.Column(db.String(200))
    github = db.Column(db.String(200))
    profile_image = db.Column(db.String(200))
    
    # CV
    cv_filename = db.Column(db.String(200))
    cv_url = db.Column(db.String(200))
    cv_uploaded_at = db.Column(db.DateTime)
    
    # Personnalisation
    theme_primary_color = db.Column(db.String(7), default='#3B82F6')
    theme_secondary_color = db.Column(db.String(7), default='#1F2937')
    theme_font_family = db.Column(db.String(50), default='Inter')
    theme_layout = db.Column(db.String(20), default='modern')
    
    # Visibilité et statistiques
    is_public = db.Column(db.Boolean, default=True)
    views_count = db.Column(db.Integer, default=0)
    last_viewed = db.Column(db.DateTime)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    projects = db.relationship('Project', backref='portfolio', lazy='dynamic', cascade='all, delete-orphan')
    experiences = db.relationship('Experience', backref='portfolio', lazy='dynamic', cascade='all, delete-orphan')
    education = db.relationship('Education', backref='portfolio', lazy='dynamic', cascade='all, delete-orphan')
    skills = db.relationship('Skill', backref='portfolio', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Portfolio {self.public_url}>'
    
    def increment_views(self):
        self.views_count += 1
        self.last_viewed = datetime.utcnow()
        db.session.commit()

class Project(db.Model):
    """Modèle projet"""
    __tablename__ = 'projects'
    
    id = db.Column(db.Integer, primary_key=True)
    portfolio_id = db.Column(db.Integer, db.ForeignKey('portfolios.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    technologies = db.Column(db.Text)  # JSON string
    github_url = db.Column(db.String(200))
    demo_url = db.Column(db.String(200))
    images = db.Column(db.Text)  # JSON string
    featured = db.Column(db.Boolean, default=False)
    order_index = db.Column(db.Integer, default=0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def get_technologies_list(self):
        if self.technologies and self.technologies.strip():
            try:
                return json.loads(self.technologies)
            except (json.JSONDecodeError, ValueError):
                # Si ce n'est pas du JSON valide, traiter comme une liste séparée par virgules
                return [tech.strip() for tech in self.technologies.split(',') if tech.strip()]
        return []
    
    def set_technologies_list(self, tech_list):
        self.technologies = json.dumps(tech_list)
    
    def get_images_list(self):
        if self.images and self.images.strip():
            try:
                return json.loads(self.images)
            except (json.JSONDecodeError, ValueError):
                return []
        return []
    
    def set_images_list(self, img_list):
        self.images = json.dumps(img_list)

class Experience(db.Model):
    """Modèle expérience professionnelle"""
    __tablename__ = 'experiences'
    
    id = db.Column(db.Integer, primary_key=True)
    portfolio_id = db.Column(db.Integer, db.ForeignKey('portfolios.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    company = db.Column(db.String(200), nullable=False)
    location = db.Column(db.String(100))
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date)
    current = db.Column(db.Boolean, default=False)
    description = db.Column(db.Text, nullable=False)
    order_index = db.Column(db.Integer, default=0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Education(db.Model):
    """Modèle formation"""
    __tablename__ = 'education'
    
    id = db.Column(db.Integer, primary_key=True)
    portfolio_id = db.Column(db.Integer, db.ForeignKey('portfolios.id'), nullable=False)
    degree = db.Column(db.String(200), nullable=False)
    institution = db.Column(db.String(200), nullable=False)
    location = db.Column(db.String(100))
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date)
    current = db.Column(db.Boolean, default=False)
    description = db.Column(db.Text)
    order_index = db.Column(db.Integer, default=0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Skill(db.Model):
    """Modèle compétence"""
    __tablename__ = 'skills'
    
    id = db.Column(db.Integer, primary_key=True)
    portfolio_id = db.Column(db.Integer, db.ForeignKey('portfolios.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    level = db.Column(db.String(20), default='Intermédiaire')
    category = db.Column(db.String(30), default='Technique')
    order_index = db.Column(db.Integer, default=0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
