/**
 * HR Recruitment System - Upload CV JavaScript
 * Handles CV upload, processing, and candidate form submission
 */

// Store skills and certifications
let skills = [];
let certifications = [];

// Initialize the upload page when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const dropzone = document.getElementById('dropzone');
    const fileInput = document.getElementById('resumeUpload');
    const selectFileBtn = document.getElementById('selectFileBtn');
    const uploadSection = document.getElementById('uploadSection');
    const reviewSection = document.getElementById('reviewSection');
    const backBtn = document.getElementById('backBtn');
    const candidateForm = document.getElementById('candidateForm');
    const loadingOverlay = document.getElementById('loadingOverlay');
    const loadingText = document.getElementById('loadingText');
    
    // Tag input elements
    const skillsContainer = document.getElementById('skillsContainer');
    const skillInput = document.getElementById('skillInput');
    const certificationsContainer = document.getElementById('certificationsContainer');
    const certificationInput = document.getElementById('certificationInput');
    
    // Set up event listeners only if elements exist (we're on the upload page)
    if (dropzone && fileInput) {
        initializeUploadPage();
    }
    
    /**
     * Initialize the upload page with all event listeners
     */
    function initializeUploadPage() {
        // Set up drag and drop listeners
        dropzone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropzone.classList.add('drag-over');
        });
        
        dropzone.addEventListener('dragleave', () => {
            dropzone.classList.remove('drag-over');
        });
        
        dropzone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropzone.classList.remove('drag-over');
            
            if (e.dataTransfer.files.length) {
                handleFileUpload(e.dataTransfer.files[0]);
            }
        });
        
        // File selection button
        selectFileBtn.addEventListener('click', () => {
            fileInput.click();
        });
        
        // Handle file selection
        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length) {
                handleFileUpload(e.target.files[0]);
            }
        });
        
        // Back button
        backBtn.addEventListener('click', () => {
            uploadSection.classList.remove('hidden');
            reviewSection.classList.add('hidden');
        });
        
        // Tag input for skills
        skillInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && skillInput.value.trim()) {
                e.preventDefault();
                addSkill(skillInput.value.trim());
                skillInput.value = '';
            }
        });
        
        // Tag input for certifications
        certificationInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && certificationInput.value.trim()) {
                e.preventDefault();
                addCertification(certificationInput.value.trim());
                certificationInput.value = '';
            }
        });
        
        // Save candidate form
        candidateForm.addEventListener('submit', (e) => {
            e.preventDefault();
            saveCandidate();
        });
    }
    
    /**
     * Handle file upload process
     * @param {File} file - The uploaded file
     */
    function handleFileUpload(file) {
        // Check if file is PDF
        if (file.type !== 'application/pdf') {
            showAlert('Invalid file format. Please upload a PDF file.', 'danger');
            return;
        }
        
        // Show loading screen
        showLoading('Processing CV...');
        
        // Create form data
        const formData = new FormData();
        formData.append('resume', file);
        
        // Send to server
        fetch('/process-resume', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            hideLoading();
            
            if (data.error) {
                showAlert(data.error, 'danger');
                return;
            }
            
            // Fill form with extracted data
            fillCandidateForm(data);
            
            // Switch to review section
            uploadSection.classList.add('hidden');
            reviewSection.classList.remove('hidden');
        })
        .catch(error => {
            hideLoading();
            showAlert('Error processing the CV. Please try again.', 'danger');
            console.error('Error:', error);
        });
    }
    
    /**
     * Fill the candidate form with extracted data
     * @param {Object} data - Candidate data from API
     */
    function fillCandidateForm(data) {
        // Clear previous data
        skills = [];
        certifications = [];
        skillsContainer.innerHTML = '<input type="text" id="skillInput" placeholder="Type and press Enter">';
        certificationsContainer.innerHTML = '<input type="text" id="certificationInput" placeholder="Type and press Enter">';
        
        // Reassign input elements
        skillInput = document.getElementById('skillInput');
        certificationInput = document.getElementById('certificationInput');
        
        // Add event listeners again
        skillInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && skillInput.value.trim()) {
                e.preventDefault();
                addSkill(skillInput.value.trim());
                skillInput.value = '';
            }
        });
        
        certificationInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && certificationInput.value.trim()) {
                e.preventDefault();
                addCertification(certificationInput.value.trim());
                certificationInput.value = '';
            }
        });
        
        // Fill basic fields
        document.getElementById('name').value = data.name || '';
        document.getElementById('email').value = data.email || '';
        document.getElementById('phone').value = data.phone || '';
        document.getElementById('age').value = data.age || '';
        document.getElementById('experienceLevel').value = data.experience_level || '';
        document.getElementById('industry').value = data.industry || '';
        document.getElementById('education').value = data.education || '';
        document.getElementById('experience').value = data.experience || '';
        document.getElementById('resumePath').value = data.resume_path || '';
        
        // Add skills
        if (data.skills && Array.isArray(data.skills)) {
            data.skills.forEach(skill => {
                if (skill) addSkill(skill);
            });
        }
        
        // Add certifications
        if (data.certifications && Array.isArray(data.certifications)) {
            data.certifications.forEach(cert => {
                if (cert) addCertification(cert);
            });
        }
    }
    
    /**
     * Add a skill to the skills list
     * @param {string} skill - Skill name
     */
    function addSkill(skill) {
        if (skills.includes(skill)) return;
        
        skills.push(skill);
        const tagElement = createTagElement(skill, removeSkill);
        skillsContainer.insertBefore(tagElement, skillInput);
    }
    
    /**
     * Remove a skill from the skills list
     * @param {string} skill - Skill name
     */
    function removeSkill(skill) {
        skills = skills.filter(s => s !== skill);
    }
    
    /**
     * Add a certification to the certifications list
     * @param {string} cert - Certification name
     */
    function addCertification(cert) {
        if (certifications.includes(cert)) return;
        
        certifications.push(cert);
        const tagElement = createTagElement(cert, removeCertification);
        certificationsContainer.insertBefore(tagElement, certificationInput);
    }
    
    /**
     * Remove a certification from the certifications list
     * @param {string} cert - Certification name
     */
    function removeCertification(cert) {
        certifications = certifications.filter(c => c !== cert);
    }
    
    /**
     * Save candidate information to database
     */
    function saveCandidate() {
        // Get form data
        const formData = {
            name: document.getElementById('name').value,
            email: document.getElementById('email').value,
            phone: document.getElementById('phone').value,
            age: document.getElementById('age').value ? parseInt(document.getElementById('age').value) : null,
            experience_level: document.getElementById('experienceLevel').value,
            industry: document.getElementById('industry').value,
            education: document.getElementById('education').value,
            experience: document.getElementById('experience').value,
            skills: skills,
            certifications: certifications,
            resume_path: document.getElementById('resumePath').value
        };
        
        // Basic validation
        if (!formData.name) {
            showAlert('Candidate name is required', 'warning');
            return;
        }
        
        // Show loading screen
        showLoading('Saving candidate...');
        
        // Send to server
        fetch('/save-candidate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        })
        .then(response => response.json())
        .then(data => {
            hideLoading();
            
            if (data.error) {
                showAlert(data.error, 'danger');
                return;
            }
            
            // Show success message
            showAlert('Candidate saved successfully!', 'success');
            
            // Reset form and return to upload section
            candidateForm.reset();
            skills = [];
            certifications = [];
            skillsContainer.innerHTML = '<input type="text" id="skillInput" placeholder="Type and press Enter">';
            certificationsContainer.innerHTML = '<input type="text" id="certificationInput" placeholder="Type and press Enter">';
            
            // Reassign input elements
            skillInput = document.getElementById('skillInput');
            certificationInput = document.getElementById('certificationInput');
            
            // Add event listeners again
            skillInput.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' && skillInput.value.trim()) {
                    e.preventDefault();
                    addSkill(skillInput.value.trim());
                    skillInput.value = '';
                }
            });
            
            certificationInput.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' && certificationInput.value.trim()) {
                    e.preventDefault();
                    addCertification(certificationInput.value.trim());
                    certificationInput.value = '';
                }
            });
            
            // Show upload section
            uploadSection.classList.remove('hidden');
            reviewSection.classList.add('hidden');
        })
        .catch(error => {
            hideLoading();
            showAlert('Error saving candidate. Please try again.', 'danger');
            console.error('Error:', error);
        });
    }
});
