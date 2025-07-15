"""
OAuth integration for social login providers
Supports Google, Apple, Facebook authentication
"""

import os
from flask import Blueprint, redirect, url_for, flash, session, request
from flask_login import login_user, current_user
from authlib.integrations.flask_client import OAuth
from models import User, db

# Create OAuth blueprint
oauth_bp = Blueprint('oauth', __name__, url_prefix='/auth')

# Initialize OAuth
oauth = OAuth()

def init_oauth(app):
    """Initialize OAuth with Flask app"""
    oauth.init_app(app)
    
    # Google OAuth
    oauth.register(
        name='google',
        client_id=os.environ.get('GOOGLE_CLIENT_ID'),
        client_secret=os.environ.get('GOOGLE_CLIENT_SECRET'),
        server_metadata_url='https://accounts.google.com/.well-known/openid_configuration',
        client_kwargs={
            'scope': 'openid email profile'
        }
    )
    
    # Apple OAuth (Sign in with Apple)
    oauth.register(
        name='apple',
        client_id=os.environ.get('APPLE_CLIENT_ID'),
        client_secret=os.environ.get('APPLE_CLIENT_SECRET'),
        server_metadata_url='https://appleid.apple.com/.well-known/openid_configuration',
        client_kwargs={
            'scope': 'name email',
            'response_mode': 'form_post'
        }
    )
    
    # Facebook OAuth
    oauth.register(
        name='facebook',
        client_id=os.environ.get('FACEBOOK_CLIENT_ID'),
        client_secret=os.environ.get('FACEBOOK_CLIENT_SECRET'),
        access_token_url='https://graph.facebook.com/oauth/access_token',
        authorize_url='https://www.facebook.com/dialog/oauth',
        api_base_url='https://graph.facebook.com/',
        client_kwargs={'scope': 'email'}
    )

@oauth_bp.route('/google')
def google_login():
    """Initiate Google OAuth login"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    redirect_uri = url_for('oauth.google_callback', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)

@oauth_bp.route('/google/callback')
def google_callback():
    """Handle Google OAuth callback"""
    try:
        token = oauth.google.authorize_access_token()
        user_info = token.get('userinfo')
        
        if user_info:
            user = User.query.filter_by(email=user_info['email']).first()
            
            if not user:
                # Create new user
                user = User(
                    email=user_info['email'],
                    first_name=user_info.get('given_name', ''),
                    last_name=user_info.get('family_name', ''),
                    oauth_provider='google',
                    oauth_id=user_info['sub']
                )
                # Set a random password for OAuth users
                user.set_password(os.urandom(24).hex())
                db.session.add(user)
                db.session.commit()
                flash('Account creato con successo tramite Google!', 'success')
            
            login_user(user)
            next_page = session.get('next_url', url_for('dashboard'))
            return redirect(next_page)
        
    except Exception as e:
        flash('Errore durante l\'autenticazione con Google. Riprova.', 'error')
        
    return redirect(url_for('login'))

@oauth_bp.route('/apple')
def apple_login():
    """Initiate Apple OAuth login"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    redirect_uri = url_for('oauth.apple_callback', _external=True)
    return oauth.apple.authorize_redirect(redirect_uri)

@oauth_bp.route('/apple/callback', methods=['GET', 'POST'])
def apple_callback():
    """Handle Apple OAuth callback"""
    try:
        token = oauth.apple.authorize_access_token()
        user_info = token.get('userinfo')
        
        if user_info:
            user = User.query.filter_by(email=user_info['email']).first()
            
            if not user:
                # Create new user
                name_parts = user_info.get('name', {})
                user = User(
                    email=user_info['email'],
                    first_name=name_parts.get('firstName', ''),
                    last_name=name_parts.get('lastName', ''),
                    oauth_provider='apple',
                    oauth_id=user_info['sub']
                )
                user.set_password(os.urandom(24).hex())
                db.session.add(user)
                db.session.commit()
                flash('Account creato con successo tramite Apple!', 'success')
            
            login_user(user)
            next_page = session.get('next_url', url_for('dashboard'))
            return redirect(next_page)
        
    except Exception as e:
        flash('Errore durante l\'autenticazione con Apple. Riprova.', 'error')
        
    return redirect(url_for('login'))

@oauth_bp.route('/facebook')
def facebook_login():
    """Initiate Facebook OAuth login"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    redirect_uri = url_for('oauth.facebook_callback', _external=True)
    return oauth.facebook.authorize_redirect(redirect_uri)

@oauth_bp.route('/facebook/callback')
def facebook_callback():
    """Handle Facebook OAuth callback"""
    try:
        token = oauth.facebook.authorize_access_token()
        
        # Get user info from Facebook
        resp = oauth.facebook.get('me?fields=id,name,email,first_name,last_name')
        user_info = resp.json()
        
        if user_info and user_info.get('email'):
            user = User.query.filter_by(email=user_info['email']).first()
            
            if not user:
                # Create new user
                user = User(
                    email=user_info['email'],
                    first_name=user_info.get('first_name', ''),
                    last_name=user_info.get('last_name', ''),
                    oauth_provider='facebook',
                    oauth_id=user_info['id']
                )
                user.set_password(os.urandom(24).hex())
                db.session.add(user)
                db.session.commit()
                flash('Account creato con successo tramite Facebook!', 'success')
            
            login_user(user)
            next_page = session.get('next_url', url_for('dashboard'))
            return redirect(next_page)
        
    except Exception as e:
        flash('Errore durante l\'autenticazione con Facebook. Riprova.', 'error')
        
    return redirect(url_for('login'))

@oauth_bp.route('/disconnect/<provider>')
def disconnect_oauth(provider):
    """Disconnect OAuth provider from account"""
    if current_user.is_authenticated and current_user.oauth_provider == provider:
        # Don't allow disconnecting if it's the only login method
        if not current_user.password_hash:
            flash('Impossibile disconnettere l\'unico metodo di accesso. Imposta prima una password.', 'error')
            return redirect(url_for('profile'))
        
        current_user.oauth_provider = None
        current_user.oauth_id = None
        db.session.commit()
        flash(f'Account {provider} disconnesso con successo.', 'success')
    
    return redirect(url_for('profile'))