let selectedParagraph = null;
let currentCvId = null;
let originalContent = {};

function goHome() {
    window.location.href = 'cvs.html';
}

// Initialize page
document.addEventListener('DOMContentLoaded', function() {
    // Get CV ID from URL parameters
    const urlParams = new URLSearchParams(window.location.search);
    currentCvId = urlParams.get('id');
    
    if (currentCvId) {
        loadCVData(currentCvId);
    }
    
    setupEventListeners();
    initializeComponents();
});

function showComparisonContent() {
    const editorContent = document.getElementById('editorContent');
    
    // Charger le contenu de comparaison complet au lieu du placeholder
    editorContent.innerHTML = `
        <div class="comparison-header">
            <div class="selector-row">
                <div class="selector-group">
                    <label for="jobSelector">Offre d'emploi</label>
                    <select id="jobSelector" class="selector" onchange="loadJobOffer(this.value)">
                        <option value="">Sélectionner une offre...</option>
                        <option value="job1">Développeur Full Stack - StartupTech</option>
                        <option value="job2">Développeur Frontend - TechCorp</option>
                        <option value="job3">Développeur Backend - InnovateLab</option>
                    </select>
                </div>
                <div class="selector-group">
                    <label for="cvSelector">CV à comparer</label>
                    <select id="cvSelector" class="selector" onchange="loadCVForComparison(this.value)">
                        <option value="">Sélectionner un CV...</option>
                        <option value="cv1" selected>CV Marie Dupont - Développeuse Full Stack</option>
                    </select>
                </div>
                <div class="selector-group">
                    <button class="selector" onclick="analyzeAndHighlightKeywords()" style="background: #3b82f6; color: white; border-color: #3b82f6;">
                        🔍 Analyser
                    </button>
                </div>
            </div>
        </div>
        
        <div class="comparison-content">
            <div class="job-section">
                <div class="section-header">
                    <h3>📋 Offre d'emploi</h3>
                </div>
                <div class="content-area" id="jobContent">
                    <div class="placeholder-message">Sélectionnez une offre d'emploi pour commencer la comparaison</div>
                </div>
            </div>
            
            <div class="cv-section-comparison">
                <div class="section-header">
                    <h3>📄 CV</h3>
                </div>
                <div class="content-area" id="cvComparisonContent">
                    <!-- Le contenu sera chargé par generateCVComparisonContent() -->
                </div>
            </div>
        </div>
    `;
    
    // Initialiser les fonctionnalités de comparaison
    initializeComparisonFeatures();
}

function initializeComparisonFeatures() {
    // Charger le contenu du CV pour la comparaison
    const cvComparisonContent = document.getElementById('cvComparisonContent');
    if (cvComparisonContent && typeof generateCVComparisonContent === 'function') {
        cvComparisonContent.innerHTML = generateCVComparisonContent();
    }
    
    // Initialiser la sélection des paragraphes
    if (typeof setupParagraphSelection === 'function') {
        setupParagraphSelection();
    }
    
    // Charger automatiquement la première offre d'emploi
    const jobSelector = document.getElementById('jobSelector');
    if (jobSelector && jobSelector.options.length > 1 && typeof loadJobOffer === 'function') {
        jobSelector.value = 'job1';
        loadJobOffer('job1');
    }
    
    // Sélectionner le CV par défaut
    if (typeof loadCVForComparison === 'function') {
        loadCVForComparison('cv1');
    }
}

function loadCVData(cvId) {
    console.log(`Loading CV with ID: ${cvId}`);
    loadEditorContent();
    loadAssistantPanel();
}

function setupEventListeners() {
    // Editor tabs
    document.querySelectorAll('.tab').forEach(tab => {
        tab.addEventListener('click', function() {
            switchEditorTab(this.dataset.tab);
        });
    });
}

function initializeComponents() {
    setupResizer();
    setupChatResizer();
    initializeEditor();
    initializeChat();
    initializeComparison();
}

function switchEditorTab(tabName) {
    // Update tab appearance
    document.querySelectorAll('.tab').forEach(tab => {
        tab.classList.remove('active');
    });
    document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');

    // Show/hide content based on tab
    const editorContent = document.getElementById('editorContent');
    const comparisonContent = document.getElementById('comparisonContent');
    
    if (tabName === 'editor') {
        showEditorContent();
    } else if (tabName === 'comparison') {
        showComparisonContent();
    } else {
        showPlaceholderContent(tabName);
    }
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 12px 20px;
        border-radius: 6px;
        color: white;
        font-size: 14px;
        font-weight: 500;
        z-index: 1000;
        transition: all 0.3s ease;
        ${type === 'success' ? 'background: #10b981;' : 'background: #3b82f6;'}
    `;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.opacity = '0';
        notification.style.transform = 'translateX(100%)';
        setTimeout(() => {
            if (document.body.contains(notification)) {
                document.body.removeChild(notification);
            }
        }, 300);
    }, 3000);
}

function showEditorContent() {
    const editorContent = document.getElementById('editorContent');
    // if (editorContent.innerHTML.trim() === '') {
        loadEditorContent();
    // }
}

function showComparisonContent() {
    const editorContent = document.getElementById('editorContent');
    editorContent.innerHTML = '<div class="placeholder-content">Fonctionnalité de comparaison en cours de développement...</div>';
}

function showPlaceholderContent(tabName) {
    const editorContent = document.getElementById('editorContent');
    editorContent.innerHTML = `<div class="placeholder-content">Contenu ${tabName} en cours de développement...</div>`;
}

function loadAssistantPanel() {
    const assistantPanel = document.getElementById('assistantPanel');
    assistantPanel.innerHTML = '<div class="placeholder-content">Assistant IA en cours de développement...</div>';
}