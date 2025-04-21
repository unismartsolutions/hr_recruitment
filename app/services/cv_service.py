import os
import PyPDF2
from werkzeug.utils import secure_filename
from flask import current_app
import uuid
import re

def allowed_file(filename):
    """Check if file has PDF extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'pdf'

def save_resume(file):
    """Save uploaded resume to disk with unique filename"""
    if not file or not allowed_file(file.filename):
        return None
    
    # Create a unique filename to prevent collisions
    original_filename = secure_filename(file.filename)
    filename = f"{uuid.uuid4()}_{original_filename}"
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    
    try:
        file.save(file_path)
        return file_path
    except Exception as e:
        current_app.logger.error(f"Error saving file: {e}")
        return None

def extract_text_from_pdf(file_path):
    """Extract all text from PDF file"""
    if not file_path or not os.path.exists(file_path):
        return ""
    
    text = ""
    try:
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        current_app.logger.error(f"Error extracting text from PDF: {e}")
        return ""
    
    return text

def extract_contact_info(text):
    """Extract basic contact information from text"""
    # Basic patterns for email and phone
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    phone_pattern = r'(\+\d{1,3}[-.\s]?)?(\(?\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{4}'
    
    # Extract email and phone
    email = re.search(email_pattern, text)
    phone = re.search(phone_pattern, text)
    
    return {
        'email': email.group(0) if email else None,
        'phone': phone.group(0) if phone else None
    }

def clean_text(text):
    """Clean extracted text for better processing"""
    # Replace multiple whitespace with single space
    text = re.sub(r'\s+', ' ', text)
    # Remove special characters
    text = re.sub(r'[^\w\s@.+-]', ' ', text)
    return text.strip()
