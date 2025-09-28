from flask import Blueprint, render_template, request, send_from_directory, current_app, abort, session
from models import Portfolio, Project, Experience, Education, Skill, User, db
import json
import requests
from datetime import datetime

public_bp = Blueprint('public', __name__)

@public_bp.route('/search')
def search_portfolios():
    """Rechercher des portfolios publics (page publique)"""
    query = request.args.get('q', '')
    portfolios = []
    
    if query:
        # Rechercher par nom d'utilisateur, nom complet, ou bio
        portfolios = Portfolio.query.join(User).filter(
            Portfolio.is_public == True,
            db.or_(
                User.username.contains(query),
                User.first_name.contains(query),
                User.last_name.contains(query),
                Portfolio.bio.contains(query)
            )
        ).limit(20).all()
    
    return render_template('public/search.html', portfolios=portfolios, query=query)

@public_bp.route('/<public_url>')
def view_portfolio(public_url):
    """Voir un portfolio public"""
    portfolio = Portfolio.query.filter_by(public_url=public_url, is_public=True).first_or_404()
    
    # Incrémenter le compteur de vues seulement si l'utilisateur n'a pas encore visité ce portfolio dans cette session
    viewed_key = f'viewed_{portfolio.id}'
    if not session.get(viewed_key, False):
        portfolio.increment_views()
        session[viewed_key] = True
        
        # Enregistrer les informations du visiteur
        visitor_info = {
            'ip': request.remote_addr,
            'user_agent': request.headers.get('User-Agent', ''),
            'referrer': request.headers.get('Referer', ''),
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Stocker les informations du visiteur dans la session
        if 'visitors' not in session:
            session['visitors'] = []
        session['visitors'].append(visitor_info)
    
    # Récupérer toutes les données du portfolio
    projects = portfolio.projects.order_by(Project.order_index).all()
    experiences = portfolio.experiences.order_by(Experience.order_index).all()
    education = portfolio.education.order_by(Education.order_index).all()
    skills = portfolio.skills.order_by(Skill.order_index).all()
    
    # Grouper les compétences par catégorie
    skills_by_category = {}
    for skill in skills:
        if skill.category not in skills_by_category:
            skills_by_category[skill.category] = []
        skills_by_category[skill.category].append(skill)
    
    return render_template('public/portfolio.html', 
                         portfolio=portfolio,
                         projects=projects,
                         experiences=experiences,
                         education=education,
                         skills_by_category=skills_by_category)

@public_bp.route('/<public_url>/cv')
def download_cv(public_url):
    """Télécharger le CV d'un portfolio"""
    portfolio = Portfolio.query.filter_by(public_url=public_url, is_public=True).first_or_404()
    
    if not portfolio.cv_filename:
        abort(404)
    
    try:
        return send_from_directory(
            os.path.join(current_app.config['UPLOAD_FOLDER'], 'cv'),
            portfolio.cv_filename,
            as_attachment=True,
            download_name=f"CV_{portfolio.user.get_full_name().replace(' ', '_')}.pdf"
        )
    except FileNotFoundError:
        abort(404)

@public_bp.route('/<public_url>/api')
def portfolio_api(public_url):
    """API JSON pour récupérer les données du portfolio"""
    portfolio = Portfolio.query.filter_by(public_url=public_url, is_public=True).first_or_404()
    
    # Incrémenter le compteur de vues seulement si l'utilisateur n'a pas encore visité ce portfolio dans cette session
    viewed_key = f'viewed_{portfolio.id}'
    if not session.get(viewed_key, False):
        portfolio.increment_views()
        session[viewed_key] = True
    
    # Préparer les données JSON
    data = {
        'user': {
            'full_name': portfolio.user.get_full_name(),
            'username': portfolio.user.username,
            'email': portfolio.user.email
        },
        'portfolio': {
            'bio': portfolio.bio,
            'location': portfolio.location,
            'phone': portfolio.phone,
            'website': portfolio.website,
            'linkedin': portfolio.linkedin,
            'github': portfolio.github,
            'profile_image': portfolio.profile_image,
            'theme': {
                'primary_color': portfolio.theme_primary_color,
                'secondary_color': portfolio.theme_secondary_color,
                'font_family': portfolio.theme_font_family,
                'layout': portfolio.theme_layout
            },
            'views_count': portfolio.views_count,
            'created_at': portfolio.created_at.isoformat() if portfolio.created_at else None,
            'updated_at': portfolio.updated_at.isoformat() if portfolio.updated_at else None
        },
        'projects': [],
        'experiences': [],
        'education': [],
        'skills': []
    }
    
    # Ajouter les projets
    for project in portfolio.projects.order_by(Project.order_index).all():
        data['projects'].append({
            'id': project.id,
            'title': project.title,
            'description': project.description,
            'technologies': project.get_technologies_list(),
            'github_url': project.github_url,
            'demo_url': project.demo_url,
            'featured': project.featured,
            'created_at': project.created_at.isoformat() if project.created_at else None
        })
    
    # Ajouter les expériences
    for exp in portfolio.experiences.order_by(Experience.order_index).all():
        data['experiences'].append({
            'id': exp.id,
            'title': exp.title,
            'company': exp.company,
            'location': exp.location,
            'start_date': exp.start_date.isoformat() if exp.start_date else None,
            'end_date': exp.end_date.isoformat() if exp.end_date else None,
            'current': exp.current,
            'description': exp.description,
            'created_at': exp.created_at.isoformat() if exp.created_at else None
        })
    
    # Ajouter les formations
    for edu in portfolio.education.order_by(Education.order_index).all():
        data['education'].append({
            'id': edu.id,
            'degree': edu.degree,
            'institution': edu.institution,
            'location': edu.location,
            'start_date': edu.start_date.isoformat() if edu.start_date else None,
            'end_date': edu.end_date.isoformat() if edu.end_date else None,
            'current': edu.current,
            'description': edu.description,
            'created_at': edu.created_at.isoformat() if edu.created_at else None
        })
    
    # Ajouter les compétences
    for skill in portfolio.skills.order_by(Skill.order_index).all():
        data['skills'].append({
            'id': skill.id,
            'name': skill.name,
            'level': skill.level,
            'category': skill.category,
            'created_at': skill.created_at.isoformat() if skill.created_at else None
        })
    
    return data

@public_bp.route('/<public_url>/embed')
def embed_portfolio(public_url):
    """Version embarquée du portfolio (iframe)"""
    portfolio = Portfolio.query.filter_by(public_url=public_url, is_public=True).first_or_404()
    
    # Incrémenter le compteur de vues seulement si l'utilisateur n'a pas encore visité ce portfolio dans cette session
    viewed_key = f'viewed_{portfolio.id}'
    if not session.get(viewed_key, False):
        portfolio.increment_views()
        session[viewed_key] = True
    
    # Récupérer toutes les données du portfolio
    projects = portfolio.projects.order_by(Project.order_index).all()
    experiences = portfolio.experiences.order_by(Experience.order_index).all()
    education = portfolio.education.order_by(Education.order_index).all()
    skills = portfolio.skills.order_by(Skill.order_index).all()
    
    # Grouper les compétences par catégorie
    skills_by_category = {}
    for skill in skills:
        if skill.category not in skills_by_category:
            skills_by_category[skill.category] = []
        skills_by_category[skill.category].append(skill)
    
    return render_template('public/embed.html', 
                         portfolio=portfolio,
                         projects=projects,
                         experiences=experiences,
                         education=education,
                         skills_by_category=skills_by_category)
