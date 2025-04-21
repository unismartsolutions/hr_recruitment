"""
Authentication service for the HR Recruitment System.
Handles user authentication, registration, and password management.
"""
from flask import current_app
from werkzeug.security import generate_password_hash
from ..models import User
from .. import db

def verify_user(username, password):
    """
    Verify user credentials.
    
    Args:
        username (str): Username or email
        password (str): Password
        
    Returns:
        User or None: User object if credentials are valid, None otherwise
    """
    # Check if username is actually an email
    if '@' in username:
        user = User.query.filter_by(email=username).first()
    else:
        user = User.query.filter_by(username=username).first()
    
    # Verify password
    if user and user.check_password(password):
        return user
    
    return None

def create_user(username, email, password, is_admin=False):
    """
    Create a new user.
    
    Args:
        username (str): Username
        email (str): Email address
        password (str): Password
        is_admin (bool): Admin status
        
    Returns:
        (User, str): Tuple of user object and status message
    """
    # Validate inputs
    if not username or not email or not password:
        return None, "All fields are required"
    
    # Check if user already exists
    if User.query.filter_by(username=username).first():
        return None, f"Username '{username}' is already taken"
    
    if User.query.filter_by(email=email).first():
        return None, f"Email '{email}' is already registered"
    
    # Create user
    user = User(
        username=username,
        email=email,
        is_admin=is_admin
    )
    user.set_password(password)
    
    try:
        db.session.add(user)
        db.session.commit()
        return user, "User created successfully"
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating user: {str(e)}")
        return None, f"Error creating user: {str(e)}"

def change_password(user, current_password, new_password):
    """
    Change user password.
    
    Args:
        user (User): User object
        current_password (str): Current password
        new_password (str): New password
        
    Returns:
        (bool, str): Success status and message
    """
    # Verify current password
    if not user.check_password(current_password):
        return False, "Current password is incorrect"
    
    # Update password
    user.set_password(new_password)
    
    try:
        db.session.commit()
        return True, "Password changed successfully"
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error changing password: {str(e)}")
        return False, f"Error changing password: {str(e)}"

def reset_password(user, new_password):
    """
    Reset user password (admin function).
    
    Args:
        user (User): User object
        new_password (str): New password
        
    Returns:
        (bool, str): Success status and message
    """
    # Update password
    user.set_password(new_password)
    
    try:
        db.session.commit()
        return True, "Password reset successfully"
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error resetting password: {str(e)}")
        return False, f"Error resetting password: {str(e)}"

def get_user_by_id(user_id):
    """
    Get user by ID.
    
    Args:
        user_id (int): User ID
        
    Returns:
        User or None: User object if found, None otherwise
    """
    return User.query.get(user_id)

def get_user_by_username(username):
    """
    Get user by username.
    
    Args:
        username (str): Username
        
    Returns:
        User or None: User object if found, None otherwise
    """
    return User.query.filter_by(username=username).first()

def get_user_by_email(email):
    """
    Get user by email.
    
    Args:
        email (str): Email address
        
    Returns:
        User or None: User object if found, None otherwise
    """
    return User.query.filter_by(email=email).first()

def get_all_users():
    """
    Get all users.
    
    Returns:
        list: List of User objects
    """
    return User.query.all()
