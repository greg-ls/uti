
/**
 * Génère et injecte le contenu de l'onglet comparaison dans le conteneur spécifié.
 * @param {string} containerId - L'id de la div où injecter le contenu.
 */
function renderComparison(containerId) {
  const container = document.getElementById(containerId);
  if (!container) {
    console.warn(`Conteneur avec id "${containerId}" introuvable.`);
    return;
  }

  // Contenu de démonstration pour comparaison de CVs
  container.innerHTML = `
    <div class="comparison-container">
      <h3>Comparaison des CVs</h3>
      <p>Voici les résultats de la comparaison des CVs sélectionnés :</p>
      <table class="comparison-table">
        <thead>
          <tr>
            <th>Nom</th>
            <th>Compétences</th>
            <th>Expérience</th>
            <th>Score</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>Jean Dupont</td>
            <td>JavaScript, Python</td>
            <td>5 ans</td>
            <td>85%</td>
          </tr>
          <tr>
            <td>Marie Curie</td>
            <td>Java, C++</td>
            <td>7 ans</td>
            <td>90%</td>
          </tr>
          <tr>
            <td>Paul Martin</td>
            <td>HTML, CSS, React</td>
            <td>3 ans</td>
            <td>78%</td>
          </tr>
        </tbody>
      </table>
    </div>
  `;
}

// Rendre la fonction globale pour pouvoir l'appeler depuis search.js
window.renderComparison = renderComparison;