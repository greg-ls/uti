
// File upload functionality
let selectedFile = null;

// Add offer modal functions
function openAddOfferModal() {
    const modal = document.getElementById('addOfferModal');
    modal.classList.add('active');
    
    // Reset form
    resetOfferForm();
}

function closeAddOfferModal() {
    const modal = document.getElementById('addOfferModal');
    modal.classList.remove('active');
    
    // Reset form
    resetOfferForm();
}

function resetOfferForm() {
    selectedFile = null;
    document.getElementById('documentName').value = '';
    updateOfferDropZone();
    updateUploadButton();
}

function updateUploadButton() {
    const uploadBtn = document.getElementById('uploadBtn');
    const documentName = document.getElementById('documentName').value.trim();
    
    if (selectedFile && documentName) {
        uploadBtn.disabled = false;
        uploadBtn.style.background = '#3b82f6';
    } else {
        uploadBtn.disabled = true;
        uploadBtn.style.background = '#94a3b8';
    }
}

function updateOfferDropZone() {
    const dropZone = document.getElementById('offerDropZone');
    const dropZoneText = dropZone.querySelector('.drop-zone-text');
    const dropZoneSubtext = dropZone.querySelector('.drop-zone-subtext');
    
    if (selectedFile) {
        dropZoneText.textContent = selectedFile.name;
        dropZoneSubtext.textContent = 'Fichier sélectionné';
        dropZone.style.borderColor = '#10b981';
        dropZone.style.background = '#f0fdf4';
    } else {
        dropZoneText.textContent = 'Glissez votre fichier ici';
        dropZoneSubtext.textContent = 'ou cliquez pour sélectionner un fichier .docx';
        dropZone.style.borderColor = '#d1d5db';
        dropZone.style.background = 'transparent';
    }
}

function triggerOfferFileInput() {
    document.getElementById('offerFileInput').click();
}

function processOfferUpload() {
    const documentName = document.getElementById('documentName').value.trim();
    
    if (selectedFile && documentName) {
        const offersList = document.getElementById('offersList');
        const newOffer = document.createElement('div');
        newOffer.className = 'offer-card';
        
        // Générer un ID unique pour la nouvelle offre
        const newOfferId = Date.now();
        
        newOffer.innerHTML = `
            <div class="offer-info">
                <div class="offer-title">${documentName}</div>
                <div class="offer-company">${selectedFile.name}</div>
            </div>
            <div class="offer-actions">
                <button class="action-btn" onclick="viewOffer(${newOfferId})">Voir</button>
                <button class="action-btn" onclick="deleteOffer(${newOfferId})">Supprimer</button>
            </div>
        `;
        offersList.prepend(newOffer);
        
        // Stocker la nouvelle offre dans les données simulées
        addOfferToData(newOfferId, {
            id: newOfferId,
            title: documentName,
            company: selectedFile.name.replace('.docx', ''),
            location: "Non spécifié",
            contractType: "À définir",
            duration: "À définir",
            description: "Description à compléter lors de l'analyse du document.",
            technicalSkills: [],
            desiredSkills: [],
            softSkills: [],
            education: [],
            experience: [],
            languages: []
        });
        
        // Close modal
        closeAddOfferModal();
        
        // Show success notification
        showNotification("Offre ajoutée avec succès!");
        
        // Add hover effects to new offer
        addOfferCardHoverEffects(newOffer);
    }
}

// Show notification
function showNotification(message, type = 'success') {
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

// Add hover effects to offer cards
function addOfferCardHoverEffects(card) {
    card.addEventListener('mouseenter', function() {
        this.style.transform = 'translateY(-2px)';
    });
    
    card.addEventListener('mouseleave', function() {
        this.style.transform = 'translateY(0)';
    });
}

// Données simulées des offres (stockage global)
let offersData = {
    1: {
        id: 1,
        title: "Développeur Full Stack Senior",
        company: "TechCorp Innovation",
        location: "Paris",
        contractType: "CDI",
        duration: "Indéterminée",
        description: "Nous recherchons un développeur Full Stack Senior pour rejoindre notre équipe technique dynamique. Vous serez responsable du développement d'applications web modernes et participerez à l'architecture de nos solutions.",
        technicalSkills: ["JavaScript", "React", "Node.js", "MongoDB", "Git", "Docker"],
        desiredSkills: ["TypeScript", "AWS", "GraphQL", "Kubernetes"],
        softSkills: ["Travail en équipe", "Communication", "Autonomie", "Créativité", "Leadership"],
        education: ["Bac+5 en informatique ou équivalent", "Formation en développement web"],
        experience: ["5+ années d'expérience en développement Full Stack", "Expérience avec les frameworks modernes", "Connaissance des méthodologies Agile"],
        languages: ["Français : Courant", "Anglais : Technique"]
    },
    2: {
        id: 2,
        title: "Designer UX/UI",
        company: "Creative Studio",
        location: "Lyon",
        contractType: "CDI",
        duration: "Indéterminée",
        description: "Rejoignez notre équipe créative en tant que Designer UX/UI. Vous concevrez des interfaces utilisateur intuitives et des expériences utilisateur exceptionnelles pour nos clients.",
        technicalSkills: ["Figma", "Adobe Creative Suite", "Sketch", "Prototyping", "HTML/CSS"],
        desiredSkills: ["After Effects", "Principle", "InVision", "Zeplin"],
        softSkills: ["Créativité", "Sens esthétique", "Communication", "Empathie utilisateur"],
        education: ["Formation en design graphique ou équivalent", "École de design"],
        experience: ["3+ années d'expérience en UX/UI", "Portfolio démontrant des projets variés"],
        languages: ["Français : Courant", "Anglais : Intermédiaire"]
    },
    3: {
        id: 3,
        title: "Chef de Projet Digital",
        company: "Digital Agency",
        location: "Marseille",
        contractType: "CDI",
        duration: "Indéterminée",
        description: "Nous cherchons un Chef de Projet Digital expérimenté pour piloter nos projets web et mobile. Vous coordonnerez les équipes techniques et créatives.",
        technicalSkills: ["Gestion de projet", "Scrum", "Kanban", "JIRA", "Confluence"],
        desiredSkills: ["PMP", "Agile", "Lean", "Six Sigma"],
        softSkills: ["Leadership", "Communication", "Organisation", "Gestion du stress"],
        education: ["Bac+5 en management ou équivalent", "Formation en gestion de projet"],
        experience: ["5+ années en gestion de projet digital", "Expérience en méthodologies agiles"],
        languages: ["Français : Courant", "Anglais : Courant"]
    }
};

// Initialize page
document.addEventListener('DOMContentLoaded', function() {
    // Add hover effects to existing offer cards
    document.querySelectorAll('.offer-card').forEach(addOfferCardHoverEffects);
    updateOfferCards();
    // Simulate navigation back to main page
    document.querySelector('.logo').addEventListener('click', function() {
        window.location.href = 'index.html';
    });

    // File input event listener
    document.getElementById('offerFileInput').addEventListener('change', function(e) {
        if (e.target.files.length > 0) {
            selectedFile = e.target.files[0];
            if (selectedFile.name.endsWith('.docx')) {
                updateOfferDropZone();
                updateUploadButton();
                
                // Auto-fill document name if empty
                const nameInput = document.getElementById('documentName');
                if (!nameInput.value.trim()) {
                    const fileName = selectedFile.name.replace('.docx', '');
                    nameInput.value = fileName;
                    updateUploadButton();
                }
            } else {
                showNotification('Veuillez sélectionner un fichier .docx', 'error');
                e.target.value = '';
                selectedFile = null;
            }
        }
    });

    // Document name input event listener
    document.getElementById('documentName').addEventListener('input', updateUploadButton);

    // Drag and drop functionality
    const offerDropZone = document.getElementById('offerDropZone');
    
    offerDropZone.addEventListener('dragover', function(e) {
        e.preventDefault();
        this.classList.add('dragover');
    });
    
    offerDropZone.addEventListener('dragleave', function(e) {
        e.preventDefault();
        this.classList.remove('dragover');
    });
    
    offerDropZone.addEventListener('drop', function(e) {
        e.preventDefault();
        this.classList.remove('dragover');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            const file = files[0];
            if (file.name.endsWith('.docx')) {
                selectedFile = file;
                updateOfferDropZone();
                updateUploadButton();
                
                // Auto-fill document name if empty
                const nameInput = document.getElementById('documentName');
                if (!nameInput.value.trim()) {
                    const fileName = file.name.replace('.docx', '');
                    nameInput.value = fileName;
                    updateUploadButton();
                }
            } else {
                showNotification('Veuillez déposer un fichier .docx', 'error');
            }
        }
    });
});

// Additional function for adding new offers (if needed)
function addNewOffer() {
    // This function can be implemented for the form-based offer addition
    console.log('Add new offer functionality to be implemented');
}

// view offer 
function viewOffer(offerId) {
    console.log('viewOffer appelée avec ID:', offerId);
    
    // Récupérer les données de l'offre
    const offerData = getOfferDataById(offerId);
    console.log('Données récupérées:', offerData);
    
    if (offerData) {
        // Stocker les données dans le localStorage
        localStorage.setItem('currentOfferView', JSON.stringify(offerData));
        console.log('Données stockées dans localStorage');
        
        // Rediriger vers la page de visualisation
        window.location.href = `offer-view.html?id=${offerId}`;
    } else {
        showNotification('Offre non trouvée', 'error');
    }
}

// Fonction pour récupérer les données d'une offre par ID
function getOfferDataById(offerId) {
    // Simulation de données d'offres - à remplacer par un appel API réel
    const offersData = {
        1: {
            id: 1,
            title: "Développeur Full Stack Senior",
            company: "TechCorp Innovation",
            location: "Paris",
            contractType: "CDI",
            duration: "Indéterminée",
            description: "Nous recherchons un développeur Full Stack Senior pour rejoindre notre équipe technique dynamique. Vous serez responsable du développement d'applications web modernes et participerez à l'architecture de nos solutions.",
            technicalSkills: ["JavaScript", "React", "Node.js", "MongoDB", "Git", "Docker"],
            desiredSkills: ["TypeScript", "AWS", "GraphQL", "Kubernetes"],
            softSkills: ["Travail en équipe", "Communication", "Autonomie", "Créativité", "Leadership"],
            education: ["Bac+5 en informatique ou équivalent", "Formation en développement web"],
            experience: ["5+ années d'expérience en développement Full Stack", "Expérience avec les frameworks modernes", "Connaissance des méthodologies Agile"],
            languages: ["Français : Courant", "Anglais : Technique"]
        },
        2: {
            id: 2,
            title: "Designer UX/UI",
            company: "Creative Studio",
            location: "Lyon",
            contractType: "CDI",
            duration: "Indéterminée",
            description: "Rejoignez notre équipe créative en tant que Designer UX/UI. Vous concevrez des interfaces utilisateur intuitives et des expériences utilisateur exceptionnelles pour nos clients.",
            technicalSkills: ["Figma", "Adobe Creative Suite", "Sketch", "Prototyping", "HTML/CSS"],
            desiredSkills: ["After Effects", "Principle", "InVision", "Zeplin"],
            softSkills: ["Créativité", "Sens esthétique", "Communication", "Empathie utilisateur"],
            education: ["Formation en design graphique ou équivalent", "École de design"],
            experience: ["3+ années d'expérience en UX/UI", "Portfolio démontrant des projets variés"],
            languages: ["Français : Courant", "Anglais : Intermédiaire"]
        },
        3: {
            id: 3,
            title: "Chef de Projet Digital",
            company: "Digital Agency",
            location: "Marseille",
            contractType: "CDI",
            duration: "Indéterminée",
            description: "Nous cherchons un Chef de Projet Digital expérimenté pour piloter nos projets web et mobile. Vous coordonnerez les équipes techniques et créatives.",
            technicalSkills: ["Gestion de projet", "Scrum", "Kanban", "JIRA", "Confluence"],
            desiredSkills: ["PMP", "Agile", "Lean", "Six Sigma"],
            softSkills: ["Leadership", "Communication", "Organisation", "Gestion du stress"],
            education: ["Bac+5 en management ou équivalent", "Formation en gestion de projet"],
            experience: ["5+ années en gestion de projet digital", "Expérience en méthodologies agiles"],
            languages: ["Français : Courant", "Anglais : Courant"]
        }
    };
    
    return offersData[offerId] || null;
}

// Ajouter des IDs aux boutons "Voir" dans les cartes d'offres existantes
function updateOfferCards() {
    const offerCards = document.querySelectorAll('.offer-card');
    offerCards.forEach((card, index) => {
        const viewButton = card.querySelector('.action-btn');
        if (viewButton && viewButton.textContent === 'Voir') {
            viewButton.setAttribute('onclick', `viewOffer(${index + 1})`);
        }
    });
}

function displayOfferModal(offerData) {
    // Créer le modal s'il n'existe pas
    let modal = document.getElementById('offerViewModal');
    if (!modal) {
        modal = document.createElement('div');
        modal.id = 'offerViewModal';
        modal.className = 'modal';
        document.body.appendChild(modal);
    }
    
    modal.innerHTML = `
        <div class="modal-content" style="max-width: 800px; max-height: 90vh; overflow-y: auto;">
            <div class="modal-header">
                <h2>${offerData.title}</h2>
                <button class="close-btn" onclick="closeOfferViewModal()">&times;</button>
            </div>
            <div class="modal-body" style="padding: 2rem;">
                <div class="offer-details">
                    <div class="detail-section">
                        <h3>Informations générales</h3>
                        <p><strong>Entreprise:</strong> ${offerData.company}</p>
                        <p><strong>Localisation:</strong> ${offerData.location}</p>
                        <p><strong>Type de contrat:</strong> ${offerData.contractType}</p>
                        <p><strong>Durée:</strong> ${offerData.duration}</p>
                    </div>
                    
                    <div class="detail-section">
                        <h3>Description du poste</h3>
                        <p>${offerData.description}</p>
                    </div>
                    
                    ${offerData.technicalSkills && offerData.technicalSkills.length > 0 ? `
                    <div class="detail-section">
                        <h3>Compétences techniques requises</h3>
                        <div class="skills-list">
                            ${offerData.technicalSkills.map(skill => `<span class="skill-tag">${skill}</span>`).join('')}
                        </div>
                    </div>
                    ` : ''}
                    
                    ${offerData.desiredSkills && offerData.desiredSkills.length > 0 ? `
                    <div class="detail-section">
                        <h3>Compétences souhaitées</h3>
                        <div class="skills-list">
                            ${offerData.desiredSkills.map(skill => `<span class="skill-tag desired">${skill}</span>`).join('')}
                        </div>
                    </div>
                    ` : ''}
                    
                    ${offerData.softSkills && offerData.softSkills.length > 0 ? `
                    <div class="detail-section">
                        <h3>Compétences comportementales</h3>
                        <div class="skills-list">
                            ${offerData.softSkills.map(skill => `<span class="skill-tag soft">${skill}</span>`).join('')}
                        </div>
                    </div>
                    ` : ''}
                    
                    ${offerData.education && offerData.education.length > 0 ? `
                    <div class="detail-section">
                        <h3>Formation</h3>
                        <ul>
                            ${offerData.education.map(edu => `<li>${edu}</li>`).join('')}
                        </ul>
                    </div>
                    ` : ''}
                    
                    ${offerData.experience && offerData.experience.length > 0 ? `
                    <div class="detail-section">
                        <h3>Expérience</h3>
                        <ul>
                            ${offerData.experience.map(exp => `<li>${exp}</li>`).join('')}
                        </ul>
                    </div>
                    ` : ''}
                    
                    ${offerData.languages && offerData.languages.length > 0 ? `
                    <div class="detail-section">
                        <h3>Langues</h3>
                        <ul>
                            ${offerData.languages.map(lang => `<li>${lang}</li>`).join('')}
                        </ul>
                    </div>
                    ` : ''}
                </div>
            </div>
        </div>
    `;
    
    // Ajouter les styles CSS si ils n'existent pas
    addOfferViewStyles();
    
    // Afficher le modal
    modal.classList.add('active');
}

// Fonction pour fermer le modal de visualisation
function closeOfferViewModal() {
    const modal = document.getElementById('offerViewModal');
    if (modal) {
        modal.classList.remove('active');
    }
}

// Ajouter les styles CSS pour le modal de visualisation
function addOfferViewStyles() {
    if (!document.getElementById('offerViewStyles')) {
        const styles = document.createElement('style');
        styles.id = 'offerViewStyles';
        styles.textContent = `
            .detail-section {
                margin-bottom: 2rem;
                padding-bottom: 1rem;
                border-bottom: 1px solid #e5e7eb;
            }
            
            .detail-section:last-child {
                border-bottom: none;
            }
            
            .detail-section h3 {
                color: #1f2937;
                margin-bottom: 1rem;
                font-size: 1.2rem;
                font-weight: 600;
            }
            
            .skills-list {
                display: flex;
                flex-wrap: wrap;
                gap: 0.5rem;
            }
            
            .skill-tag {
                background: #3b82f6;
                color: white;
                padding: 0.25rem 0.75rem;
                border-radius: 1rem;
                font-size: 0.875rem;
                font-weight: 500;
            }
            
            .skill-tag.desired {
                background: #10b981;
            }
            
            .skill-tag.soft {
                background: #8b5cf6;
            }
            
            .detail-section ul {
                list-style-type: disc;
                margin-left: 1.5rem;
            }
            
            .detail-section li {
                margin-bottom: 0.5rem;
                line-height: 1.5;
            }
        `;
        document.head.appendChild(styles);
    }
}

// Fonction pour récupérer les données d'une offre par ID
function getOfferDataById(offerId) {
    return offersData[offerId] || null;
}

// Ajouter des IDs aux boutons "Voir" dans les cartes d'offres existantes
function updateOfferCards() {
    const offerCards = document.querySelectorAll('.offer-card');
    offerCards.forEach((card, index) => {
        const viewButton = card.querySelector('.action-btn');
        if (viewButton && viewButton.textContent === 'Voir') {
            viewButton.setAttribute('onclick', `viewOffer(${index + 1})`);
        }
        
        // Ajouter aussi le bouton supprimer si il n'existe pas
        const deleteButton = card.querySelectorAll('.action-btn')[1];
        if (deleteButton && deleteButton.textContent === 'Supprimer') {
            deleteButton.setAttribute('onclick', `deleteOffer(${index + 1})`);
        }
    });
}

// Initialize page
document.addEventListener('DOMContentLoaded', function() {
    // Add hover effects to existing offer cards
    document.querySelectorAll('.offer-card').forEach(addOfferCardHoverEffects);
    updateOfferCards();
    
    // Simulate navigation back to main page
    document.querySelector('.logo').addEventListener('click', function() {
        window.location.href = 'index.html';
    });

    // File input event listener
    document.getElementById('offerFileInput').addEventListener('change', function(e) {
        if (e.target.files.length > 0) {
            selectedFile = e.target.files[0];
            if (selectedFile.name.endsWith('.docx')) {
                updateOfferDropZone();
                updateUploadButton();
                
                // Auto-fill document name if empty
                const nameInput = document.getElementById('documentName');
                if (!nameInput.value.trim()) {
                    const fileName = selectedFile.name.replace('.docx', '');
                    nameInput.value = fileName;
                    updateUploadButton();
                }
            } else {
                showNotification('Veuillez sélectionner un fichier .docx', 'error');
                e.target.value = '';
                selectedFile = null;
            }
        }
    });

    // Document name input event listener
    document.getElementById('documentName').addEventListener('input', updateUploadButton);

    // Drag and drop functionality
    const offerDropZone = document.getElementById('offerDropZone');
    
    offerDropZone.addEventListener('dragover', function(e) {
        e.preventDefault();
        this.classList.add('dragover');
    });
    
    offerDropZone.addEventListener('dragleave', function(e) {
        e.preventDefault();
        this.classList.remove('dragover');
    });
    
    offerDropZone.addEventListener('drop', function(e) {
        e.preventDefault();
        this.classList.remove('dragover');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            const file = files[0];
            if (file.name.endsWith('.docx')) {
                selectedFile = file;
                updateOfferDropZone();
                updateUploadButton();
                
                // Auto-fill document name if empty
                const nameInput = document.getElementById('documentName');
                if (!nameInput.value.trim()) {
                    const fileName = file.name.replace('.docx', '');
                    nameInput.value = fileName;
                    updateUploadButton();
                }
            } else {
                showNotification('Veuillez déposer un fichier .docx', 'error');
            }
        }
    });
    
    // Fermer le modal si on clique en dehors
    document.addEventListener('click', function(e) {
        const modal = document.getElementById('offerViewModal');
        if (modal && e.target === modal) {
            closeOfferViewModal();
        }
    });
});

// Additional function for adding new offers (if needed)
function addNewOffer() {
    // This function can be implemented for the form-based offer addition
    console.log('Add new offer functionality to be implemented');
}