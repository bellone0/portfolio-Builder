from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, jsonify, send_from_directory, session
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from models import User, Portfolio, Project, Experience, Education, Skill, db
from forms import PortfolioForm, ProjectForm, ExperienceForm, EducationForm, SkillForm, CVUploadForm, CVImportForm, ThemeForm
import os
import json
import secrets
from datetime import datetime

portfolio_bp = Blueprint('portfolio', __name__)

@portfolio_bp.route('/dashboard')
@login_required
def dashboard():
    """Tableau de bord du portfolio"""
    portfolio = current_user.portfolio
    if not portfolio:
        # Créer un portfolio par défaut
        portfolio = create_default_portfolio(current_user)
    
    # Récupérer les données pour les compteurs
    projects = portfolio.projects.all()
    experiences = portfolio.experiences.all()
    education = portfolio.education.all()
    skills = portfolio.skills.all()
    
    return render_template('portfolio/dashboard.html', 
                         portfolio=portfolio,
                         projects=projects,
                         experiences=experiences,
                         education=education,
                         skills=skills)

@portfolio_bp.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    """Édition des informations personnelles du portfolio"""
    portfolio = current_user.portfolio
    if not portfolio:
        portfolio = create_default_portfolio(current_user)
    
    form = PortfolioForm(obj=portfolio)
    
    if form.validate_on_submit():
        portfolio.bio = form.bio.data
        portfolio.location = form.location.data
        portfolio.phone = form.phone.data
        portfolio.website = form.website.data
        portfolio.linkedin = form.linkedin.data
        portfolio.github = form.github.data
        
        # Gestion de l'upload de l'image de profil
        if form.profile_image.data:
            filename = save_profile_image(form.profile_image.data)
            if filename:
                portfolio.profile_image = filename
        
        db.session.commit()
        flash('Portfolio mis à jour avec succès !', 'success')
        return redirect(url_for('portfolio.dashboard'))
    
    return render_template('portfolio/edit.html', form=form, portfolio=portfolio)

@portfolio_bp.route('/projects')
@login_required
def projects():
    """Gestion des projets"""
    portfolio = current_user.portfolio
    if not portfolio:
        portfolio = create_default_portfolio(current_user)
    
    projects = portfolio.projects.order_by(Project.order_index).all()
    return render_template('portfolio/projects.html', projects=projects, portfolio=portfolio)

@portfolio_bp.route('/projects/add', methods=['GET', 'POST'])
@login_required
def add_project():
    """Ajouter un nouveau projet"""
    form = ProjectForm()
    
    if form.validate_on_submit():
        portfolio = current_user.portfolio
        if not portfolio:
            portfolio = create_default_portfolio(current_user)
        
        # Convertir les technologies en JSON
        technologies = [tech.strip() for tech in form.technologies.data.split(',') if tech.strip()]
        
        project = Project(
            portfolio_id=portfolio.id,
            title=form.title.data,
            description=form.description.data,
            technologies=json.dumps(technologies),
            github_url=form.github_url.data,
            demo_url=form.demo_url.data,
            featured=form.featured.data,
            order_index=portfolio.projects.count()
        )
        
        db.session.add(project)
        db.session.commit()
        
        flash('Projet ajouté avec succès !', 'success')
        return redirect(url_for('portfolio.projects'))
    
    return render_template('portfolio/add_project.html', form=form)

@portfolio_bp.route('/projects/edit/<int:project_id>', methods=['GET', 'POST'])
@login_required
def edit_project(project_id):
    """Modifier un projet"""
    project = Project.query.filter_by(id=project_id, portfolio_id=current_user.portfolio.id).first_or_404()
    form = ProjectForm(obj=project)
    
    # Pré-remplir les technologies
    if project.technologies:
        try:
            technologies_list = json.loads(project.technologies)
            form.technologies.data = ', '.join(technologies_list)
        except (json.JSONDecodeError, ValueError):
            # Si ce n'est pas du JSON valide, utiliser directement la chaîne
            form.technologies.data = project.technologies
    
    if form.validate_on_submit():
        project.title = form.title.data
        project.description = form.description.data
        project.github_url = form.github_url.data
        project.demo_url = form.demo_url.data
        project.featured = form.featured.data
        
        # Convertir les technologies en JSON
        technologies = [tech.strip() for tech in form.technologies.data.split(',') if tech.strip()]
        project.technologies = json.dumps(technologies)
        
        db.session.commit()
        flash('Projet mis à jour avec succès !', 'success')
        return redirect(url_for('portfolio.projects'))
    
    return render_template('portfolio/edit_project.html', form=form, project=project)

@portfolio_bp.route('/projects/delete/<int:project_id>', methods=['POST'])
@login_required
def delete_project(project_id):
    """Supprimer un projet"""
    project = Project.query.filter_by(id=project_id, portfolio_id=current_user.portfolio.id).first_or_404()
    
    db.session.delete(project)
    db.session.commit()
    
    flash('Projet supprimé avec succès !', 'success')
    return redirect(url_for('portfolio.projects'))

@portfolio_bp.route('/experiences')
@login_required
def experiences():
    """Gestion des expériences professionnelles"""
    portfolio = current_user.portfolio
    if not portfolio:
        portfolio = create_default_portfolio(current_user)
    
    experiences = portfolio.experiences.order_by(Experience.order_index).all()
    return render_template('portfolio/experiences.html', experiences=experiences, portfolio=portfolio)

@portfolio_bp.route('/experiences/add', methods=['GET', 'POST'])
@login_required
def add_experience():
    """Ajouter une nouvelle expérience"""
    form = ExperienceForm()
    
    if form.validate_on_submit():
        portfolio = current_user.portfolio
        if not portfolio:
            portfolio = create_default_portfolio(current_user)
        
        experience = Experience(
            portfolio_id=portfolio.id,
            title=form.title.data,
            company=form.company.data,
            location=form.location.data,
            start_date=form.start_date.data,
            end_date=form.end_date.data if not form.current.data else None,
            current=form.current.data,
            description=form.description.data,
            order_index=portfolio.experiences.count()
        )
        
        db.session.add(experience)
        db.session.commit()
        
        flash('Expérience ajoutée avec succès !', 'success')
        return redirect(url_for('portfolio.experiences'))
    
    return render_template('portfolio/add_experience.html', form=form)

@portfolio_bp.route('/experiences/edit/<int:exp_id>', methods=['GET', 'POST'])
@login_required
def edit_experience(exp_id):
    """Modifier une expérience"""
    experience = Experience.query.filter_by(id=exp_id, portfolio_id=current_user.portfolio.id).first_or_404()
    form = ExperienceForm(obj=experience)
    
    if form.validate_on_submit():
        experience.title = form.title.data
        experience.company = form.company.data
        experience.location = form.location.data
        experience.start_date = form.start_date.data
        experience.end_date = form.end_date.data if not form.current.data else None
        experience.current = form.current.data
        experience.description = form.description.data
        
        db.session.commit()
        flash('Expérience mise à jour avec succès !', 'success')
        return redirect(url_for('portfolio.experiences'))
    
    return render_template('portfolio/edit_experience.html', form=form, experience=experience)

@portfolio_bp.route('/experiences/delete/<int:exp_id>', methods=['POST'])
@login_required
def delete_experience(exp_id):
    """Supprimer une expérience"""
    experience = Experience.query.filter_by(id=exp_id, portfolio_id=current_user.portfolio.id).first_or_404()
    
    db.session.delete(experience)
    db.session.commit()
    
    flash('Expérience supprimée avec succès !', 'success')
    return redirect(url_for('portfolio.experiences'))

@portfolio_bp.route('/education')
@login_required
def education():
    """Gestion des formations"""
    portfolio = current_user.portfolio
    if not portfolio:
        portfolio = create_default_portfolio(current_user)
    
    education_list = portfolio.education.order_by(Education.order_index).all()
    return render_template('portfolio/education.html', education=education_list, portfolio=portfolio)

@portfolio_bp.route('/education/add', methods=['GET', 'POST'])
@login_required
def add_education():
    """Ajouter une nouvelle formation"""
    form = EducationForm()
    
    if form.validate_on_submit():
        portfolio = current_user.portfolio
        if not portfolio:
            portfolio = create_default_portfolio(current_user)
        
        education = Education(
            portfolio_id=portfolio.id,
            degree=form.degree.data,
            institution=form.institution.data,
            location=form.location.data,
            start_date=form.start_date.data,
            end_date=form.end_date.data if not form.current.data else None,
            current=form.current.data,
            description=form.description.data,
            order_index=portfolio.education.count()
        )
        
        db.session.add(education)
        db.session.commit()
        
        flash('Formation ajoutée avec succès !', 'success')
        return redirect(url_for('portfolio.education'))
    
    return render_template('portfolio/add_education.html', form=form)

@portfolio_bp.route('/skills')
@login_required
def skills():
    """Gestion des compétences"""
    portfolio = current_user.portfolio
    if not portfolio:
        portfolio = create_default_portfolio(current_user)
    
    skills = portfolio.skills.order_by(Skill.order_index).all()
    return render_template('portfolio/skills.html', skills=skills, portfolio=portfolio)

@portfolio_bp.route('/skills/add', methods=['GET', 'POST'])
@login_required
def add_skill():
    """Ajouter une nouvelle compétence"""
    form = SkillForm()
    
    if form.validate_on_submit():
        portfolio = current_user.portfolio
        if not portfolio:
            portfolio = create_default_portfolio(current_user)
        
        skill = Skill(
            portfolio_id=portfolio.id,
            name=form.name.data,
            level=form.level.data,
            category=form.category.data,
            order_index=portfolio.skills.count()
        )
        
        db.session.add(skill)
        db.session.commit()
        
        flash('Compétence ajoutée avec succès !', 'success')
        return redirect(url_for('portfolio.skills'))
    
    return render_template('portfolio/add_skill.html', form=form)

@portfolio_bp.route('/skills/edit/<int:skill_id>', methods=['GET', 'POST'])
@login_required
def edit_skill(skill_id):
    """Modifier une compétence"""
    skill = Skill.query.filter_by(id=skill_id, portfolio_id=current_user.portfolio.id).first_or_404()
    form = SkillForm(obj=skill)
    
    if form.validate_on_submit():
        skill.name = form.name.data
        skill.level = form.level.data
        skill.category = form.category.data
        
        db.session.commit()
        flash('Compétence mise à jour avec succès !', 'success')
        return redirect(url_for('portfolio.skills'))
    
    return render_template('portfolio/edit_skill.html', form=form, skill=skill)

@portfolio_bp.route('/skills/delete/<int:skill_id>', methods=['POST'])
@login_required
def delete_skill(skill_id):
    """Supprimer une compétence"""
    skill = Skill.query.filter_by(id=skill_id, portfolio_id=current_user.portfolio.id).first_or_404()
    
    db.session.delete(skill)
    db.session.commit()
    
    flash('Compétence supprimée avec succès !', 'success')
    return redirect(url_for('portfolio.skills'))

@portfolio_bp.route('/education/edit/<int:edu_id>', methods=['GET', 'POST'])
@login_required
def edit_education(edu_id):
    """Modifier une formation"""
    education = Education.query.filter_by(id=edu_id, portfolio_id=current_user.portfolio.id).first_or_404()
    form = EducationForm(obj=education)
    
    if form.validate_on_submit():
        education.degree = form.degree.data
        education.institution = form.institution.data
        education.location = form.location.data
        education.start_date = form.start_date.data
        education.end_date = form.end_date.data if not form.current.data else None
        education.current = form.current.data
        education.description = form.description.data
        
        db.session.commit()
        flash('Formation mise à jour avec succès !', 'success')
        return redirect(url_for('portfolio.education'))
    
    return render_template('portfolio/edit_education.html', form=form, education=education)

@portfolio_bp.route('/education/delete/<int:edu_id>', methods=['POST'])
@login_required
def delete_education(edu_id):
    """Supprimer une formation"""
    education = Education.query.filter_by(id=edu_id, portfolio_id=current_user.portfolio.id).first_or_404()
    
    db.session.delete(education)
    db.session.commit()
    
    flash('Formation supprimée avec succès !', 'success')
    return redirect(url_for('portfolio.education'))

@portfolio_bp.route('/cv', methods=['GET', 'POST'])
@login_required
def cv():
    """Gestion du CV"""
    portfolio = current_user.portfolio
    if not portfolio:
        portfolio = create_default_portfolio(current_user)
    
    form = CVUploadForm()
    import_form = CVImportForm()
    
    if form.validate_on_submit():
        if form.cv_file.data:
            filename = save_cv_file(form.cv_file.data)
            if filename:
                portfolio.cv_filename = filename
                portfolio.cv_url = f"/uploads/cv/{filename}"
                portfolio.cv_uploaded_at = datetime.utcnow()
                db.session.commit()
                flash('CV téléchargé avec succès !', 'success')
                return redirect(url_for('portfolio.cv'))
    
    if import_form.validate_on_submit():
        # Import de CV depuis une URL
        import requests
        try:
            response = requests.get(import_form.cv_url.data, timeout=30)
            if response.status_code == 200:
                # Vérifier que c'est un PDF
                if response.headers.get('content-type', '').startswith('application/pdf'):
                    # Générer un nom de fichier unique
                    filename = import_form.cv_name.data or f"imported_cv_{current_user.id}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.pdf"
                    filename = secure_filename(filename)
                    
                    # Créer le dossier s'il n'existe pas
                    cv_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], 'cv')
                    os.makedirs(cv_folder, exist_ok=True)
                    
                    # Sauvegarder le fichier
                    file_path = os.path.join(cv_folder, filename)
                    with open(file_path, 'wb') as f:
                        f.write(response.content)
                    
                    # Mettre à jour le portfolio
                    portfolio.cv_filename = filename
                    portfolio.cv_url = f"/uploads/cv/{filename}"
                    portfolio.cv_uploaded_at = datetime.utcnow()
                    db.session.commit()
                    
                    flash('CV importé avec succès !', 'success')
                    return redirect(url_for('portfolio.cv'))
                else:
                    flash('Le fichier doit être un PDF.', 'error')
            else:
                flash('Impossible de télécharger le fichier depuis cette URL.', 'error')
        except requests.RequestException as e:
            flash(f'Erreur lors du téléchargement : {str(e)}', 'error')
        except Exception as e:
            flash(f'Erreur lors de l\'import : {str(e)}', 'error')
    
    return render_template('portfolio/cv.html', form=form, import_form=import_form, portfolio=portfolio)

@portfolio_bp.route('/theme', methods=['GET', 'POST'])
@login_required
def theme():
    """Personnalisation du thème"""
    portfolio = current_user.portfolio
    if not portfolio:
        portfolio = create_default_portfolio(current_user)
    
    form = ThemeForm(obj=portfolio)
    
    if form.validate_on_submit():
        portfolio.theme_primary_color = form.primary_color.data
        portfolio.theme_secondary_color = form.secondary_color.data
        portfolio.theme_font_family = form.font_family.data
        portfolio.theme_layout = form.layout.data
        
        db.session.commit()
        flash('Thème mis à jour avec succès !', 'success')
        return redirect(url_for('portfolio.theme'))
    
    return render_template('portfolio/theme.html', form=form, portfolio=portfolio)

@portfolio_bp.route('/preview')
@login_required
def preview():
    """Aperçu du portfolio"""
    portfolio = current_user.portfolio
    if not portfolio:
        portfolio = create_default_portfolio(current_user)
    
    return render_template('portfolio/preview.html', portfolio=portfolio)

@portfolio_bp.route('/search', methods=['GET', 'POST'])
@login_required
def search_portfolios():
    """Rechercher des portfolios publics"""
    query = request.form.get('query', '') if request.method == 'POST' else request.args.get('q', '')
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
    
    return render_template('portfolio/search.html', portfolios=portfolios, query=query)

@portfolio_bp.route('/analytics')
@login_required
def analytics():
    """Analytics du portfolio"""
    portfolio = current_user.portfolio
    if not portfolio:
        portfolio = create_default_portfolio(current_user)
    
    # Récupérer les informations des visiteurs depuis la session
    visitors = session.get('visitors', [])
    
    return render_template('portfolio/analytics.html', portfolio=portfolio, visitors=visitors)

def create_default_portfolio(user):
    """Créer un portfolio par défaut pour un utilisateur"""
    public_url = f"{user.username}-{secrets.token_hex(4)}"
    
    portfolio = Portfolio(
        user_id=user.id,
        public_url=public_url,
        bio=f"Bonjour, je suis {user.get_full_name()}.",
        location="",
        phone="",
        website="",
        linkedin="",
        github=""
    )
    
    db.session.add(portfolio)
    db.session.commit()
    
    return portfolio

def save_profile_image(file):
    """Sauvegarder l'image de profil"""
    if file and allowed_file(file.filename, {'png', 'jpg', 'jpeg', 'gif'}):
        filename = secure_filename(file.filename)
        filename = f"profile_{current_user.id}_{secrets.token_hex(8)}_{filename}"
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], 'images', filename)
        file.save(filepath)
        return filename
    return None

def save_cv_file(file):
    """Sauvegarder le fichier CV"""
    if file and allowed_file(file.filename, {'pdf'}):
        filename = secure_filename(file.filename)
        filename = f"cv_{current_user.id}_{secrets.token_hex(8)}_{filename}"
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], 'cv', filename)
        file.save(filepath)
        return filename
    return None

def allowed_file(filename, allowed_extensions):
    """Vérifier si l'extension du fichier est autorisée"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions
