// Portfolio Builder - JavaScript principal

document.addEventListener('DOMContentLoaded', function() {
    // Initialisation des composants
    initTooltips();
    initModals();
    initNotifications();
    initFormValidation();
    initImagePreview();
    initSkillBars();
    initThemePreview();
});

// Gestion des tooltips
function initTooltips() {
    const tooltips = document.querySelectorAll('[data-tooltip]');
    tooltips.forEach(tooltip => {
        tooltip.addEventListener('mouseenter', showTooltip);
        tooltip.addEventListener('mouseleave', hideTooltip);
    });
}

function showTooltip(event) {
    const text = event.target.getAttribute('data-tooltip');
    const tooltip = document.createElement('div');
    tooltip.className = 'tooltip-content';
    tooltip.textContent = text;
    tooltip.style.cssText = `
        position: absolute;
        background: #374151;
        color: white;
        padding: 8px 12px;
        border-radius: 6px;
        font-size: 14px;
        z-index: 1000;
        pointer-events: none;
    `;
    
    document.body.appendChild(tooltip);
    
    const rect = event.target.getBoundingClientRect();
    tooltip.style.left = rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2) + 'px';
    tooltip.style.top = rect.top - tooltip.offsetHeight - 8 + 'px';
}

function hideTooltip() {
    const tooltip = document.querySelector('.tooltip-content');
    if (tooltip) {
        tooltip.remove();
    }
}

// Gestion des modales
function initModals() {
    const modals = document.querySelectorAll('.modal');
    const closeButtons = document.querySelectorAll('.close');
    
    closeButtons.forEach(button => {
        button.addEventListener('click', closeModal);
    });
    
    window.addEventListener('click', function(event) {
        if (event.target.classList.contains('modal')) {
            closeModal(event);
        }
    });
}

function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'block';
        document.body.style.overflow = 'hidden';
    }
}

function closeModal(event) {
    const modal = event.target.closest('.modal');
    if (modal) {
        modal.style.display = 'none';
        document.body.style.overflow = 'auto';
    }
}

// Gestion des notifications
function initNotifications() {
    // Auto-hide notifications after 5 seconds
    const notifications = document.querySelectorAll('.notification');
    notifications.forEach(notification => {
        setTimeout(() => {
            notification.style.opacity = '0';
            setTimeout(() => {
                notification.remove();
            }, 300);
        }, 5000);
    });
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.opacity = '0';
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, 5000);
}

// Validation des formulaires
function initFormValidation() {
    const forms = document.querySelectorAll('form[data-validate]');
    forms.forEach(form => {
        form.addEventListener('submit', validateForm);
    });
}

function validateForm(event) {
    const form = event.target;
    const requiredFields = form.querySelectorAll('[required]');
    let isValid = true;
    
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            showFieldError(field, 'Ce champ est requis');
            isValid = false;
        } else {
            clearFieldError(field);
        }
    });
    
    // Validation email
    const emailFields = form.querySelectorAll('input[type="email"]');
    emailFields.forEach(field => {
        if (field.value && !isValidEmail(field.value)) {
            showFieldError(field, 'Adresse email invalide');
            isValid = false;
        }
    });
    
    // Validation URL
    const urlFields = form.querySelectorAll('input[type="url"]');
    urlFields.forEach(field => {
        if (field.value && !isValidUrl(field.value)) {
            showFieldError(field, 'URL invalide');
            isValid = false;
        }
    });
    
    if (!isValid) {
        event.preventDefault();
    }
}

function showFieldError(field, message) {
    clearFieldError(field);
    const error = document.createElement('div');
    error.className = 'field-error';
    error.textContent = message;
    error.style.cssText = 'color: #ef4444; font-size: 14px; margin-top: 4px;';
    field.parentNode.appendChild(error);
    field.classList.add('error');
}

function clearFieldError(field) {
    const error = field.parentNode.querySelector('.field-error');
    if (error) {
        error.remove();
    }
    field.classList.remove('error');
}

function isValidEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

function isValidUrl(url) {
    try {
        new URL(url);
        return true;
    } catch {
        return false;
    }
}

// Aperçu des images
function initImagePreview() {
    const imageInputs = document.querySelectorAll('input[type="file"][accept*="image"]');
    imageInputs.forEach(input => {
        input.addEventListener('change', previewImage);
    });
}

function previewImage(event) {
    const file = event.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            const preview = document.getElementById('image-preview');
            if (preview) {
                preview.src = e.target.result;
                preview.style.display = 'block';
            }
        };
        reader.readAsDataURL(file);
    }
}

// Barres de compétences
function initSkillBars() {
    const skillBars = document.querySelectorAll('.skill-progress');
    skillBars.forEach(bar => {
        const level = bar.getAttribute('data-level');
        const width = getSkillWidth(level);
        bar.style.width = width;
    });
}

function getSkillWidth(level) {
    switch(level) {
        case 'Débutant': return '25%';
        case 'Intermédiaire': return '50%';
        case 'Avancé': return '75%';
        case 'Expert': return '100%';
        default: return '50%';
    }
}

// Aperçu du thème
function initThemePreview() {
    const colorInputs = document.querySelectorAll('input[type="color"]');
    const fontSelect = document.querySelector('select[name="font_family"]');
    
    colorInputs.forEach(input => {
        input.addEventListener('change', updateThemePreview);
    });
    
    if (fontSelect) {
        fontSelect.addEventListener('change', updateThemePreview);
    }
}

function updateThemePreview() {
    const primaryColor = document.querySelector('input[name="primary_color"]')?.value || '#3B82F6';
    const secondaryColor = document.querySelector('input[name="secondary_color"]')?.value || '#1F2937';
    const fontFamily = document.querySelector('select[name="font_family"]')?.value || 'Inter';
    
    const preview = document.querySelector('.theme-preview');
    if (preview) {
        preview.style.setProperty('--primary-color', primaryColor);
        preview.style.setProperty('--secondary-color', secondaryColor);
        preview.style.fontFamily = fontFamily;
    }
}

// Utilitaires
function copyToClipboard(text) {
    if (navigator.clipboard) {
        navigator.clipboard.writeText(text).then(() => {
            showNotification('Lien copié dans le presse-papiers !', 'success');
        });
    } else {
        // Fallback pour les navigateurs plus anciens
        const textArea = document.createElement('textarea');
        textArea.value = text;
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);
        showNotification('Lien copié dans le presse-papiers !', 'success');
    }
}

function confirmDelete(message = 'Êtes-vous sûr de vouloir supprimer cet élément ?') {
    return confirm(message);
}

// Gestion des formulaires dynamiques
function addFormField(containerId, templateId) {
    const container = document.getElementById(containerId);
    const template = document.getElementById(templateId);
    
    if (container && template) {
        const clone = template.content.cloneNode(true);
        container.appendChild(clone);
    }
}

function removeFormField(button) {
    const field = button.closest('.form-field');
    if (field) {
        field.remove();
    }
}

// Gestion des onglets
function initTabs() {
    const tabButtons = document.querySelectorAll('.tab-button');
    const tabContents = document.querySelectorAll('.tab-content');
    
    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const targetId = button.getAttribute('data-tab');
            
            // Désactiver tous les onglets
            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabContents.forEach(content => content.classList.remove('active'));
            
            // Activer l'onglet sélectionné
            button.classList.add('active');
            const targetContent = document.getElementById(targetId);
            if (targetContent) {
                targetContent.classList.add('active');
            }
        });
    });
}

// Gestion des filtres
function initFilters() {
    const filterButtons = document.querySelectorAll('.filter-button');
    const filterItems = document.querySelectorAll('.filter-item');
    
    filterButtons.forEach(button => {
        button.addEventListener('click', () => {
            const filter = button.getAttribute('data-filter');
            
            // Mettre à jour les boutons actifs
            filterButtons.forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');
            
            // Filtrer les éléments
            filterItems.forEach(item => {
                if (filter === 'all' || item.classList.contains(filter)) {
                    item.style.display = 'block';
                } else {
                    item.style.display = 'none';
                }
            });
        });
    });
}

// Gestion des animations
function initAnimations() {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
            }
        });
    });
    
    const animatedElements = document.querySelectorAll('.animate-on-scroll');
    animatedElements.forEach(el => observer.observe(el));
}

// Gestion des statistiques
function updateStats() {
    const statNumbers = document.querySelectorAll('.stat-number');
    statNumbers.forEach(stat => {
        const target = parseInt(stat.getAttribute('data-target'));
        const duration = 2000; // 2 secondes
        const increment = target / (duration / 16); // 60 FPS
        let current = 0;
        
        const timer = setInterval(() => {
            current += increment;
            if (current >= target) {
                current = target;
                clearInterval(timer);
            }
            stat.textContent = Math.floor(current);
        }, 16);
    });
}

// Initialisation des animations au chargement
window.addEventListener('load', () => {
    initAnimations();
    updateStats();
});

// Gestion des erreurs globales
window.addEventListener('error', (event) => {
    console.error('Erreur JavaScript:', event.error);
    showNotification('Une erreur est survenue. Veuillez recharger la page.', 'error');
});

// Gestion des formulaires de suppression
document.addEventListener('submit', (event) => {
    if (event.target.classList.contains('delete-form')) {
        if (!confirm('Êtes-vous sûr de vouloir supprimer cet élément ?')) {
            event.preventDefault();
        }
    }
});

// Gestion des liens externes
document.addEventListener('click', (event) => {
    if (event.target.tagName === 'A' && event.target.hostname !== window.location.hostname) {
        event.target.setAttribute('target', '_blank');
        event.target.setAttribute('rel', 'noopener noreferrer');
    }
});
