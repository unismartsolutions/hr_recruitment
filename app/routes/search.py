from flask import Blueprint, render_template, request, jsonify, current_app
from flask_login import login_required
from sqlalchemy import or_, func, and_
from ..models import Candidate
from .. import db
from ..services.gpt_service import rank_candidates_for_job

search_bp = Blueprint('search', __name__)

@search_bp.route('/search', methods=['GET'])
@login_required
def search_page():
    """Render the search page"""
    return render_template('search.html')

@search_bp.route('/api/search', methods=['POST'])
@login_required
def search_candidates():
    """API endpoint for searching candidates"""
    data = request.json
    if not data:
        return jsonify({'error': 'No search parameters provided'}), 400
    
    # Get search parameters
    query = data.get('query', '').strip()
    skills = data.get('skills', [])
    experience_level = data.get('experience_level')
    industry = data.get('industry')
    certifications = data.get('certifications', [])
    
    # Start with base query
    candidates_query = Candidate.query
    
    # Apply filters if they exist
    if query:
        search_terms = query.split()
        search_filters = []
        for term in search_terms:
            term_filter = or_(
                Candidate.name.ilike(f'%{term}%'),
                Candidate.email.ilike(f'%{term}%'),
                Candidate.phone.ilike(f'%{term}%'),
                Candidate.industry.ilike(f'%{term}%'),
                Candidate.experience.ilike(f'%{term}%'),
                Candidate.education.ilike(f'%{term}%')
            )
            search_filters.append(term_filter)
        candidates_query = candidates_query.filter(and_(*search_filters))
    
    # Filter by skills
    if skills:
        for skill in skills:
            candidates_query = candidates_query.filter(
                func.array_to_string(Candidate.skills, ',').ilike(f'%{skill}%')
            )
    
    # Filter by experience level
    if experience_level:
        candidates_query = candidates_query.filter(
            Candidate.experience_level.ilike(f'%{experience_level}%')
        )
    
    # Filter by industry
    if industry:
        candidates_query = candidates_query.filter(
            Candidate.industry.ilike(f'%{industry}%')
        )
    
    # Filter by certifications
    if certifications:
        for cert in certifications:
            candidates_query = candidates_query.filter(
                func.array_to_string(Candidate.certifications, ',').ilike(f'%{cert}%')
            )
    
    # Execute query
    try:
        candidates = candidates_query.all()
        
        # Convert to dictionary
        result = [candidate.to_dict() for candidate in candidates]
        return jsonify(result)
    
    except Exception as e:
        current_app.logger.error(f"Error in search_candidates: {str(e)}")
        return jsonify({'error': f'Search failed: {str(e)}'}), 500

@search_bp.route('/api/match-job', methods=['POST'])
@login_required
def match_job():
    """Match candidates to job requirements using GPT"""
    data = request.json
    if not data or not data.get('requirements'):
        return jsonify({'error': 'No job requirements provided'}), 400
    
    job_requirements = data.get('requirements')
    
    try:
        # Get all candidates
        candidates = Candidate.query.all()
        
        if not candidates:
            return jsonify([])
        
        # Convert candidates to dictionary format
        candidate_profiles = [candidate.to_dict() for candidate in candidates]
        
        # Rank candidates for the job
        ranked_candidates = rank_candidates_for_job(job_requirements, candidate_profiles)
        
        return jsonify(ranked_candidates)
    
    except Exception as e:
        current_app.logger.error(f"Error in match_job: {str(e)}")
        return jsonify({'error': f'Job matching failed: {str(e)}'}), 500
