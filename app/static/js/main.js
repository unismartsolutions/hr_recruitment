/**
 * HR Recruitment System - Main JavaScript
 * Common utility functions for the application
 */

// Initialize common UI elements when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Auto-close flash messages after 5 seconds
    initializeFlashMessages();
    
    // Initialize all tooltips
    initializeTooltips();
    
    // Initialize confirmation dialogs
    initializeConfirmations();
});

/**
 * Initialize flash message auto-close functionality
 */
function initializeFlashMessages() {
    setTimeout(function() {
        const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
        alerts.forEach(function(alert) {
            if (typeof bootstrap !== 'undefined') {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            } else {
                alert.style.display = 'none';
            }
        });
    }, 5000);
}

/**
 * Initialize Bootstrap tooltips
 */
function initializeTooltips() {
    if (typeof bootstrap !== 'undefined') {
        const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
        const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => 
            new bootstrap.Tooltip(tooltipTriggerEl)
        );
    }
}

/**
 * Initialize confirmation dialogs
 */
function initializeConfirmations() {
    document.querySelectorAll('[data-confirm]').forEach(element => {
        element.addEventListener('click', function(event) {
            if (!confirm(this.getAttribute('data-confirm'))) {
                event.preventDefault();
            }
        });
    });
}

/**
 * Show a flash message
 * @param {string} message - The message text
 * @param {string} type - Message type (success, info, warning, danger)
 */
function showAlert(message, type = 'info') {
    const alertsContainer = document.querySelector('.flash-messages');
    
    if (!alertsContainer) {
        console.error('Flash messages container not found');
        return;
    }
    
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    alertsContainer.appendChild(alertDiv);
    
    // Auto close after 5 seconds
    setTimeout(() => {
        if (typeof bootstrap !== 'undefined') {
            const bsAlert = new bootstrap.Alert(alertDiv);
            bsAlert.close();
        } else {
            alertDiv.style.display = 'none';
            setTimeout(() => {
                alertDiv.remove();
            }, 500);
        }
    }, 5000);
}

/**
 * Format date to a readable string
 * @param {string} dateString - ISO date string
 * @param {boolean} includeTime - Whether to include time
 * @returns {string} Formatted date string
 */
function formatDate(dateString, includeTime = false) {
    if (!dateString) return '';
    
    const date = new Date(dateString);
    const options = { 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric' 
    };
    
    if (includeTime) {
        options.hour = '2-digit';
        options.minute = '2-digit';
    }
    
    return date.toLocaleDateString('en-US', options);
}

/**
 * Debounce function to limit how often a function can be called
 * @param {Function} func - Function to debounce
 * @param {number} wait - Wait time in milliseconds
 * @returns {Function} Debounced function
 */
function debounce(func, wait = 300) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Make an API request with proper error handling
 * @param {string} url - API endpoint
 * @param {Object} options - Fetch options
 * @returns {Promise} Promise with response data
 */
async function apiRequest(url, options = {}) {
    try {
        const response = await fetch(url, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Something went wrong');
        }
        
        return data;
    } catch (error) {
        console.error('API request error:', error);
        showAlert(error.message, 'danger');
        throw error;
    }
}

/**
 * Create a tag element for tag inputs
 * @param {string} text - Tag text
 * @param {Function} removeCallback - Callback when tag is removed
 * @returns {HTMLElement} Tag element
 */
function createTagElement(text, removeCallback) {
    const tag = document.createElement('div');
    tag.className = 'tag';
    tag.innerHTML = `${text} <span class="remove">&times;</span>`;
    
    const removeBtn = tag.querySelector('.remove');
    removeBtn.addEventListener('click', () => {
        tag.remove();
        if (typeof removeCallback === 'function') {
            removeCallback(text);
        }
    });
    
    return tag;
}

/**
 * Convert form data to JSON object
 * @param {HTMLFormElement} form - Form element
 * @returns {Object} Form data as object
 */
function formToJson(form) {
    const formData = new FormData(form);
    const jsonData = {};
    
    for (const [key, value] of formData.entries()) {
        jsonData[key] = value;
    }
    
    return jsonData;
}

/**
 * Get color class based on score
 * @param {number} score - Score value (0-100)
 * @returns {string} Bootstrap color class
 */
function getScoreClass(score) {
    if (score >= 80) return 'bg-success text-white';
    if (score >= 60) return 'bg-primary text-white';
    if (score >= 40) return 'bg-warning text-dark';
    return 'bg-danger text-white';
}

/**
 * Truncate text to specified length
 * @param {string} text - Text to truncate
 * @param {number} length - Maximum length
 * @returns {string} Truncated text
 */
function truncateText(text, length = 100) {
    if (!text || text.length <= length) return text;
    return text.substring(0, length) + '...';
}

/**
 * Check if an element is in viewport
 * @param {HTMLElement} el - Element to check
 * @returns {boolean} True if element is in viewport
 */
function isInViewport(el) {
    const rect = el.getBoundingClientRect();
    return (
        rect.top >= 0 &&
        rect.left >= 0 &&
        rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
        rect.right <= (window.innerWidth || document.documentElement.clientWidth)
    );
}

/**
 * Show loading overlay
 * @param {string} message - Loading message
 */
function showLoading(message = 'Loading...') {
    let overlay = document.getElementById('loadingOverlay');
    
    if (!overlay) {
        overlay = document.createElement('div');
        overlay.id = 'loadingOverlay';
        overlay.className = 'loading-overlay';
        overlay.innerHTML = `
            <div class="spinner-container">
                <div class="spinner-border text-primary mb-3" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <h5 id="loadingText">${message}</h5>
                <p class="text-muted">Please wait...</p>
            </div>
        `;
        document.body.appendChild(overlay);
    } else {
        document.getElementById('loadingText').textContent = message;
        overlay.classList.remove('hidden');
    }
}

/**
 * Hide loading overlay
 */
function hideLoading() {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) {
        overlay.classList.add('hidden');
    }
}
