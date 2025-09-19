function initializeChat() {
    loadChatInterface();
    initializeChatResizer();
}

function loadChatInterface() {
    const assistantPanel = document.getElementById('assistantPanel');
    assistantPanel.innerHTML = `
    <div class="chat-header">
    <h3>🤖 Assistant IA</h3>
    <div class="chat-status">En ligne</div>
    </div>
    
    <div class="selection-info" id="selectionInfo" style="display: none;">
    <div class="selection-label">Paragraphe sélectionné :</div>
    <div class="selected-text" id="selectedText"></div>
    </div>
    
    <div class="chat-messages" id="chatMessages">
    <div class="message assistant-message">
    <div class="message-content">
    👋 Bonjour ! Je suis votre assistant IA pour l'édition de CV. 
    Sélectionnez un paragraphe et demandez-moi des suggestions d'amélioration !
    </div>
    </div>
    </div>
    
    <div class="chat-resizer" id="chatResizer"></div>
    
    <div class="chat-input-container" id="chatInputContainer">
    <textarea id="chatInput" placeholder="Demandez des suggestions pour améliorer votre CV..." rows="3"></textarea>
    <button id="sendButton" onclick="sendMessage()">Envoyer</button>
    </div>
    `;
}

function initializeChatResizer() {
    const resizer = document.getElementById('chatResizer');
    const chatMessages = document.getElementById('chatMessages');
    const inputContainer = document.getElementById('chatInputContainer');
    let isResizing = false;

    resizer.addEventListener('mousedown', (e) => {
        isResizing = true;
        document.body.style.cursor = 'row-resize';
        document.body.style.userSelect = 'none';
        e.preventDefault();
    });

    document.addEventListener('mousemove', (e) => {
        if (!isResizing) return;

        const assistantPanel = document.getElementById('assistantPanel');
        const rect = assistantPanel.getBoundingClientRect();
        const headerHeight = document.querySelector('.chat-header').offsetHeight;
        const selectionInfo = document.getElementById('selectionInfo');
        const selectionHeight = selectionInfo.style.display !== 'none' ? selectionInfo.offsetHeight : 0;
        
        // Calculer la position relative de la souris dans le panel
        const mouseY = e.clientY - rect.top;
        const availableHeight = rect.height - headerHeight - selectionHeight - 4; // 4px pour le resizer
        
        // Définir les limites min/max
        const minMessagesHeight = 200;
        const minInputHeight = 120;
        const maxMessagesHeight = availableHeight - minInputHeight;
        
        let newMessagesHeight = mouseY - headerHeight - selectionHeight;
        newMessagesHeight = Math.max(minMessagesHeight, Math.min(maxMessagesHeight, newMessagesHeight));
        
        const newInputHeight = availableHeight - newMessagesHeight;
        
        // Appliquer les nouvelles hauteurs
        chatMessages.style.height = `${newMessagesHeight}px`;
        chatMessages.style.flex = 'none';
        inputContainer.style.height = `${newInputHeight}px`;
    });

    document.addEventListener('mouseup', () => {
        if (isResizing) {
            isResizing = false;
            document.body.style.cursor = '';
            document.body.style.userSelect = '';
        }
    });
}

function sendMessage() {
    const chatInput = document.getElementById('chatInput');
    const message = chatInput.value.trim();
    
    if (!message) return;
    
    // Ajouter le message de l'utilisateur
    addMessage(message, 'user');
    
    // Vider l'input
    chatInput.value = '';
    
    // Simuler une réponse de l'assistant
    setTimeout(() => {
    const response = generateResponse(message);
    addMessage(response, 'assistant');
    }, 1000);
}

function addMessage(content, sender) {
    const chatMessages = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}-message`;
    
    messageDiv.innerHTML = `
    <div class="message-content">${content}</div>
    <div class="message-time">${new Date().toLocaleTimeString()}</div>
    `;
    
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function generateResponse(message) {
    // Réponses simulées basées sur le contenu du message
    const responses = [
    "Excellente question ! Pour améliorer ce paragraphe, je suggère d'ajouter des métriques quantifiables.",
    "Ce paragraphe pourrait bénéficier de mots-clés plus spécifiques à votre secteur d'activité.",
    "Pensez à utiliser des verbes d'action plus impactants pour décrire vos réalisations.",
    "Il serait intéressant d'ajouter des exemples concrets de vos succès dans ce domaine."
    ];
    
    return responses[Math.floor(Math.random() * responses.length)];
}

// Gérer l'envoi avec Enter
document.addEventListener('DOMContentLoaded', function() {
    document.addEventListener('keydown', function(e) {
    const chatInput = document.getElementById('chatInput');
    if (e.key === 'Enter' && !e.shiftKey && document.activeElement === chatInput) {
    e.preventDefault();
    sendMessage();
    }
    });
});

/* js/comparison.js */
function initializeComparison() {
    console.log('Comparison initialized');
}