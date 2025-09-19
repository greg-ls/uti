function initializeEditor() {
    setupParagraphSelection();
}

let commonKeywords = [];
let selectedParagraphKeywords = [];

// function loadEditorContent() {
//     const editorContent = document.getElementById('editorContent');
//     editorContent.innerHTML = `
//         <div class="cv-title" id="cvTitle">CV Marie Dupont - Développeuse Full Stack</div>
//         <!-- CV sections content -->
//     `;
// }
function initializeEditor() {
    setupParagraphSelection();
    loadEditorContent();
}
function showComparisonContent() {
    const editorContent = document.getElementById('editorContent');
    
    // Charger le contenu de comparaison au lieu du placeholder
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
                    ${generateCVComparisonContent()}
                </div>
            </div>
        </div>
    `;
    
    // Initialiser les fonctionnalités de comparaison
    initializeComparison();
    setupParagraphSelection();
}

function generateCVComparisonContent() {
    return `
        <div class="cv-title">CV Marie Dupont - Développeuse Full Stack</div>
        
        <div class="cv-section">
            <div class="section-title">👤 Profil Professionnel</div>
            <div class="paragraph" data-id="profile">
                <div class="paragraph-content">
                    Développeuse Full Stack passionnée avec 5 ans d'expérience dans le développement d'applications web modernes. 
                    Expertise en JavaScript, React, Node.js et bases de données. Forte capacité d'adaptation et esprit d'équipe.
                </div>
                <div class="paragraph-actions">
                    <div class="action-icon" title="Éditer" onclick="toggleEdit(this)">✏️</div>
                </div>
                <div class="edit-controls">
                    <button class="edit-btn primary" onclick="saveEdit(this)">Sauvegarder</button>
                    <button class="edit-btn secondary" onclick="cancelEdit(this)">Annuler</button>
                </div>
            </div>
        </div>

        <div class="cv-section">
            <div class="section-title">💼 Expérience Professionnelle</div>
            <div class="paragraph" data-id="exp1">
                <div class="paragraph-content">
                    <strong>Développeuse Full Stack Senior</strong> - TechCorp (2021-2024)<br>
                    • Développement d'applications React avec TypeScript<br>
                    • Architecture et développement d'APIs REST avec Node.js<br>
                    • Gestion de bases de données PostgreSQL et MongoDB<br>
                    • Collaboration en équipe agile, code reviews et mentoring
                </div>
                <div class="paragraph-actions">
                    <div class="action-icon" title="Éditer" onclick="toggleEdit(this)">✏️</div>
                </div>
                <div class="edit-controls">
                    <button class="edit-btn primary" onclick="saveEdit(this)">Sauvegarder</button>
                    <button class="edit-btn secondary" onclick="cancelEdit(this)">Annuler</button>
                </div>
            </div>
        </div>

        <div class="cv-section">
            <div class="section-title">🎓 Formation</div>
            <div class="paragraph" data-id="education">
                <div class="paragraph-content">
                    <strong>Master en Informatique</strong> - Université de Technologie (2019)<br>
                    Spécialisation en développement web et bases de données
                </div>
                <div class="paragraph-actions">
                    <div class="action-icon" title="Éditer" onclick="toggleEdit(this)">✏️</div>
                </div>
                <div class="edit-controls">
                    <button class="edit-btn primary" onclick="saveEdit(this)">Sauvegarder</button>
                    <button class="edit-btn secondary" onclick="cancelEdit(this)">Annuler</button>
                </div>
            </div>
        </div>

        <div class="cv-section">
            <div class="section-title">🛠️ Compétences Techniques</div>
            <div class="paragraph" data-id="skills">
                <div class="paragraph-content">
                    <strong>Langages :</strong> JavaScript, TypeScript, Python, SQL<br>
                    <strong>Frontend :</strong> React, Vue.js, HTML5, CSS3, Sass<br>
                    <strong>Backend :</strong> Node.js, Express, Django<br>
                    <strong>Bases de données :</strong> PostgreSQL, MongoDB, Redis<br>
                    <strong>Outils :</strong> Git, Docker, AWS, Jenkins
                </div>
                <div class="paragraph-actions">
                    <div class="action-icon" title="Éditer" onclick="toggleEdit(this)">✏️</div>
                </div>
                <div class="edit-controls">
                    <button class="edit-btn primary" onclick="saveEdit(this)">Sauvegarder</button>
                    <button class="edit-btn secondary" onclick="cancelEdit(this)">Annuler</button>
                </div>
            </div>
        </div>
    `;
}

function initializeComparison() {
    // Charger le CV par défaut pour la comparaison
    loadCVForComparison('cv1');
    
    // Sélectionner automatiquement la première offre d'emploi si disponible
    const jobSelector = document.getElementById('jobSelector');
    if (jobSelector && jobSelector.options.length > 1) {
        jobSelector.value = 'job1';
        loadJobOffer('job1');
    }
}

function setupParagraphSelection() {
    document.querySelectorAll('.paragraph').forEach(paragraph => {
        paragraph.addEventListener('click', function(e) {
            if (e.target.closest('.paragraph-actions') || e.target.closest('.edit-controls')) {
                return;
            }
            selectParagraph(this);
        });
    });
}

function loadJobOffer(jobId) {
    const jobContent = document.getElementById('jobContent');
    
    if (!jobId) {
        jobContent.innerHTML = '<div class="placeholder-message">Sélectionnez une offre d\'emploi pour commencer la comparaison</div>';
        return;
    }
    
    // Simuler le chargement d'une offre d'emploi
    const jobOffers = {
        job1: {
            title: "Développeur Full Stack - StartupTech",
            content: `
                <div class="job-card">
                    <div class="job-header">
                        <h4>Développeur Full Stack</h4>
                        <div class="company">StartupTech - Paris</div>
                    </div>
                    
                    <div class="job-section">
                        <h5>📋 Description du poste</h5>
                        <div class="job-paragraph" data-id="job-desc">
                            <div class="paragraph-content">
                                Nous recherchons un développeur Full Stack expérimenté pour rejoindre notre équipe dynamique. 
                                Vous travaillerez sur des projets innovants utilisant les dernières technologies web.
                            </div>
                            <div class="paragraph-actions">
                                <div class="action-icon" title="Éditer" onclick="toggleEdit(this)">✏️</div>
                            </div>
                            <div class="edit-controls">
                                <button class="edit-btn primary" onclick="saveEdit(this)">Sauvegarder</button>
                                <button class="edit-btn secondary" onclick="cancelEdit(this)">Annuler</button>
                            </div>
                        </div>
                    </div>
                    
                    <div class="job-section">
                        <h5>🎯 Compétences requises</h5>
                        <div class="job-paragraph" data-id="job-skills">
                            <div class="paragraph-content">
                                • Maîtrise de JavaScript/TypeScript<br>
                                • Expérience avec React et Node.js<br>
                                • Connaissance des bases de données (PostgreSQL, MongoDB)<br>
                                • Expérience avec Git et les méthodologies agiles<br>
                                • Minimum 3 ans d'expérience
                            </div>
                            <div class="paragraph-actions">
                                <div class="action-icon" title="Éditer" onclick="toggleEdit(this)">✏️</div>
                            </div>
                            <div class="edit-controls">
                                <button class="edit-btn primary" onclick="saveEdit(this)">Sauvegarder</button>
                                <button class="edit-btn secondary" onclick="cancelE

this)">Annuler</button>
                            </div>
                        </div>
                    </div>
                    
                    <div class="job-section">
                        <h5>💼 Ce que nous offrons</h5>
                        <div class="job-paragraph" data-id="job-offer">
                            <div class="paragraph-content">
                                • Salaire compétitif (45-55k€)<br>
                                • Télétravail partiel<br>
                                • Formation continue<br>
                                • Équipe jeune et dynamique<br>
                                • Projets variés et stimulants
                            </div>
                            <div class="paragraph-actions">
                                <div class="action-icon" title="Éditer" onclick="toggleEdit(this)">✏️</div>
                            </div>
                            <div class="edit-controls">
                                <button class="edit-btn primary" onclick="saveEdit(this)">Sauvegarder</button>
                                <button class="edit-btn secondary" onclick="cancelEdit(this)">Annuler</button>
                            </div>
                        </div>
                    </div>
                </div>
            `
        }
        // Ajouter d'autres offres d'emploi ici
    };
    
    const selectedJob = jobOffers[jobId];
    if (selectedJob) {
        jobContent.innerHTML = selectedJob.content;
        // Réinitialiser la sélection des paragraphes pour les nouvelles cartes d'offre
        setupJobParagraphSelection();
    }
}

function analyzeAndHighlightKeywords() {
    // Extraire le texte du CV et de l'offre d'emploi
    const cvText = extractTextFromCV();
    const jobText = extractTextFromJob();
    
    // Trouver les mots-clés communs
    commonKeywords = findCommonKeywords(cvText, jobText);
    
    // Appliquer la surbrillance
    highlightKeywords();
}

function extractTextFromCV() {
    const cvContent = document.getElementById('cvComparisonContent');
    if (!cvContent) return '';
    
    const paragraphs = cvContent.querySelectorAll('.paragraph-content');
    return Array.from(paragraphs).map(p => p.textContent).join(' ');
}

function extractTextFromJob() {
    const jobContent = document.getElementById('jobContent');
    if (!jobContent) return '';
    
    const paragraphs = jobContent.querySelectorAll('.paragraph-content');
    return Array.from(paragraphs).map(p => p.textContent).join(' ');
}

function findCommonKeywords(cvText, jobText) {
    // Nettoyer et normaliser le texte
    const cleanText = (text) => {
        return text.toLowerCase()
            .replace(/[^\w\s]/g, ' ')
            .split(/\s+/)
            .filter(word => word.length > 2); // Ignorer les mots trop courts
    };
    
    const cvWords = new Set(cleanText(cvText));
    const jobWords = new Set(cleanText(jobText));
    
    // Mots-clés techniques et professionnels importants
    const technicalKeywords = [
        'javascript', 'typescript', 'react', 'nodejs', 'node', 'postgresql', 'mongodb',
        'git', 'docker', 'aws', 'html', 'css', 'python', 'sql', 'express', 'django',
        'développeur', 'développeuse', 'full', 'stack', 'frontend', 'backend',
        'expérience', 'équipe', 'agile', 'projet', 'application', 'web', 'base',
        'données', 'api', 'rest', 'architecture', 'développement'
    ];
    
    // Trouver les mots communs, en privilégiant les mots-clés techniques
    const commonWords = [...cvWords].filter(word => jobWords.has(word));
    
    // Prioriser les mots-clés techniques
    return commonWords.sort((a, b) => {
        const aIsTechnical = technicalKeywords.includes(a);
        const bIsTechnical = technicalKeywords.includes(b);
        
        if (aIsTechnical && !bIsTechnical) return -1;
        if (!aIsTechnical && bIsTechnical) return 1;
        return b.length - a.length; // Puis par longueur
    }).slice(0, 20); // Limiter à 20 mots-clés
}

function highlightKeywords() {
    // Supprimer les anciennes surbrillances
    clearHighlights();
    
    if (commonKeywords.length === 0) return;
    
    // Surbrillancer dans l'offre d'emploi
    highlightInContainer('jobContent', commonKeywords, 'job-highlight');
    
    // Surbrillancer dans le CV
    highlightInContainer('cvComparisonContent', commonKeywords, 'cv-highlight');
}

function highlightInContainer(containerId, keywords, className) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    const paragraphs = container.querySelectorAll('.paragraph-content');
    
    paragraphs.forEach(paragraph => {
        let html = paragraph.innerHTML;
        
        keywords.forEach(keyword => {
            const regex = new RegExp(`\\b(${escapeRegExp(keyword)})\\b`, 'gi');
            html = html.replace(regex, `<span class="${className}">$1</span>`);
        });
        
        paragraph.innerHTML = html;
    });
}

function highlightSelectedParagraphKeywords(selectedParagraph) {
    if (!selectedParagraph) return;
    
    // Extraire le texte du paragraphe sélectionné
    const paragraphText = selectedParagraph.querySelector('.paragraph-content').textContent;
    
    // Trouver les mots-clés du paragraphe qui sont aussi dans l'offre
    const jobText = extractTextFromJob();
    selectedParagraphKeywords = findCommonKeywords(paragraphText, jobText);
    
    // Supprimer les anciennes surbrillances spéciales
    clearSelectedHighlights();
    
    // Appliquer la surbrillance spéciale pour le paragraphe sélectionné
    if (selectedParagraphKeywords.length > 0) {
        highlightSelectedKeywords(selectedParagraph, selectedParagraphKeywords);
    }
}

function highlightSelectedKeywords(selectedParagraph, keywords) {
    const paragraphContent = selectedParagraph.querySelector('.paragraph-content');
    let html = paragraphContent.innerHTML;
    
    // Remplacer les surbrillances normales par des surbrillances sélectionnées
    keywords.forEach(keyword => {
        const regex = new RegExp(`<span class="cv-highlight">(${escapeRegExp(keyword)})</span>`, 'gi');
        html = html.replace(regex, `<span class="cv-highlight-selected">$1</span>`);
    });
    
    paragraphContent.innerHTML = html;
}

function clearHighlights() {
    // Supprimer toutes les surbrillances
    document.querySelectorAll('.job-highlight, .cv-highlight, .cv-highlight-selected').forEach(span => {
        const parent = span.parentNode;
        parent.replaceChild(document.createTextNode(span.textContent), span);
        parent.normalize();
    });
}

function clearSelectedHighlights() {
    // Supprimer uniquement les surbrillances de sélection
    document.querySelectorAll('.cv-highlight-selected').forEach(span => {
        span.className = 'cv-highlight';
    });
}

function escapeRegExp(string) {
    return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

// Modifier la fonction selectParagraph existante
function selectParagraph(paragraphElement) {
    // Restaurer les surbrillances normales pour l'ancien paragraphe sélectionné
    if (selectedParagraph) {
        clearSelectedHighlights();
    }
    
    document.querySelectorAll('.paragraph').forEach(p => {
        p.classList.remove('selected');
    });
    
    paragraphElement.classList.add('selected');
    selectedParagraph = paragraphElement;
    
    // Appliquer la surbrillance spéciale pour le nouveau paragraphe sélectionné
    highlightSelectedParagraphKeywords(paragraphElement);
    
    updateSelectionInfo(paragraphElement);
}


function setupJobParagraphSelection() {
    document.querySelectorAll('.job-paragraph').forEach(paragraph => {
        paragraph.addEventListener('click', function(e) {
            if (e.target.closest('.paragraph-actions') || e.target.closest('.edit-controls')) {
                return;
            }
            selectParagraph(this);
        });
    });
}

function loadCVForComparison(cvId) {
    const cvComparisonContent = document.getElementById('cvComparisonContent');
    
    // Pour l'instant, on garde le même contenu, mais on pourrait charger différents CVs
    if (cvId === currentCvId) {
        cvComparisonContent.innerHTML = generateCVComparisonContent();
        setupParagraphSelection();
    }
    // Ajouter la logique pour charger d'autres CVs si nécessaire
}

function initializeEditor() {
    setupParagraphSelection();
    loadEditorContent();
}

function loadEditorContent() {
    const editorContent = document.getElementById('editorContent');
    editorContent.innerHTML = `
        <div class="cv-title" id="cvTitle">CV Marie Dupont - Développeuse Full Stack</div>
        
        <div class="cv-section">
            <div class="section-title">👤 Profil Professionnel</div>
            <div class="paragraph" data-id="profile">
                <div class="paragraph-content">
                    Développeuse Full Stack passionnée avec 5 ans d'expérience dans le développement d'applications web modernes. 
                    Expertise en JavaScript, React, Node.js et bases de données. Forte capacité d'adaptation et esprit d'équipe.
                </div>
                <div class="paragraph-actions">
                    <div class="action-icon" title="Éditer" onclick="toggleEdit(this)">✏️</div>
                </div>
                <div class="edit-controls">
                    <button class="edit-btn primary" onclick="saveEdit(this)">Sauvegarder</button>
                    <button class="edit-btn secondary" onclick="cancelEdit(this)">Annuler</button>
                </div>
            </div>
        </div>

        <div class="cv-section">
            <div class="section-title">💼 Expérience Professionnelle</div>
            <div class="paragraph" data-id="exp1">
                <div class="paragraph-content">
                    <strong>Développeuse Full Stack Senior</strong> - TechCorp (2021-2024)<br>
                    • Développement d'applications React avec TypeScript<br>
                    • Architecture et développement d'APIs REST avec Node.js<br>
                    • Gestion de bases de données PostgreSQL et MongoDB<br>
                    • Collaboration en équipe agile, code reviews et mentoring
                </div>
                <div class="paragraph-actions">
                    <div class="action-icon" title="Éditer" onclick="toggleEdit(this)">✏️</div>
                </div>
                <div class="edit-controls">
                    <button class="edit-btn primary" onclick="saveEdit(this)">Sauvegarder</button>
                    <button class="edit-btn secondary" onclick="cancelEdit(this)">Annuler</button>
                </div>
            </div>
        </div>

        <div class="cv-section">
            <div class="section-title">🎓 Formation</div>
            <div class="paragraph" data-id="education">
                <div class="paragraph-content">
                    <strong>Master en Informatique</strong> - Université de Technologie (2019)<br>
                    Spécialisation en développement web et bases de données
                </div>
                <div class="paragraph-actions">
                    <div class="action-icon" title="Éditer" onclick="toggleEdit(this)">✏️</div>
                </div>
                <div class="edit-controls">
                    <button class="edit-btn primary" onclick="saveEdit(this)">Sauvegarder</button>
                    <button class="edit-btn secondary" onclick="cancelEdit(this)">Annuler</button>
                </div>
            </div>
        </div>

        <div class="cv-section">
            <div class="section-title">🛠️ Compétences Techniques</div>
            <div class="paragraph" data-id="skills">
                <div class="paragraph-content">
                    <strong>Langages :</strong> JavaScript, TypeScript, Python, SQL<br>
                    <strong>Frontend :</strong> React, Vue.js, HTML5, CSS3, Sass<br>
                    <strong>Backend :</strong> Node.js, Express, Django<br>
                    <strong>Bases de données :</strong> PostgreSQL, MongoDB, Redis<br>
                    <strong>Outils :</strong> Git, Docker, AWS, Jenkins
                </div>
                <div class="paragraph-actions">
                    <div class="action-icon" title="Éditer" onclick="toggleEdit(this)">✏️</div>
                </div>
                <div class="edit-controls">
                    <button class="edit-btn primary" onclick="saveEdit(this)">Sauvegarder</button>
                    <button class="edit-btn secondary" onclick="cancelEdit(this)">Annuler</button>
                </div>
            </div>
        </div>
    `;
    
    // Réinitialiser la sélection des paragraphes après le chargement
    setupParagraphSelection();
}

function setupParagraphSelection() {
    document.querySelectorAll('.paragraph').forEach(paragraph => {
        paragraph.addEventListener('click', function(e) {
            if (e.target.closest('.paragraph-actions') || e.target.closest('.edit-controls')) {
                return;
            }
            selectParagraph(this);
        });
    });
}

function toggleEdit(actionIcon) {
    const paragraph = actionIcon.closest('.paragraph');
    const content = paragraph.querySelector('.paragraph-content');
    const editControls = paragraph.querySelector('.edit-controls');
    const paragraphId = paragraph.dataset.id;
    
    if (paragraph.classList.contains('editing')) {
        cancelEdit(editControls.querySelector('.edit-btn.secondary'));
    } else {
        originalContent[paragraphId] = content.innerHTML;
        content.contentEditable = true;
        content.focus();
        paragraph.classList.add('editing');
        actionIcon.classList.add('active');
        editControls.classList.add('active');
        
        const range = document.createRange();
        const selection = window.getSelection();
        range.selectNodeContents(content);
        range.collapse(false);
        selection.removeAllRanges();
        selection.addRange(range);
    }
}

function saveEdit(saveBtn) {
    const paragraph = saveBtn.closest('.paragraph');
    const content = paragraph.querySelector('.paragraph-content');
    const editControls = paragraph.querySelector('.edit-controls');
    const actionIcon = paragraph.querySelector('.action-icon[title="Éditer"]');
    const paragraphId = paragraph.dataset.id;
    
    content.contentEditable = false;
    paragraph.classList.remove('editing');
    actionIcon.classList.remove('active');
    editControls.classList.remove('active');
    
    delete originalContent[paragraphId];
    
    console.log(`Saved paragraph ${paragraphId}:`, content.innerHTML);
    showNotification('Modifications sauvegardées', 'success');
}

function cancelEdit(cancelBtn) {
    const paragraph = cancelBtn.closest('.paragraph');
    const content = paragraph.querySelector('.paragraph-content');
    const editControls = paragraph.querySelector('.edit-controls');
    const actionIcon = paragraph.querySelector('.action-icon[title="Éditer"]');
    const paragraphId = paragraph.dataset.id;
    
    if (originalContent[paragraphId]) {
        content.innerHTML = originalContent[paragraphId];
        delete originalContent[paragraphId];
    }
    
    content.contentEditable = false;
    paragraph.classList.remove('editing');
    actionIcon.classList.remove('active');
    editControls.classList.remove('active');
}

function selectParagraph(paragraphElement) {
    document.querySelectorAll('.paragraph').forEach(p => {
        p.classList.remove('selected');
    });
    
    paragraphElement.classList.add('selected');
    selectedParagraph = paragraphElement;
    
    updateSelectionInfo(paragraphElement);
}

function updateSelectionInfo(paragraphElement) {
    const selectionInfo = document.getElementById('selectionInfo');
    const selectedText = document.getElementById('selectedText');
    const content = paragraphElement.querySelector('.paragraph-content').textContent;
    
    if (selectionInfo && selectedText) {
        selectedText.textContent = content.substring(0, 100) + (content.length > 100 ? '...' : '');
        selectionInfo.style.display = 'block';
    }
    
    const chatInput = document.getElementById('chatInput');
    if (chatInput) {
        chatInput.placeholder = 'Demandez des suggestions pour le paragraphe sélectionné...';
    }
}
