// Main JavaScript file for SproutsProject

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Auto-hide alerts after 5 seconds
    setTimeout(function() {
        var alerts = document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);

    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Form validation enhancement
    const forms = document.querySelectorAll('.needs-validation');
    Array.prototype.slice.call(forms).forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });

    // Application status update functionality
    const statusButtons = document.querySelectorAll('.update-status-btn');
    statusButtons.forEach(button => {
        button.addEventListener('click', function() {
            const applicationId = this.dataset.applicationId;
            const newStatus = this.dataset.status;
            updateApplicationStatus(applicationId, newStatus);
        });
    });

    // Withdraw application functionality
    const withdrawButtons = document.querySelectorAll('.withdraw-application-btn');
    withdrawButtons.forEach(button => {
        button.addEventListener('click', function() {
            const applicationId = this.dataset.applicationId;
            if (confirm('Are you sure you want to withdraw this application?')) {
                withdrawApplication(applicationId);
            }
        });
    });

    // Toggle internship active status
    const toggleButtons = document.querySelectorAll('.toggle-internship-btn');
    toggleButtons.forEach(button => {
        button.addEventListener('click', function() {
            const internshipId = this.dataset.internshipId;
            toggleInternshipStatus(internshipId);
        });
    });
});

// Function to update application status
function updateApplicationStatus(applicationId, status, notes = '') {
    const data = {
        status: status,
        notes: notes
    };

    fetch(`/restaurant/applications/${applicationId}/update_status`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken()
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showAlert('success', data.message);
            // Refresh the page or update the UI
            setTimeout(() => {
                location.reload();
            }, 1000);
        } else {
            showAlert('danger', data.error || 'An error occurred');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showAlert('danger', 'An error occurred while updating the application status');
    });
}

// Function to withdraw application
function withdrawApplication(applicationId) {
    fetch(`/intern/withdraw_application/${applicationId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken()
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showAlert('success', data.message);
            // Refresh the page or update the UI
            setTimeout(() => {
                location.reload();
            }, 1000);
        } else {
            showAlert('danger', data.error || 'An error occurred');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showAlert('danger', 'An error occurred while withdrawing the application');
    });
}

// Function to toggle internship status
function toggleInternshipStatus(internshipId) {
    fetch(`/restaurant/internships/${internshipId}/toggle_active`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken()
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showAlert('success', data.message);
            // Refresh the page or update the UI
            setTimeout(() => {
                location.reload();
            }, 1000);
        } else {
            showAlert('danger', data.error || 'An error occurred');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showAlert('danger', 'An error occurred while updating the internship status');
    });
}

// Function to show alert messages
function showAlert(type, message) {
    const alertContainer = document.getElementById('alert-container') || createAlertContainer();
    
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    alertContainer.appendChild(alertDiv);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.parentNode.removeChild(alertDiv);
        }
    }, 5000);
}

// Function to create alert container if it doesn't exist
function createAlertContainer() {
    const container = document.createElement('div');
    container.id = 'alert-container';
    container.className = 'container mt-3';
    
    const main = document.querySelector('main');
    if (main) {
        main.insertBefore(container, main.firstChild);
    } else {
        document.body.insertBefore(container, document.body.firstChild);
    }
    
    return container;
}

// Function to get CSRF token
function getCsrfToken() {
    const token = document.querySelector('meta[name="csrf-token"]');
    return token ? token.getAttribute('content') : '';
}

// Function to format dates
function formatDate(dateString) {
    const options = { 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric' 
    };
    return new Date(dateString).toLocaleDateString(undefined, options);
}

// Function to format currency
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
}

// Function to truncate text
function truncateText(text, maxLength) {
    if (text.length <= maxLength) {
        return text;
    }
    return text.substr(0, maxLength) + '...';
}

// Function to validate email
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

// Function to validate phone number
function isValidPhone(phone) {
    const phoneRegex = /^[\+]?[1-9][\d]{0,15}$/;
    return phoneRegex.test(phone.replace(/[\s\-\(\)]/g, ''));
}

// Function to show loading spinner
function showLoading(element) {
    const originalContent = element.innerHTML;
    element.innerHTML = '<span class="loading"></span> Loading...';
    element.disabled = true;
    return originalContent;
}

// Function to hide loading spinner
function hideLoading(element, originalContent) {
    element.innerHTML = originalContent;
    element.disabled = false;
}

// Export functions for use in other scripts
window.SproutsProject = {
    updateApplicationStatus,
    withdrawApplication,
    toggleInternshipStatus,
    showAlert,
    formatDate,
    formatCurrency,
    truncateText,
    isValidEmail,
    isValidPhone,
    showLoading,
    hideLoading
};
