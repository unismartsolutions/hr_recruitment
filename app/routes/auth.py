from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.urls import url_parse
from ..models import User
from .. import db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
def index():
    """Home page route - redirects to login if not authenticated"""
    if current_user.is_authenticated:
        return redirect(url_for('candidates.upload'))
    return redirect(url_for('auth.login'))

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login route"""
    # Redirect if user already logged in
    if current_user.is_authenticated:
        return redirect(url_for('candidates.upload'))
    
    # Handle login form submission
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember_me = 'remember_me' in request.form
        
        # Validate form data
        if not username or not password:
            flash('Please enter username and password', 'error')
            return render_template('login.html')
        
        # Authenticate user
        user = User.query.filter_by(username=username).first()
        if user is None or not user.check_password(password):
            flash('Invalid username or password', 'error')
            return render_template('login.html')
        
        # Login user and redirect
        login_user(user, remember=remember_me)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('candidates.upload')
        return redirect(next_page)
    
    # Display login form
    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """User logout route"""
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('auth.login'))
