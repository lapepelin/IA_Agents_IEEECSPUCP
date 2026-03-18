const chatForm = document.getElementById('chatForm');
const userInput = document.getElementById('userInput');
const chatBox = document.getElementById('chatBox');
const sendBtn = document.getElementById('sendBtn');
const resetBtn = document.getElementById('resetBtn');

// Función para agregar mensajes al DOM
function addMessage(text, sender) {
  const msgDiv = document.createElement('div');
  msgDiv.className = `message ${sender}`;
  
  const contentDiv = document.createElement('div');
  contentDiv.className = 'msg-content';
  contentDiv.innerText = text; // Usa innerText para evitar inyección HTML
  
  msgDiv.appendChild(contentDiv);
  chatBox.appendChild(msgDiv);
  
  // Scrollear hacia abajo automáticamente
  chatBox.scrollTo({
    top: chatBox.scrollHeight,
    behavior: 'smooth'
  });
}

// Mostrar indicador de "escribiendo..."
function showTypingIndicator() {
  const indicator = document.createElement('div');
  indicator.id = 'typingIndicator';
  indicator.className = 'typing';
  indicator.innerText = 'El agente está pensando...';
  chatBox.appendChild(indicator);
  chatBox.scrollTo({ top: chatBox.scrollHeight, behavior: 'smooth' });
}

// Ocultar indicador
function removeTypingIndicator() {
  const indicator = document.getElementById('typingIndicator');
  if (indicator) {
    indicator.remove();
  }
}

// Bloquear input mientras responde
function setInputState(disabled) {
  userInput.disabled = disabled;
  sendBtn.disabled = disabled;
  if (!disabled) userInput.focus();
}

// Enviar mensaje al servidor
chatForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  
  const text = userInput.value.trim();
  if (!text) return;
  
  // 1. Mostrar mensaje del usuario
  addMessage(text, 'user');
  userInput.value = '';
  
  // 2. Preparar UI para esperar respuesta
  setInputState(true);
  showTypingIndicator();
  
  try {
    // 3. Llamar a nuestra propia API local Node.js
    const response = await fetch('/api/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ message: text })
    });
    
    if (!response.ok) throw new Error("Error en el servidor");
    
    const data = await response.json();
    
    removeTypingIndicator();
    addMessage(data.response, 'assistant');
    
  } catch (err) {
    console.error(err);
    removeTypingIndicator();
    addMessage("[Error] No me pude comunicar con el servidor backend.", 'assistant');
  } finally {
    setInputState(false);
  }
});

// Limpiar historial
resetBtn.addEventListener('click', async () => {
  if(!confirm("¿Deseas borrar la memoria de la conversación actual?")) return;
  
  try {
    await fetch('/api/reset', { method: 'POST' });
    chatBox.innerHTML = `
      <div class="message assistant">
        <div class="msg-content">Memoria borrada. ¡Empecemos de nuevo!</div>
      </div>
    `;
  } catch (err) {
    console.error("Error reseteando:", err);
  }
});
