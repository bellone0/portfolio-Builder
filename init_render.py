#!/usr/bin/env python3
"""
Script d'initialisation pour Render
Crée les tables de base de données et ajoute des données de démonstration
"""

import os
import sys
from app import app, db
from models import User, Portfolio, Project, Experience, Education, Skill
from werkzeug.security import generate_password_hash
import secrets
from datetime import datetime

def init_database():
    """Initialiser la base de données"""
    print("🗄️ Initialisation de la base de données...")
    
    with app.app_context():
        # Créer toutes les tables
        db.create_all()
        print("✅ Tables créées avec succès")
        
        # Vérifier si des utilisateurs existent déjà
        if User.query.first():
            print("ℹ️ Des utilisateurs existent déjà, pas d'ajout de données de démonstration")
            return
        
        # Créer un utilisateur de démonstration
        demo_user = User(
            username='demo',
            email='demo@example.com',
            first_name='Demo',
            last_name='User',
            password_hash=generate_password_hash('demo123')
        )
        db.session.add(demo_user)
        db.session.commit()
        
        # Créer un portfolio pour le démo
        demo_portfolio = Portfolio(
            user_id=demo_user.id,
            public_url='demo-portfolio',
            bio='Portfolio de démonstration - Portfolio Builder',
            location='Paris, France',
            website='https://example.com',
            linkedin='https://linkedin.com/in/demo',
            github='https://github.com/demo',
            is_public=True,
            views_count=0
        )
        db.session.add(demo_portfolio)
        db.session.commit()
        
        # Ajouter des projets de démonstration
        projects_data = [
            {
                'title': 'Application Web Portfolio',
                'description': 'Application de création de portfolios professionnels',
                'technologies': '["Python", "Flask", "SQLAlchemy", "TailwindCSS"]',
                'github_url': 'https://github.com/demo/portfolio-builder',
                'live_url': 'https://portfolio-builder.onrender.com',
                'order_index': 1
            },
            {
                'title': 'API REST',
                'description': 'API RESTful pour la gestion des données',
                'technologies': '["Python", "Flask", "SQLAlchemy", "JSON"]',
                'github_url': 'https://github.com/demo/api-rest',
                'live_url': 'https://api-demo.onrender.com',
                'order_index': 2
            }
        ]
        
        for project_data in projects_data:
            project = Project(
                portfolio_id=demo_portfolio.id,
                **project_data
            )
            db.session.add(project)
        
        # Ajouter des expériences de démonstration
        experiences_data = [
            {
                'title': 'Développeur Full Stack',
                'company': 'Tech Company',
                'location': 'Paris, France',
                'start_date': datetime(2023, 1, 1),
                'end_date': None,
                'description': 'Développement d\'applications web modernes',
                'order_index': 1
            },
            {
                'title': 'Développeur Python',
                'company': 'Startup Inc',
                'location': 'Lyon, France',
                'start_date': datetime(2022, 6, 1),
                'end_date': datetime(2022, 12, 31),
                'description': 'Développement backend avec Python et Flask',
                'order_index': 2
            }
        ]
        
        for exp_data in experiences_data:
            experience = Experience(
                portfolio_id=demo_portfolio.id,
                **exp_data
            )
            db.session.add(experience)
        
        # Ajouter des formations de démonstration
        education_data = [
            {
                'degree': 'Master en Informatique',
                'institution': 'Université de Paris',
                'location': 'Paris, France',
                'start_date': datetime(2020, 9, 1),
                'end_date': datetime(2022, 6, 30),
                'description': 'Spécialisation en développement web',
                'order_index': 1
            },
            {
                'degree': 'Licence Informatique',
                'institution': 'Université de Lyon',
                'location': 'Lyon, France',
                'start_date': datetime(2018, 9, 1),
                'end_date': datetime(2020, 6, 30),
                'description': 'Formation générale en informatique',
                'order_index': 2
            }
        ]
        
        for edu_data in education_data:
            education = Education(
                portfolio_id=demo_portfolio.id,
                **edu_data
            )
            db.session.add(education)
        
        # Ajouter des compétences de démonstration
        skills_data = [
            {'name': 'Python', 'level': 90, 'category': 'Langages', 'order_index': 1},
            {'name': 'Flask', 'level': 85, 'category': 'Frameworks', 'order_index': 2},
            {'name': 'SQLAlchemy', 'level': 80, 'category': 'ORM', 'order_index': 3},
            {'name': 'JavaScript', 'level': 75, 'category': 'Langages', 'order_index': 4},
            {'name': 'HTML/CSS', 'level': 85, 'category': 'Frontend', 'order_index': 5},
            {'name': 'Git', 'level': 80, 'category': 'Outils', 'order_index': 6}
        ]
        
        for skill_data in skills_data:
            skill = Skill(
                portfolio_id=demo_portfolio.id,
                **skill_data
            )
            db.session.add(skill)
        
        db.session.commit()
        print("✅ Données de démonstration ajoutées avec succès")
        print("👤 Utilisateur de démo créé :")
        print("   - Email: demo@example.com")
        print("   - Mot de passe: demo123")
        print("   - Portfolio: https://votre-app.onrender.com/p/demo-portfolio")

if __name__ == '__main__':
    init_database()
