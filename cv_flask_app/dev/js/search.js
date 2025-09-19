document.addEventListener('DOMContentLoaded', function() {
    // Initialiser la fonctionnalité de comparaison dans le contexte de recherche
    initializeSearchComparison();
});

function initializeSearchComparison() {
    // Charger le contenu de comparaison dans la section de recherche
    const searchContent = document.getElementById('searchContent');
    
    // Créer le même contenu que l'onglet comparaison
    searchContent.innerHTML = `
        <div class="comparison-container">
            <!-- Le contenu sera identique à celui de l'onglet comparaison -->
        </div>
    `;
    
    // Initialiser les fonctionnalités de comparaison
    if (typeof initializeComparison === 'function') {
        renderComparison('searchContent');
    }
}

function goHome() {
    window.location.href = 'index.html';
}