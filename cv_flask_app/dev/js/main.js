
/**
 * Navigation functions
 */
function uploadCV() {
    window.location.href = '/dev/cvs.html';
}

function manageOffers() {
    window.location.href = '/dev/offers.html';
}

function editWithAI() {
    window.location.href = 'design_iterations/document_editor.html';
}

function viewHistory() {
    // showNotification("Affichage de l'historique...");
    window.location.href = 'search.html';
}

function editCV(cvId) {
    showNotification(`Édition du CV ${cvId}...`);
    // Simulate CV editing
}

function viewOffer(offerId) {
    showNotification(`Affichage de l'offre ${offerId}...`);
    // Simulate offer viewing
}

/**
 * Tab management functions for editor
 */
function initializeTabs() {
    const tabs = document.querySelectorAll('.tab');
    const editorContent = document.getElementById('editorContent');
    
    if (!tabs.length || !editorContent) return;
    
    tabs.forEach(tab => {
        tab.addEventListener('click', function() {
            const tabName = this.getAttribute('data-tab');
            switchTab(tabName);
        });
    });
}

function switchTab(tabName) {
    // Remove active class from all tabs
    document.querySelectorAll('.tab').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Add active class to clicked tab
    const activeTab = document.querySelector(`[data-tab="${tabName}"]`);
    if (activeTab) {
        activeTab.classList.add('active');
    }
    
    // Update content based on tab
    const editorContent = document.getElementById('editorContent');
    if (editorContent) {
        switch(tabName) {
            case 'editor':
                // Vérifier si la fonction existe dans edition.js, sinon utiliser la version locale
                if (typeof window.loadEditorContent === 'function') {
                    window.loadEditorContent();
                } else {
                    loadEditorContentLocal();
                }
                // Réinitialiser les fonctionnalités d'édition si elles existent
                if (typeof initializeEditor === 'function') {
                    initializeEditor();
                }
                break;
            case 'comparison':
                // Vérifier si la fonction existe dans edition.js, sinon utiliser la version locale
                if (typeof showComparisonContent === 'function') {
                    showComparisonContent();
                } else {
                    loadComparisonContent();
                }
                break;
            case 'preview':
                loadPreviewContent();
                break;
        }
    }
}

// Version locale de loadEditorContent pour compatibilité
function loadEditorContentLocal() {
    const editorContent = document.getElementById('editorContent');
    editorContent.innerHTML = `
        <div class="editor-workspace">
            <div class="editor-toolbar">
                <button class="btn-primary">Sauvegarder</button>
                <button class="btn-secondary">Exporter</button>
            </div>
            <div class="editor-area">
                <textarea id="cvEditor" placeholder="Contenu du CV..."></textarea>
            </div>
        </div>
    `;
}

function loadComparisonContent() {
    const editorContent = document.getElementById('editorContent');
    editorContent.innerHTML = `
        <div class="comparison-view">
            <div class="comparison-panel">
                <h3>CV</h3>
                <div class="cv-content">Contenu du CV...</div>
            </div>
            <div class="comparison-panel">
                <h3>Offre d'emploi</h3>
                <div class="offer-content">Contenu de l'offre...</div>
            </div>
        </div>
    `;
}

function loadPreviewContent() {
    const editorContent = document.getElementById('editorContent');
    editorContent.innerHTML = `
        <div class="preview-container">
            <div class="preview-header">
                <h3>Aperçu du CV</h3>
            </div>
            <div class="preview-content">
                <div class="cv-preview">Aperçu formaté du CV...</div>
            </div>
        </div>
    `;
}

/**
 * Utility functions
 */
function showNotification(message, type = 'success') {
    // Create notification element
    const notification = document.createElement('div');
    const bgColor = type === 'error' ? '#ef4444' : '#10b981';
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${bgColor};
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 0.5rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        z-index: 1001;
        font-weight: 500;
        transform: translateX(100%);
        transition: transform 0.3s ease;
    `;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    // Animate in
    setTimeout(() => {
        notification.style.transform = 'translateX(0)';
    }, 10);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.style.transform = 'translateX(100%)';
        setTimeout(() => {
            if (document.body.contains(notification)) {
                document.body.removeChild(notification);
            }
        }, 300);
    }, 3000);
}

/**
 * Initialize page animations and interactions
 */
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tabs if they exist (for editor page)
    initializeTabs();
    
    // Add subtle animations on page load
    const cards = document.querySelectorAll('.action-card, .feature-card');
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        setTimeout(() => {
            card.style.transition = 'all 0.6s ease';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 100);
    });

    // Add hover effects for better interactivity
    /*document.querySelectorAll('.action-card, .cv-item, .offer-item').forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-2px)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });
    */

    document.addEventListener('DOMContentLoaded', function() {
        // Attacher les événements de manière plus robuste
        const uploadButton = document.querySelector('.action-card:first-child');
        if (uploadButton) {
            uploadButton.addEventListener('click', uploadCV);
        }
        
        const manageOffersButton = document.querySelector('.action-card:nth-child(2)');
        if (manageOffersButton) {
            manageOffersButton.addEventListener('click', manageOffers);
        }
        
        const viewHistoryButton = document.querySelector('.action-card:nth-child(3)');
        if (viewHistoryButton) {
            viewHistoryButton.addEventListener('click', viewHistory);
        }
    });
});