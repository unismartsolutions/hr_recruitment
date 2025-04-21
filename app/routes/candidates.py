from flask import Blueprint, render_template, request, jsonify, current_app, flash, redirect, url_for
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from ..models import Candidate
from .. import db
from ..services.cv_service import save_resume, extract_text_from_pdf, extract_contact_info, clean_text
from ..services.gpt_service import process_resume_with_gpt
import os
import json

candidates_bp = Blueprint('candidates', __name__)

@candidates_bp.route('/upload', methods=['GET'])
@login_required
def upload():
    """Render the CV upload page"""
    return render_template('upload.html')

@candidates_bp.route('/process-resume', methods=['POST'])
@login_required
def process_resume():
    """Process uploaded resume with GPT and return extracted information"""
    # Check if file part exists in request
    if 'resume' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['resume']
    # Check if file was selected
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Save the uploaded file
    file_path = save_resume(file)
    if not file_path:
        return jsonify({'error': 'Invalid file format. Only PDF files are allowed.'}), 400
    
    try:
        # Extract text from PDF
        resume_text = extract_text_from_pdf(file_path)
        if not resume_text:
            return jsonify({'error': 'Failed to extract text from PDF'}), 500
        
        # Clean the extracted text
        cleaned_text = clean_text(resume_text)
        
        # Extract basic contact info using regex as a fallback
        contact_info = extract_contact_info(cleaned_text)
        
        # Process with GPT
        candidate_data = process_resume_with_gpt(cleaned_text)
        
        if not candidate_data:
            # If GPT fails, return basic info with error
            return jsonify({
                'error': 'Partial processing only. GPT analysis failed.',
                'email': contact_info.get('email'),
                'phone': contact_info.get('phone'),
                'resume_path': file_path
            }), 207  # 207 Multi-Status
        
        # Add resume path to the data
        candidate_data['resume_path'] = file_path
        
        # Return the processed data
        return jsonify(candidate_data)
    
    except Exception as e:
        current_app.logger.error(f"Error in process_resume: {str(e)}")
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

@candidates_bp.route('/save-candidate', methods=['POST'])
@login_required
def save_candidate():
    """Save candidate information to database"""
    try:
        # Get data from request
        data = request.json
        
        if not data or not data.get('name'):
            return jsonify({'error': 'Invalid data. Name is required.'}), 400
        
        # Check if candidate with this email already exists
        if data.get('email'):
            existing_candidate = Candidate.query.filter_by(email=data['email']).first()
            if existing_candidate:
                return jsonify({'error': 'A candidate with this email already exists'}), 409
        
        # Create new candidate
        candidate = Candidate(
            name=data.get('name'),
            email=data.get('email'),
            phone=data.get('phone'),
            age=data.get('age') if data.get('age') else None,
            education=data.get('education'),
            skills=data.get('skills', []),
            experience=data.get('experience'),
            experience_level=data.get('experience_level'),
            industry=data.get('industry'),
            certifications=data.get('certifications', []),
            resume_path=data.get('resume_path'),
            created_by=current_user.id
        )
        
        # Add to database
        db.session.add(candidate)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Candidate saved successfully',
            'id': candidate.id
        })
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error in save_candidate: {str(e)}")
        return jsonify({'error': f'Failed to save candidate: {str(e)}'}), 500

@candidates_bp.route('/candidates/<int:candidate_id>', methods=['GET'])
@login_required
def get_candidate(candidate_id):
    """Get candidate details by ID"""
    candidate = Candidate.query.get_or_404(candidate_id)
    return jsonify(candidate.to_dict())

@candidates_bp.route('/candidates/<int:candidate_id>', methods=['DELETE'])
@login_required
def delete_candidate(candidate_id):
    """Delete a candidate"""
    candidate = Candidate.query.get_or_404(candidate_id)
    
    try:
        # Delete the resume file if it exists
        if candidate.resume_path and os.path.exists(candidate.resume_path):
            os.remove(candidate.resume_path)
        
        # Delete from database
        db.session.delete(candidate)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Candidate deleted successfully'})
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting candidate: {str(e)}")
        return jsonify({'error': f'Failed to delete candidate: {str(e)}'}), 500
