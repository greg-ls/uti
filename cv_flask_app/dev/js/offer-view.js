// Variables globales pour stocker les données de l'offre
let currentOffer = null;

// Initialisation de la page
document.addEventListener('DOMContentLoaded', function() {
    loadOfferData();
});

// Charger les données de l'offre depuis l'URL ou le localStorage
function loadOfferData() {
    console.log('loadOfferData appelée');
    
    const urlParams = new URLSearchParams(window.location.search);
    const offerId = urlParams.get('id');
    console.log('ID depuis URL:', offerId);
    
    // Essayer de récupérer les données depuis le localStorage
    const storedOfferData = localStorage.getItem('currentOfferView');
    console.log('Données localStorage:', storedOfferData);
    
    if (storedOfferData) {
        try {
            currentOffer = JSON.parse(storedOfferData);
            console.log('Données parsées:', currentOffer);
            displayOfferData(currentOffer);
            localStorage.removeItem('currentOfferView');
            return;
        } catch (e) {
            console.error('Erreur lors du parsing des données d\'offre:', e);
        }
    }
    
    // Si pas de données dans le localStorage, essayer de récupérer par ID
    if (offerId) {
        currentOffer = getOfferDataById(offerId);
        if (currentOffer) {
            displayOfferData(currentOffer);
            return;
        }
    }
    
    // Données par défaut seulement si aucune autre source n'est disponible
    currentOffer = {
        id: offerId || 1,
        title: "Développeur Full Stack Senior",
        company: "TechCorp Innovation",
        location: "Paris",
        contractType: "CDI",
        duration: "Indéterminée",
        description: "Nous recherchons un développeur Full Stack Senior pour rejoindre notre équipe technique dynamique. Vous serez responsable du développement d'applications web modernes et participerez à l'architecture de nos solutions.",
        technicalSkills: ["JavaScript", "React", "Node.js", "MongoDB", "Git"],
        desiredSkills: ["TypeScript", "Docker", "AWS", "GraphQL"],
        softSkills: ["Travail en équipe", "Communication", "Autonomie", "Créativité"],
        education: ["Bac+5 en informatique ou équivalent", "Formation en développement web"],
        experience: ["5+ années d'expérience en développement Full Stack", "Expérience avec les frameworks modernes", "Connaissance des méthodologies Agile"],
        languages: ["Français : Courant", "Anglais : Technique"]
    };
    displayOfferData(currentOffer);
}

function getOfferDataById(offerId) {
    // Simulation de données d'offres - identique à celle dans offers.js
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

// Ajouter une fonction pour formater l'affichage comme dans l'onglet comparaison
function displayOfferData(offer) {
    // Mettre à jour le titre de la page
    document.title = `${offer.title} - ${offer.company} | Éditeur de CV par UTI`;
    
    // Mettre à jour le titre et les métadonnées
    document.getElementById('offerTitle').textContent = offer.title;
    document.getElementById('offerCompany').textContent = offer.company;
    document.getElementById('offerLocation').textContent = offer.location;
    document.getElementById('contractType').textContent = offer.contractType;
    
    // Mettre à jour les détails
    document.getElementById('detailCompany').textContent = offer.company;
    document.getElementById('detailTitle').textContent = offer.title;
    document.getElementById('detailLocation').textContent = offer.location;
    document.getElementById('detailContract').textContent = offer.contractType;
    document.getElementById('detailDuration').textContent = offer.duration;
    document.getElementById('offerDescription').innerHTML = `<p>${offer.description}</p>`;
    
    // Mettre à jour les compétences avec animation
    updateSkillsList('technicalSkills', offer.technicalSkills, 'required');
    updateSkillsList('desiredSkills', offer.desiredSkills, 'desired');
    updateSkillsList('softSkills', offer.softSkills, 'soft');
    
    // Mettre à jour les exigences
    updateRequirementsList('educationRequirements', offer.education);
    updateRequirementsList('experienceRequirements', offer.experience);
    updateRequirementsList('languageRequirements', offer.languages);
    
    // Ajouter une animation d'apparition
    animateContentAppearance();
}

// Ajouter une animation d'apparition du contenu
function animateContentAppearance() {
    const sections = document.querySelectorAll('.offer-details-section, .skills-analysis-section, .requirements-section, .actions-section');
    
    sections.forEach((section, index) => {
        section.style.opacity = '0';
        section.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            section.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
            section.style.opacity = '1';
            section.style.transform = 'translateY(0)';
        }, index * 150);
    });
}

// Mettre à jour une liste de compétences avec animation
function updateSkillsList(elementId, skills, skillType) {
    const container = document.getElementById(elementId);
    container.innerHTML = '';
    
    skills.forEach((skill, index) => {
        const skillTag = document.createElement('span');
        skillTag.className = `skill-tag ${skillType}`;
        skillTag.textContent = skill;
        skillTag.style.opacity = '0';
        skillTag.style.transform = 'scale(0.8)';
        container.appendChild(skillTag);
        
        // Animation d'apparition des tags
        setTimeout(() => {
            skillTag.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
            skillTag.style.opacity = '1';
            skillTag.style.transform = 'scale(1)';
        }, index * 100);
    });
}

// Mettre à jour une liste d'exigences
function updateRequirementsList(elementId, requirements) {
    const container = document.getElementById(elementId);
    container.innerHTML = '';
    
    requirements.forEach(requirement => {
        const li = document.createElement('li');
        li.textContent = requirement;
        container.appendChild(li);
    });
}

// Récupérer une offre par ID (simulation)
function getOfferById(id) {
    // Ici, vous pourriez faire un appel API ou récupérer depuis le localStorage
    // Pour la démonstration, on retourne des données statiques
    return null; // Retournera null pour utiliser les données par défaut
}

// Fonctions de navigation et d'actions
function goBack() {
    window.location.href = 'offers.html';
}

function editOffer() {
    if (currentOffer) {
        // Simuler l'édition avec une alerte ou un modal
        const newTitle = prompt('Nouveau titre:', currentOffer.title);
        if (newTitle && newTitle !== currentOffer.title) {
            currentOffer.title = newTitle;
            displayOfferData(currentOffer);
            showNotification('Offre mise à jour avec succès!');
        }
    }
}

function duplicateOffer() {
    if (currentOffer) {
        if (confirm('Voulez-vous dupliquer cette offre ?')) {
            // Logique pour dupliquer l'offre
            console.log('Duplication de l\'offre:', currentOffer);
            // Rediriger vers la création d'une nouvelle offre avec les données pré-remplies
        }
    }
}

function deleteOffer() {
    if (currentOffer) {
        if (confirm('Êtes-vous sûr de vouloir supprimer cette offre ? Cette action est irréversible.')) {
            // Logique pour supprimer l'offre
            console.log('Suppression de l\'offre:', currentOffer);
            // Rediriger vers la liste des offres
            window.location.href = 'offers.html';
        }
    }
}