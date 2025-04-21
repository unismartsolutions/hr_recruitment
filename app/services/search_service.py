"""
Search service for the HR Recruitment System.
Provides functionality for searching and filtering candidates.
"""
from flask import current_app
from sqlalchemy import or_, and_, func, text
from ..models import Candidate, db

def basic_search(query_text, limit=100):
    """
    Perform a basic text search across candidate data.
    
    Args:
        query_text (str): Text to search for
        limit (int): Maximum number of results to return
        
    Returns:
        list: List of Candidate objects matching the search
    """
    if not query_text:
        return []
    
    # Split query into terms
    terms = query_text.strip().split()
    search_filters = []
    
    # Build filter for each term
    for term in terms:
        term_filter = or_(
            Candidate.name.ilike(f'%{term}%'),
            Candidate.email.ilike(f'%{term}%'),
            Candidate.phone.ilike(f'%{term}%'),
            Candidate.industry.ilike(f'%{term}%'),
            Candidate.experience.ilike(f'%{term}%'),
            Candidate.education.ilike(f'%{term}%'),
            Candidate.experience_level.ilike(f'%{term}%'),
            func.array_to_string(Candidate.skills, ',').ilike(f'%{term}%'),
            func.array_to_string(Candidate.certifications, ',').ilike(f'%{term}%')
        )
        search_filters.append(term_filter)
    
    # Combine filters with AND
    candidates = Candidate.query.filter(
        and_(*search_filters)
    ).limit(limit).all()
    
    return candidates

def advanced_search(filters, limit=100):
    """
    Perform an advanced search with multiple filters.
    
    Args:
        filters (dict): Dictionary of search filters
        limit (int): Maximum number of results to return
        
    Returns:
        list: List of Candidate objects matching the search
    """
    query = Candidate.query
    
    # Apply text search if provided
    if filters.get('query'):
        terms = filters['query'].strip().split()
        search_filters = []
        for term in terms:
            term_filter = or_(
                Candidate.name.ilike(f'%{term}%'),
                Candidate.email.ilike(f'%{term}%'),
                Candidate.phone.ilike(f'%{term}%'),
                Candidate.industry.ilike(f'%{term}%'),
                Candidate.experience.ilike(f'%{term}%'),
                Candidate.education.ilike(f'%{term}%')
            )
            search_filters.append(term_filter)
        query = query.filter(and_(*search_filters))
    
    # Filter by skills
    if filters.get('skills') and isinstance(filters['skills'], list):
        for skill in filters['skills']:
            query = query.filter(
                func.array_to_string(Candidate.skills, ',').ilike(f'%{skill}%')
            )
    
    # Filter by experience level
    if filters.get('experience_level'):
        query = query.filter(
            Candidate.experience_level.ilike(f'%{filters["experience_level"]}%')
        )
    
    # Filter by industry
    if filters.get('industry'):
        query = query.filter(
            Candidate.industry.ilike(f'%{filters["industry"]}%')
        )
    
    # Filter by certifications
    if filters.get('certifications') and isinstance(filters['certifications'], list):
        for cert in filters['certifications']:
            query = query.filter(
                func.array_to_string(Candidate.certifications, ',').ilike(f'%{cert}%')
            )
    
    # Filter by age range
    if filters.get('min_age'):
        query = query.filter(Candidate.age >= filters['min_age'])
    
    if filters.get('max_age'):
        query = query.filter(Candidate.age <= filters['max_age'])
    
    # Execute query with limit
    candidates = query.limit(limit).all()
    
    return candidates

def get_candidate_by_id(candidate_id):
    """
    Get candidate by ID.
    
    Args:
        candidate_id (int): Candidate ID
        
    Returns:
        Candidate or None: Candidate object if found, None otherwise
    """
    return Candidate.query.get(candidate_id)

def get_candidate_by_email(email):
    """
    Get candidate by email.
    
    Args:
        email (str): Email address
        
    Returns:
        Candidate or None: Candidate object if found, None otherwise
    """
    return Candidate.query.filter_by(email=email).first()

def get_all_candidates(limit=1000):
    """
    Get all candidates.
    
    Args:
        limit (int): Maximum number of results to return
        
    Returns:
        list: List of Candidate objects
    """
    return Candidate.query.limit(limit).all()

def get_candidates_stats():
    """
    Get statistics about candidates in the database.
    
    Returns:
        dict: Dictionary with statistics
    """
    try:
        total_count = Candidate.query.count()
        
        # Get counts by experience level
        experience_counts = db.session.query(
            Candidate.experience_level, 
            func.count(Candidate.id)
        ).group_by(Candidate.experience_level).all()
        
        experience_stats = {level: count for level, count in experience_counts}
        
        # Get top industries
        industry_counts = db.session.query(
            Candidate.industry, 
            func.count(Candidate.id)
        ).group_by(Candidate.industry).order_by(
            func.count(Candidate.id).desc()
        ).limit(5).all()
        
        top_industries = {industry: count for industry, count in industry_counts}
        
        # Get top skills (this is more complex because skills is an array)
        # Using raw SQL for this query
        top_skills_query = text("""
            SELECT skill, COUNT(*) as count
            FROM (
                SELECT unnest(skills) as skill
                FROM candidates
            ) as skill_list
            GROUP BY skill
            ORDER BY count DESC
            LIMIT 10
        """)
        
        top_skills_result = db.session.execute(top_skills_query)
        top_skills = {row[0]: row[1] for row in top_skills_result}
        
        # Get top certifications
        top_certs_query = text("""
            SELECT cert, COUNT(*) as count
            FROM (
                SELECT unnest(certifications) as cert
                FROM candidates
            ) as cert_list
            GROUP BY cert
            ORDER BY count DESC
            LIMIT 5
        """)
        
        top_certs_result = db.session.execute(top_certs_query)
        top_certifications = {row[0]: row[1] for row in top_certs_result}
        
        return {
            'total_candidates': total_count,
            'by_experience_level': experience_stats,
            'top_industries': top_industries,
            'top_skills': top_skills,
            'top_certifications': top_certifications
        }
        
    except Exception as e:
        current_app.logger.error(f"Error getting candidate stats: {str(e)}")
        return {
            'total_candidates': 0,
            'by_experience_level': {},
            'top_industries': {},
            'top_skills': {},
            'top_certifications': {}
        }

def delete_candidate(candidate_id):
    """
    Delete a candidate.
    
    Args:
        candidate_id (int): Candidate ID
        
    Returns:
        (bool, str): Success status and message
    """
    candidate = Candidate.query.get(candidate_id)
    if not candidate:
        return False, f"Candidate with ID {candidate_id} not found"
    
    try:
        db.session.delete(candidate)
        db.session.commit()
        return True, "Candidate deleted successfully"
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting candidate: {str(e)}")
        return False, f"Error deleting candidate: {str(e)}"
