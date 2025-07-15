// ShipConnect - JavaScript functionality
document.addEventListener('DOMContentLoaded', function() {
    
    // Initialize tooltips
    initializeTooltips();
    
    // Form validation enhancements
    enhanceFormValidation();
    
    // Auto-dismiss alerts
    autoDismissAlerts();
    
    // Card number formatting
    formatCardNumbers();
    
    // Price calculation helpers
    initializePriceCalculators();
    
    // Tracking updates
    initializeTrackingFeatures();
    
    // Modal enhancements
    enhanceModals();
    
    // Table enhancements
    enhanceDataTables();
    
    // Initialize rating interactions
    initializeRatingSystem();
    
    console.log('dabba initialized successfully');
});

/**
 * Initialize Bootstrap tooltips
 */
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/**
 * Enhance form validation with real-time feedback
 */
function enhanceFormValidation() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        // Real-time validation
        const inputs = form.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            input.addEventListener('blur', function() {
                validateField(this);
            });
            
            input.addEventListener('input', function() {
                if (this.classList.contains('is-invalid')) {
                    validateField(this);
                }
            });
        });
        
        // Form submission validation
        form.addEventListener('submit', function(e) {
            if (!validateForm(this)) {
                e.preventDefault();
                e.stopPropagation();
            }
            this.classList.add('was-validated');
        });
    });
}

/**
 * Validate individual field
 */
function validateField(field) {
    const value = field.value.trim();
    let isValid = true;
    let errorMessage = '';
    
    // Email validation
    if (field.type === 'email' && value) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(value)) {
            isValid = false;
            errorMessage = 'Please enter a valid email address';
        }
    }
    
    // Password validation
    if (field.name === 'password' && value) {
        if (value.length < 6) {
            isValid = false;
            errorMessage = 'Password must be at least 6 characters long';
        }
    }
    
    // Confirm password validation
    if (field.name === 'confirm_password' && value) {
        const passwordField = document.querySelector('input[name="password"]');
        if (passwordField && value !== passwordField.value) {
            isValid = false;
            errorMessage = 'Passwords do not match';
        }
    }
    
    // Weight validation
    if (field.name === 'weight' && value) {
        const weight = parseFloat(value);
        if (isNaN(weight) || weight <= 0 || weight > 10000) {
            isValid = false;
            errorMessage = 'Weight must be between 0.1 and 10000 kg';
        }
    }
    
    // Price validation
    if ((field.name === 'price' || field.name === 'proposed_price') && value) {
        const price = parseFloat(value);
        if (isNaN(price) || price <= 0) {
            isValid = false;
            errorMessage = 'Price must be a positive number';
        }
    }
    
    // Card number validation
    if (field.name === 'card_number' && value) {
        const cardRegex = /^\d{16}$/;
        if (!cardRegex.test(value.replace(/\s/g, ''))) {
            isValid = false;
            errorMessage = 'Card number must be 16 digits';
        }
    }
    
    // CVV validation
    if (field.name === 'cvv' && value) {
        const cvvRegex = /^\d{3,4}$/;
        if (!cvvRegex.test(value)) {
            isValid = false;
            errorMessage = 'CVV must be 3 or 4 digits';
        }
    }
    
    // Update field appearance
    updateFieldValidation(field, isValid, errorMessage);
    
    return isValid;
}

/**
 * Validate entire form
 */
function validateForm(form) {
    const inputs = form.querySelectorAll('input[required], select[required], textarea[required]');
    let isValid = true;
    
    inputs.forEach(input => {
        if (!validateField(input)) {
            isValid = false;
        }
    });
    
    return isValid;
}

/**
 * Update field validation appearance
 */
function updateFieldValidation(field, isValid, errorMessage) {
    const feedbackDiv = field.parentNode.querySelector('.invalid-feedback') || 
                       field.parentNode.querySelector('.text-danger');
    
    if (isValid) {
        field.classList.remove('is-invalid');
        field.classList.add('is-valid');
        if (feedbackDiv) {
            feedbackDiv.style.display = 'none';
        }
    } else {
        field.classList.remove('is-valid');
        field.classList.add('is-invalid');
        
        if (feedbackDiv) {
            feedbackDiv.textContent = errorMessage;
            feedbackDiv.style.display = 'block';
        } else if (errorMessage) {
            const newFeedback = document.createElement('div');
            newFeedback.className = 'invalid-feedback';
            newFeedback.textContent = errorMessage;
            field.parentNode.appendChild(newFeedback);
        }
    }
}

/**
 * Auto-dismiss alerts after delay
 */
function autoDismissAlerts() {
    const alerts = document.querySelectorAll('.alert:not(.alert-warning):not(.alert-info)');
    
    alerts.forEach(alert => {
        if (alert.classList.contains('alert-success')) {
            setTimeout(() => {
                const bsAlert = new bootstrap.Alert(alert);
                if (bsAlert) {
                    bsAlert.close();
                }
            }, 5000);
        }
    });
}

/**
 * Format card number input
 */
function formatCardNumbers() {
    const cardInputs = document.querySelectorAll('input[name="card_number"]');
    
    cardInputs.forEach(input => {
        input.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\s/g, '').replace(/\D/g, '');
            value = value.substring(0, 16);
            value = value.replace(/(.{4})/g, '$1 ');
            e.target.value = value.trim();
        });
        
        input.addEventListener('keydown', function(e) {
            // Allow backspace, delete, tab, escape, enter
            if ([8, 9, 27, 13, 46].indexOf(e.keyCode) !== -1 ||
                // Allow Ctrl+A, Ctrl+C, Ctrl+V, Ctrl+X
                (e.keyCode === 65 && e.ctrlKey === true) ||
                (e.keyCode === 67 && e.ctrlKey === true) ||
                (e.keyCode === 86 && e.ctrlKey === true) ||
                (e.keyCode === 88 && e.ctrlKey === true)) {
                return;
            }
            // Ensure that it is a number and stop the keypress
            if ((e.shiftKey || (e.keyCode < 48 || e.keyCode > 57)) && (e.keyCode < 96 || e.keyCode > 105)) {
                e.preventDefault();
            }
        });
    });
}

/**
 * Initialize price calculators
 */
function initializePriceCalculators() {
    const weightInputs = document.querySelectorAll('input[name="weight"]');
    
    weightInputs.forEach(weightInput => {
        if (weightInput && weightInput.closest) {
            const priceInput = weightInput.closest('form')?.querySelector('input[name="price"]');
            
            if (priceInput) {
                weightInput.addEventListener('input', function() {
                    if (this.value) {
                        const weight = parseFloat(this.value);
                        if (!isNaN(weight) && weight > 0 && !priceInput.value) {
                            // Simple price calculation: base rate + weight-based pricing
                            const baseRate = 10;
                            const perKgRate = 2;
                            const suggestedPrice = baseRate + (weight * perKgRate);
                            
                            // Show suggested price as placeholder
                            priceInput.placeholder = `Suggested: €${suggestedPrice.toFixed(2)}`;
                        }
                    }
                });
            }
        }
    });
}

/**
 * Initialize tracking features
 */
function initializeTrackingFeatures() {
    // Auto-refresh tracking updates
    if (window.location.pathname.includes('/track/')) {
        const refreshInterval = 30000; // 30 seconds
        
        setInterval(() => {
            const currentPath = window.location.pathname;
            if (currentPath.includes('/track/')) {
                // Subtle indication of refresh
                const timeline = document.querySelector('.tracking-timeline');
                if (timeline) {
                    timeline.classList.add('loading');
                    setTimeout(() => {
                        timeline.classList.remove('loading');
                    }, 1000);
                }
            }
        }, refreshInterval);
    }
    
    // Add smooth scrolling to latest update
    const trackingItems = document.querySelectorAll('.tracking-item');
    if (trackingItems.length > 0) {
        const latestUpdate = trackingItems[0];
        if (latestUpdate.classList.contains('active')) {
            setTimeout(() => {
                latestUpdate.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }, 500);
        }
    }
}

/**
 * Enhance modals
 */
function enhanceModals() {
    const modals = document.querySelectorAll('.modal');
    
    modals.forEach(modal => {
        modal.addEventListener('shown.bs.modal', function() {
            // Focus first input when modal opens
            const firstInput = this.querySelector('input:not([type="hidden"]), select, textarea');
            if (firstInput) {
                setTimeout(() => firstInput.focus(), 100);
            }
        });
        
        modal.addEventListener('hidden.bs.modal', function() {
            // Clear form validation states when modal closes
            const form = this.querySelector('form');
            if (form) {
                form.classList.remove('was-validated');
                const inputs = form.querySelectorAll('.is-valid, .is-invalid');
                inputs.forEach(input => {
                    input.classList.remove('is-valid', 'is-invalid');
                });
            }
        });
    });
}

/**
 * Enhance data tables
 */
function enhanceDataTables() {
    const tables = document.querySelectorAll('.table');
    
    tables.forEach(table => {
        // Add hover effects and loading states
        const rows = table.querySelectorAll('tbody tr');
        
        rows.forEach(row => {
            // Add click handlers for action buttons
            const actionButtons = row.querySelectorAll('.btn');
            actionButtons.forEach(button => {
                if (button.textContent.includes('Pay') || 
                    button.textContent.includes('Book') ||
                    button.textContent.includes('Mark as Delivered')) {
                    
                    button.addEventListener('click', function(e) {
                        // Add loading state
                        const originalText = this.innerHTML;
                        this.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Processing...';
                        this.disabled = true;
                        
                        // Reset after delay if not form submission
                        if (!this.closest('form')) {
                            setTimeout(() => {
                                this.innerHTML = originalText;
                                this.disabled = false;
                            }, 2000);
                        }
                    });
                }
            });
        });
    });
}

/**
 * Initialize rating system
 */
function initializeRatingSystem() {
    const ratingSelects = document.querySelectorAll('select[name="rating"]');
    
    ratingSelects.forEach(select => {
        // Create visual star rating
        const starContainer = document.createElement('div');
        starContainer.className = 'star-rating d-flex mb-2';
        
        for (let i = 1; i <= 5; i++) {
            const star = document.createElement('i');
            star.className = 'fas fa-star star-clickable';
            star.dataset.rating = i;
            star.style.color = '#ddd';
            star.style.cursor = 'pointer';
            star.style.fontSize = '1.5rem';
            star.style.marginRight = '0.25rem';
            
            star.addEventListener('click', function() {
                const rating = parseInt(this.dataset.rating);
                select.value = rating;
                updateStarDisplay(starContainer, rating);
            });
            
            star.addEventListener('mouseover', function() {
                const rating = parseInt(this.dataset.rating);
                updateStarDisplay(starContainer, rating, true);
            });
            
            starContainer.appendChild(star);
        }
        
        starContainer.addEventListener('mouseleave', function() {
            const currentRating = parseInt(select.value) || 0;
            updateStarDisplay(starContainer, currentRating);
        });
        
        // Insert star container before the select
        select.parentNode.insertBefore(starContainer, select);
        
        // Hide the original select
        select.style.display = 'none';
        
        // Initialize with current value
        const currentRating = parseInt(select.value) || 0;
        updateStarDisplay(starContainer, currentRating);
    });
}

/**
 * Update star display
 */
function updateStarDisplay(container, rating, isHover = false) {
    const stars = container.querySelectorAll('.star-clickable');
    stars.forEach((star, index) => {
        const starRating = index + 1;
        if (starRating <= rating) {
            star.style.color = isHover ? '#ffb400' : '#ffc107';
        } else {
            star.style.color = '#ddd';
        }
    });
}

/**
 * Utility functions
 */

// Debounce function for performance
function debounce(func, wait) {
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

// Format currency
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-EU', {
        style: 'currency',
        currency: 'EUR'
    }).format(amount);
}

// Copy to clipboard
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showToast('Copied to clipboard!', 'success');
    }).catch(() => {
        showToast('Failed to copy', 'error');
    });
}

// Show toast notification
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `alert alert-${type} position-fixed`;
    toast.style.top = '20px';
    toast.style.right = '20px';
    toast.style.zIndex = '9999';
    toast.style.minWidth = '250px';
    toast.innerHTML = `
        ${message}
        <button type="button" class="btn-close float-end" aria-label="Close"></button>
    `;
    
    document.body.appendChild(toast);
    
    // Auto remove after 3 seconds
    setTimeout(() => {
        if (toast.parentNode) {
            toast.parentNode.removeChild(toast);
        }
    }, 3000);
    
    // Manual close
    const closeBtn = toast.querySelector('.btn-close');
    closeBtn.addEventListener('click', () => {
        if (toast.parentNode) {
            toast.parentNode.removeChild(toast);
        }
    });
}

// Smooth scroll to element
function scrollToElement(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}

// Global error handler
window.addEventListener('error', function(e) {
    console.error('JavaScript Error:', e.error);
    // In production, you might want to send this to a logging service
});

// Service Worker registration (for future PWA features)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        // Service worker would be implemented here for offline functionality
        console.log('Service Worker support detected');
    });
}
