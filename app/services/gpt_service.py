
import json
import openai
from flask import current_app

def process_resume_with_gpt(resume_text):
    """
    Process resume text with OpenAI GPT model to extract structured information
    
    Args:
        resume_text (str): The extracted text from the resume
        
    Returns:
        dict: Structured candidate information
    """
    if not resume_text:
        return None
    
    # Set OpenAI API key from configuration
    openai.api_key = current_app.config['OPENAI_API_KEY']
    
    try:
        # Define the system prompt
        system_prompt = """
        You are an expert HR recruiter assistant specialized in analyzing CVs/resumes.
        Extract the following information from the provided resume text:
        
        1. Full Name
        2. Email address
        3. Phone number
        4. Skills (as a list)
        5. Work experience and determine level (Junior, Mid, Senior)
        6. Education details
        7. Professional certifications (especially note CA, CIMA, or CFA)
        8. Main industry experience
        9. Approximate age (if provided or can be inferred from graduation dates)
        
        Format your response ONLY as a clean JSON object with the following structure:
        {
            "name": "Full Name",
            "email": "email@example.com",
            "phone": "Phone number",
            "skills": ["Skill 1", "Skill 2", "Skill 3"],
            "experience": "Summary of experience",
            "experience_level": "Junior/Mid/Senior",
            "education": "Education details",
            "certifications": ["Certification 1", "Certification 2"],
            "industry": "Main industry",
            "age": null or approximate age as integer
        }
        
        Make your best inference if information is not explicitly stated. 
        For certifications, look specifically for accounting/finance qualifications like CA, CIMA, or CFA.
        Include only the JSON in your response, no additional text.
        """
        
        # Call OpenAI API
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": resume_text}
            ],
            temperature=0.2,  # Lower temperature for more consistent results
            response_format={"type": "json_object"}  # Ensure JSON response
        )
        
        # Extract and parse the response
        gpt_response = response.choices[0].message.content
        candidate_data = json.loads(gpt_response)
        
        return candidate_data
        
    except Exception as e:
        current_app.logger.error(f"Error processing with GPT: {e}")
        return None

def rank_candidates_for_job(job_requirements, candidate_profiles):
    """
    Rank candidates based on job requirements using GPT
    
    Args:
        job_requirements (str): Job requirements description
        candidate_profiles (list): List of candidate profile dictionaries
        
    Returns:
        list: Ranked candidate profiles with score
    """
    if not job_requirements or not candidate_profiles:
        return []
    
    openai.api_key = current_app.config['OPENAI_API_KEY']
    
    system_prompt = """
    You are an expert HR recruiter specializing in candidate matching.
    You will receive job requirements followed by candidate profiles.
    Evaluate how well each candidate matches the job requirements on a scale of 0-100.
    Consider skills, experience level, education, certifications, and industry background.
    Focus particularly on relevant technical skills and domain knowledge.
    For finance roles, give higher importance to relevant certifications like CA, CIMA, or CFA.
    Return a JSON array of candidate IDs with their match scores, sorted from highest to lowest score.
    Format: [{"id": candidate_id, "score": match_score}, ...]
    """
    
    # Prepare candidate profiles for the prompt
    candidates_text = "\n\n".join([
        f"Candidate ID: {c['id']}\n" +
        f"Name: {c['name']}\n" +
        f"Skills: {', '.join(c['skills'])}\n" +
        f"Experience: {c['experience']}\n" +
        f"Experience Level: {c['experience_level']}\n" +
        f"Education: {c['education']}\n" +
        f"Certifications: {', '.join(c['certifications']) if c['certifications'] else 'None'}\n" +
        f"Industry: {c['industry']}"
        for c in candidate_profiles
    ])
    
    prompt = f"Job Requirements:\n{job_requirements}\n\nCandidates:\n{candidates_text}"
    
    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            response_format={"type": "json_object"}
        )
        
        # Parse the ranked results
        result = json.loads(response.choices[0].message.content)
        
        # Map the results back to full candidate profiles
        candidates_by_id = {c['id']: c for c in candidate_profiles}
        ranked_candidates = []
        
        for item in result:
            candidate_id = item['id']
            if candidate_id in candidates_by_id:
                candidate = candidates_by_id[candidate_id].copy()
                candidate['score'] = item['score']
                ranked_candidates.append(candidate)
        
        return ranked_candidates
        
    except Exception as e:
        current_app.logger.error(f"Error ranking candidates: {e}")
        return []
