from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectField, DateField, FileField, HiddenField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional, URL, ValidationError
from models import User

class LoginForm(FlaskForm):
    """Formulaire de connexion"""
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Mot de passe', validators=[DataRequired()])
    remember_me = BooleanField('Se souvenir de moi')
    submit = SubmitField('Se connecter')

class RegisterForm(FlaskForm):
    """Formulaire d'inscription"""
    username = StringField('Nom d\'utilisateur', validators=[
        DataRequired(), 
        Length(min=3, max=30, message='Le nom d\'utilisateur doit contenir entre 3 et 30 caractères')
    ])
    email = StringField('Email', validators=[DataRequired(), Email()])
    first_name = StringField('Prénom', validators=[DataRequired(), Length(min=2, max=50)])
    last_name = StringField('Nom', validators=[DataRequired(), Length(min=2, max=50)])
    password = PasswordField('Mot de passe', validators=[
        DataRequired(), 
        Length(min=6, message='Le mot de passe doit contenir au moins 6 caractères')
    ])
    password2 = PasswordField('Confirmer le mot de passe', validators=[
        DataRequired(), 
        EqualTo('password', message='Les mots de passe ne correspondent pas')
    ])
    submit = SubmitField('S\'inscrire')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Ce nom d\'utilisateur est déjà pris. Veuillez en choisir un autre.')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Un compte avec cet email existe déjà.')

class ResetPasswordRequestForm(FlaskForm):
    """Formulaire de demande de réinitialisation de mot de passe"""
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Demander la réinitialisation')

class ResetPasswordForm(FlaskForm):
    """Formulaire de réinitialisation de mot de passe"""
    password = PasswordField('Nouveau mot de passe', validators=[
        DataRequired(), 
        Length(min=6, message='Le mot de passe doit contenir au moins 6 caractères')
    ])
    password2 = PasswordField('Confirmer le nouveau mot de passe', validators=[
        DataRequired(), 
        EqualTo('password', message='Les mots de passe ne correspondent pas')
    ])
    submit = SubmitField('Réinitialiser le mot de passe')

class PortfolioForm(FlaskForm):
    """Formulaire de création/modification de portfolio"""
    bio = TextAreaField('Biographie', validators=[Optional(), Length(max=1000)])
    location = StringField('Localisation', validators=[Optional(), Length(max=100)])
    phone = StringField('Téléphone', validators=[Optional(), Length(max=20)])
    website = StringField('Site web', validators=[Optional(), URL(), Length(max=200)])
    linkedin = StringField('LinkedIn', validators=[Optional(), URL(), Length(max=200)])
    github = StringField('GitHub', validators=[Optional(), URL(), Length(max=200)])
    profile_image = FileField('Photo de profil')
    submit = SubmitField('Sauvegarder')

class ProjectForm(FlaskForm):
    """Formulaire de création/modification de projet"""
    title = StringField('Titre du projet', validators=[DataRequired(), Length(max=200)])
    description = TextAreaField('Description', validators=[DataRequired()])
    technologies = StringField('Technologies (séparées par des virgules)', validators=[Optional()])
    github_url = StringField('Lien GitHub', validators=[Optional(), URL(), Length(max=200)])
    demo_url = StringField('Lien de démonstration', validators=[Optional(), URL(), Length(max=200)])
    featured = BooleanField('Projet mis en avant')
    submit = SubmitField('Sauvegarder')

class ExperienceForm(FlaskForm):
    """Formulaire de création/modification d'expérience"""
    title = StringField('Poste', validators=[DataRequired(), Length(max=200)])
    company = StringField('Entreprise', validators=[DataRequired(), Length(max=200)])
    location = StringField('Lieu', validators=[Optional(), Length(max=100)])
    start_date = DateField('Date de début', validators=[DataRequired()])
    end_date = DateField('Date de fin', validators=[Optional()])
    current = BooleanField('Poste actuel')
    description = TextAreaField('Description', validators=[DataRequired()])
    submit = SubmitField('Sauvegarder')

class EducationForm(FlaskForm):
    """Formulaire de création/modification de formation"""
    degree = StringField('Diplôme/Formation', validators=[DataRequired(), Length(max=200)])
    institution = StringField('Établissement', validators=[DataRequired(), Length(max=200)])
    location = StringField('Lieu', validators=[Optional(), Length(max=100)])
    start_date = DateField('Date de début', validators=[DataRequired()])
    end_date = DateField('Date de fin', validators=[Optional()])
    current = BooleanField('Formation en cours')
    description = TextAreaField('Description', validators=[Optional()])
    submit = SubmitField('Sauvegarder')

class SkillForm(FlaskForm):
    """Formulaire de création/modification de compétence"""
    name = StringField('Compétence', validators=[DataRequired(), Length(max=100)])
    level = SelectField('Niveau', choices=[
        ('Débutant', 'Débutant'),
        ('Intermédiaire', 'Intermédiaire'),
        ('Avancé', 'Avancé'),
        ('Expert', 'Expert')
    ], default='Intermédiaire')
    category = SelectField('Catégorie', choices=[
        ('Technique', 'Technique'),
        ('Langue', 'Langue'),
        ('Soft Skills', 'Soft Skills'),
        ('Autre', 'Autre')
    ], default='Technique')
    submit = SubmitField('Sauvegarder')

class CVUploadForm(FlaskForm):
    """Formulaire d'upload de CV"""
    cv_file = FileField('Fichier CV (PDF)', validators=[DataRequired()])
    submit = SubmitField('Télécharger le CV')

class CVImportForm(FlaskForm):
    """Formulaire d'import de CV existant"""
    cv_url = StringField('URL du CV', validators=[DataRequired(), URL()], 
                        render_kw={'placeholder': 'https://example.com/mon-cv.pdf'})
    cv_name = StringField('Nom du fichier', validators=[Optional()],
                         render_kw={'placeholder': 'CV_Mon_Nom.pdf'})
    submit = SubmitField('Importer le CV')

class ThemeForm(FlaskForm):
    """Formulaire de personnalisation du thème"""
    primary_color = StringField('Couleur principale', validators=[DataRequired()])
    secondary_color = StringField('Couleur secondaire', validators=[DataRequired()])
    font_family = SelectField('Police', choices=[
        ('Inter', 'Inter'),
        ('Roboto', 'Roboto'),
        ('Open Sans', 'Open Sans'),
        ('Lato', 'Lato'),
        ('Montserrat', 'Montserrat')
    ], default='Inter')
    layout = SelectField('Mise en page', choices=[
        ('modern', 'Moderne'),
        ('classic', 'Classique'),
        ('minimal', 'Minimaliste')
    ], default='modern')
    submit = SubmitField('Appliquer le thème')
