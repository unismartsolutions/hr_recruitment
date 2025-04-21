/**
 * HR Recruitment System - Search JavaScript
 * Handles candidate search and job matching functionality
 */

// Store filter tags
let filterSkills = [];
let filterCertifications = [];

// Initialize the search page when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const searchForm = document.getElementById('searchForm');
    const matchForm = document.getElementById('matchForm');
    const toggleFiltersBtn = document.getElementById('toggleFilters');
    const searchFilters = document.getElementById('searchFilters');
    const searchResults = document.getElementById('searchResults');
    const matchResults = document.getElementById('matchResults');
    const candidateModal = document.getElementById('candidateModal');
    const candidateModalBody = document.getElementById('candidateModalBody');
    
    // Tag input elements
    const skillsFilterContainer = document.getElementById('skillsFilterContainer');
    const skillsFilterInput = document.getElementById('skillsFilterInput');
    const certsFilterContainer = document.getElementById('certsFilterContainer');
    const certsFilterInput = document.getElementById('certsFilterInput');
    
    // Set up event listeners only if elements exist (we're on the search page)
    if (searchForm && matchForm) {
        initializeSearchPage();
    }
    
    /**
     * Initialize the search page with all event listeners
     */
    function initializeSearchPage() {
        // Toggle advanced filters
        toggleFiltersBtn.addEventListener('click', () => {
            searchFilters.style.display = searchFilters.style.display === 'none' ? 'block' : 'none';
        });
        
        // Search form submission
        searchForm.addEventListener('submit', (e) => {
            e.preventDefault();
            searchCandidates();
        });
        
        // Match form submission
        matchForm.addEventListener('submit', (e) => {
            e.preventDefault();
            matchJobRequirements();
        });
        
        // Skills filter input
        skillsFilterInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && skillsFilterInput.value.trim()) {
                e.preventDefault();
                addSkillFilter(skillsFilterInput.value.trim());
                skillsFilterInput.value = '';
            }
        });
        
        // Certifications filter input
        certsFilterInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && certsFilterInput.value.trim()) {
                e.preventDefault();
                addCertFilter(certsFilterInput.value.trim());
                certsFilterInput.value = '';
            }
        });
        
        // Modal behavior
        candidateModal.addEventListener('hidden.bs.modal', () => {
            candidateModalBody.innerHTML = `
                <div class="text-center">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                </div>
            `;
        });
    }
    
    /**
     * Add a skill to the filter skills list
     * @param {string} skill - Skill name
     */
    function addSkillFilter(skill) {
        if (filterSkills.includes(skill)) return;
        
        filterSkills.push(skill);
        const tagElement = createTagElement(skill, removeSkillFilter);
        skillsFilterContainer.insertBefore(tagElement, skillsFilterInput);
    }
    
    /**
     * Remove a skill from the filter skills list
     * @param {string} skill - Skill name
     */
    function removeSkillFilter(skill) {
        filterSkills = filterSkills.filter(s => s !== skill);
    }
    
    /**
     * Add a certification to the filter certifications list
     * @param {string} cert - Certification name
     */
    function addCertFilter(cert) {
        if (filterCertifications.includes(cert)) return;
        
        filterCertifications.push(cert);
        const tagElement = createTagElement(cert, removeCertFilter);
        certsFilterContainer.insertBefore(tagElement, certsFilterInput);
    }
    
    /**
     * Remove a certification from the filter certifications list
     * @param {string} cert - Certification name
     */
    function removeCertFilter(cert) {
        filterCertifications = filterCertifications.filter(c => c !== cert);
    }
    
    /**
     * Search for candidates with the specified filters
     */
    function searchCandidates() {
        // Show loading
        showLoading('Searching candidates...');
        
        // Prepare search params
        const searchParams = {
            query: document.getElementById('searchQuery').value,
            skills: filterSkills,
            experience_level: document.getElementById('experienceLevelFilter').value,
            industry: document.getElementById('industryFilter').value,
            certifications: filterCertifications
        };
        
        // Send search request
        fetch('/api/search', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(searchParams)
        })
        .then(response => response.json())
        .then(data => {
            hideLoading();
            
            if (data.error) {
                showAlert(data.error, 'danger');
                return;
            }
            
            displaySearchResults(data);
        })
        .catch(error => {
            hideLoading();
            showAlert('Error searching candidates. Please try again.', 'danger');
            console.error('Error:', error);
        });
    }
    
    /**
     * Match candidates to job requirements
     */
    function matchJobRequirements() {
        const jobRequirements = document.getElementById('jobRequirements').value.trim();
        
        if (!jobRequirements) {
            showAlert('Please enter job requirements.', 'warning');
            return;
        }
        
        // Show loading
        showLoading('Matching candidates...');
        
        // Send match request
        fetch('/api/match-job', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                requirements: jobRequirements
            })
        })
        .then(response => response.json())
        .then(data => {
            hideLoading();
            
            if (data.error) {
                showAlert(data.error, 'danger');
                return;
            }
            
            displayMatchResults(data);
        })
        .catch(error => {
            hideLoading();
            showAlert('Error matching candidates. Please try again.', 'danger');
            console.error('Error:', error);
        });
    }
    
    /**
     * Display search results
     * @param {Array} candidates - List of candidate objects
     */
    function displaySearchResults(candidates) {
        if (!candidates || candidates.length === 0) {
            searchResults.innerHTML = `
                <div class="text-center py-5 text-muted">
                    <i class="fas fa-search fa-4x mb-3"></i>
                    <h4>No candidates found</h4>
                    <p>Try different search criteria.</p>
                </div>
            `;
            return;
        }
        
        let resultsHtml = `
            <h5 class="mb-3">Found ${candidates.length} candidate(s)</h5>
            <div class="row">
        `;
        
        candidates.forEach(candidate => {
            resultsHtml += createCandidateCard(candidate);
        });
        
        resultsHtml += '</div>';
        searchResults.innerHTML = resultsHtml;
        
        // Add event listeners to view buttons
        document.querySelectorAll('.view-candidate-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const candidateId = btn.getAttribute('data-id');
                viewCandidateDetails(candidateId);
            });
        });
    }
    
    /**
     * Display job matching results
     * @param {Array} candidates - List of candidate objects with match scores
     */
    function displayMatchResults(candidates) {
        if (!candidates || candidates.length === 0) {
            matchResults.innerHTML = `
                <div class="text-center py-5 text-muted">
                    <i class="fas fa-exclamation-circle fa-4x mb-3"></i>
                    <h4>No matching candidates found</h4>
                    <p>Try different job requirements or check if candidates are available in the system.</p>
                </div>
            `;
            return;
        }
        
        let resultsHtml = `
            <h5 class="mb-3">Found ${candidates.length} matching candidate(s)</h5>
            <div class="row">
        `;
        
        candidates.forEach(candidate => {
            resultsHtml += createMatchCard(candidate);
        });
        
        resultsHtml += '</div>';
        matchResults.innerHTML = resultsHtml;
        
        // Add event listeners to view buttons
        document.querySelectorAll('.view-candidate-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const candidateId = btn.getAttribute('data-id');
                viewCandidateDetails(candidateId);
            });
        });
    }
    
    /**
     * Create a candidate card for search results
     * @param {Object} candidate - Candidate object
     * @returns {string} HTML for candidate card
     */
    function createCandidateCard(candidate) {
        const skills = candidate.skills && candidate.skills.length > 0 
            ? candidate.skills.map(skill => `<span class="badge badge-skill">${skill}</span>`).join(' ')
            : '<span class="text-muted">No skills listed</span>';
            
        const certifications = candidate.certifications && candidate.certifications.length > 0 
            ? candidate.certifications.map(cert => `<span class="badge badge-certification">${cert}</span>`).join(' ')
            : '<span class="text-muted">No certifications</span>';
        
        return `
            <div class="col-md-6 mb-3">
                <div class="card candidate-card h-100">
                    <div class="card-body">
                        <h5 class="card-title">${candidate.name}</h5>
                        <p class="text-muted mb-2">
                            ${candidate.experience_level || ''} · ${candidate.industry || 'Industry not specified'}
                        </p>
                        <div class="mb-2">
                            <small class="text-muted">Skills:</small><br>
                            ${skills}
                        </div>
                        <div class="mb-3">
                            <small class="text-muted">Certifications:</small><br>
                            ${certifications}
                        </div>
                        <button class="btn btn-sm btn-outline-primary view-candidate-btn" 
                                data-id="${candidate.id}" data-bs-toggle="modal" data-bs-target="#candidateModal">
                            <i class="fas fa-user me-1"></i> View Details
                        </button>
                    </div>
                </div>
            </div>
        `;
    }
    
    /**
     * Create a candidate card for job matching results
     * @param {Object} candidate - Candidate object with match score
     * @returns {string} HTML for candidate card
     */
    function createMatchCard(candidate) {
        const scoreClass = getScoreClass(candidate.score);
        
        const skills = candidate.skills && candidate.skills.length > 0 
            ? candidate.skills.map(skill => `<span class="badge badge-skill">${skill}</span>`).join(' ')
            : '<span class="text-muted">No skills listed</span>';
            
        const certifications = candidate.certifications && candidate.certifications.length > 0 
            ? candidate.certifications.map(cert => `<span class="badge badge-certification">${cert}</span>`).join(' ')
            : '<span class="text-muted">No certifications</span>';
        
        return `
            <div class="col-md-6 mb-3">
                <div class="card candidate-card h-100">
                    <div class="card-body">
                        <div class="d-flex justify-content-between align-items-start mb-2">
                            <div>
                                <h5 class="card-title">${candidate.name}</h5>
                                <p class="text-muted mb-2">
                                    ${candidate.experience_level || ''} · ${candidate.industry || 'Industry not specified'}
                                </p>
                            </div>
                            <div class="score-badge ${scoreClass}">
                                ${Math.round(candidate.score)}
                            </div>
                        </div>
                        <div class="mb-2">
                            <small class="text-muted">Skills:</small><br>
                            ${skills}
                        </div>
                        <div class="mb-3">
                            <small class="text-muted">Certifications:</small><br>
                            ${certifications}
                        </div>
                        <button class="btn btn-sm btn-outline-primary view-candidate-btn" 
                                data-id="${candidate.id}" data-bs-toggle="modal" data-bs-target="#candidateModal">
                            <i class="fas fa-user me-1"></i> View Details
                        </button>
                    </div>
                </div>
            </div>
        `;
    }
    
    /**
     * View candidate details in modal
     * @param {number} candidateId - Candidate ID
     */
    function viewCandidateDetails(candidateId) {
        // Show candidate modal with loading spinner
        const candidateModalBS = new bootstrap.Modal(candidateModal);
        candidateModalBS.show();
        
        // Fetch candidate details
        fetch(`/candidates/${candidateId}`)
            .then(response => response.json())
            .then(candidate => {
                const skills = candidate.skills && candidate.skills.length > 0 
                    ? candidate.skills.map(skill => `<span class="badge badge-skill">${skill}</span>`).join(' ')
                    : '<span class="text-muted">No skills listed</span>';
                    
                const certifications = candidate.certifications && candidate.certifications.length > 0 
                    ? candidate.certifications.map(cert => `<span class="badge badge-certification">${cert}</span>`).join(' ')
                    : '<span class="text-muted">No certifications</span>';
                
                // Format date
                const formattedDate = formatDate(candidate.created_at);
                
                // Build modal content
                candidateModalBody.innerHTML = `
                    <div class="row mb-4">
                        <div class="col-md-6">
                            <h4>${candidate.name}</h4>
                            <p class="text-muted">
                                ${candidate.experience_level || ''} · ${candidate.industry || 'Industry not specified'}
                            </p>
                            <p>
                                <i class="fas fa-envelope me-2"></i> ${candidate.email || 'No email'}<br>
                                <i class="fas fa-phone me-2"></i> ${candidate.phone || 'No phone'}<br>
                                <i class="fas fa-calendar me-2"></i> Age: ${candidate.age || 'Not specified'}
                            </p>
                        </div>
                        <div class="col-md-6">
                            <div class="mb-3">
                                <h6>Skills</h6>
                                <div>${skills}</div>
                            </div>
                            <div class="mb-3">
                                <h6>Certifications</h6>
                                <div>${certifications}</div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="row mb-3">
                        <div class="col-12">
                            <h6>Education</h6>
                            <p>${candidate.education || 'No education information available.'}</p>
                        </div>
                    </div>
                    
                    <div class="row mb-3">
                        <div class="col-12">
                            <h6>Experience</h6>
                            <p>${candidate.experience || 'No experience information available.'}</p>
                        </div>
                    </div>
                    
                    <div class="row">
                        <div class="col-12 text-muted">
                            <small>Added on ${formattedDate}</small>
                        </div>
                    </div>
                `;
            })
            .catch(error => {
                candidateModalBody.innerHTML = `
                    <div class="alert alert-danger">
                        Error loading candidate details. Please try again.
                    </div>
                `;
                console.error('Error:', error);
            });
    }
});
