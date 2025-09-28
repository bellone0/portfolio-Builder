from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Message
from models import User, db
from forms import LoginForm, RegisterForm, ResetPasswordForm, ResetPasswordRequestForm
import secrets
from datetime import datetime, timedelta

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Inscription d'un nouvel utilisateur"""
    if current_user.is_authenticated:
        return redirect(url_for('portfolio.dashboard'))
    
    form = RegisterForm()
    if form.validate_on_submit():
        # Vérifier si l'utilisateur existe déjà
        existing_user = User.query.filter(
            (User.email == form.email.data) | 
            (User.username == form.username.data)
        ).first()
        
        if existing_user:
            if existing_user.email == form.email.data:
                flash('Un compte avec cet email existe déjà.', 'error')
            else:
                flash('Ce nom d\'utilisateur est déjà pris.', 'error')
            return render_template('auth/register.html', form=form)
        
        # Créer le nouvel utilisateur
        user = User(
            username=form.username.data,
            email=form.email.data,
            password_hash=generate_password_hash(form.password.data),
            first_name=form.first_name.data,
            last_name=form.last_name.data
        )
        
        try:
            db.session.add(user)
            db.session.commit()
            
            # Envoyer email de vérification (optionnel)
            send_verification_email(user)
            
            flash('Compte créé avec succès ! Vous pouvez maintenant vous connecter.', 'success')
            return redirect(url_for('auth.login'))
            
        except Exception as e:
            db.session.rollback()
            flash('Une erreur est survenue lors de la création du compte.', 'error')
            current_app.logger.error(f"Erreur création utilisateur: {e}")
    
    return render_template('auth/register.html', form=form)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Connexion utilisateur"""
    if current_user.is_authenticated:
        return redirect(url_for('portfolio.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            flash(f'Bienvenue {user.get_full_name()} !', 'success')
            return redirect(next_page) if next_page else redirect(url_for('portfolio.dashboard'))
        else:
            flash('Email ou mot de passe incorrect.', 'error')
    
    return render_template('auth/login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    """Déconnexion utilisateur"""
    logout_user()
    flash('Vous avez été déconnecté avec succès.', 'info')
    return redirect(url_for('index'))

@auth_bp.route('/reset-password', methods=['GET', 'POST'])
def reset_password_request():
    """Demande de réinitialisation de mot de passe"""
    if current_user.is_authenticated:
        return redirect(url_for('portfolio.dashboard'))
    
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Si un compte avec cet email existe, vous recevrez un email avec les instructions de réinitialisation.', 'info')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/reset_password_request.html', form=form)

@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Réinitialisation du mot de passe avec token"""
    if current_user.is_authenticated:
        return redirect(url_for('portfolio.dashboard'))
    
    user = User.verify_reset_token(token)
    if not user:
        flash('Token invalide ou expiré.', 'error')
        return redirect(url_for('auth.reset_password_request'))
    
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.password_hash = generate_password_hash(form.password.data)
        user.reset_token = None
        user.reset_token_expires = None
        db.session.commit()
        flash('Votre mot de passe a été réinitialisé avec succès.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/reset_password.html', form=form)

def send_verification_email(user):
    """Envoyer email de vérification"""
    try:
        token = user.get_reset_token()
        msg = Message(
            'Vérification de votre compte Portfolio Builder',
            sender=current_app.config['MAIL_USERNAME'],
            recipients=[user.email]
        )
        msg.body = f'''
Bonjour {user.get_full_name()},

Bienvenue sur Portfolio Builder !

Votre compte a été créé avec succès. Vous pouvez maintenant commencer à créer votre portfolio professionnel.

Pour vérifier votre email, cliquez sur le lien suivant :
{url_for('auth.verify_email', token=token, _external=True)}

Si vous n'avez pas créé de compte, ignorez cet email.

Cordialement,
L'équipe Portfolio Builder
        '''
        mail.send(msg)
    except Exception as e:
        current_app.logger.error(f"Erreur envoi email vérification: {e}")

def send_password_reset_email(user):
    """Envoyer email de réinitialisation de mot de passe"""
    try:
        token = user.get_reset_token()
        msg = Message(
            'Réinitialisation de votre mot de passe',
            sender=current_app.config['MAIL_USERNAME'],
            recipients=[user.email]
        )
        msg.body = f'''
Bonjour {user.get_full_name()},

Vous avez demandé la réinitialisation de votre mot de passe.

Pour réinitialiser votre mot de passe, cliquez sur le lien suivant :
{url_for('auth.reset_password', token=token, _external=True)}

Ce lien expire dans 1 heure.

Si vous n'avez pas demandé cette réinitialisation, ignorez cet email.

Cordialement,
L'équipe Portfolio Builder
        '''
        mail.send(msg)
    except Exception as e:
        current_app.logger.error(f"Erreur envoi email reset: {e}")
