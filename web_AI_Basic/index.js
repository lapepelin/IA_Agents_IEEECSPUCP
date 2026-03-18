require('dotenv').config();
const express = require('express');
const cors = require('cors');
const { OpenAI } = require('openai');
const path = require('path');
const fs = require('fs');

const app = express();
const port = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

// Inicializar el cliente compatible con OpenAI (para NVIDIA Nemotron)
const openai = new OpenAI({
  apiKey: process.env.LLM_API_KEY,
  baseURL: process.env.LLM_BASE_URL,
});

// Cargar el system prompt
let systemPrompt = "Eres un asistente de IA.";
try {
  systemPrompt = fs.readFileSync(path.join(__dirname, 'system_prompt.txt'), 'utf8');
} catch (error) {
  console.error("Error cargando system_prompt.txt. Se usará el default.");
}

// Historial en memoria para simplificar (solo para esta demo básica)
// En un entorno real se usaría una Base de Datos y IDs de sesión
let conversationHistory = [
  { role: "system", content: systemPrompt }
];

app.post('/api/chat', async (req, res) => {
  try {
    const userMessage = req.body.message;
    if (!userMessage) {
      return res.status(400).json({ error: "No message provided" });
    }

    // Agregar mensaje del usuario al historial
    conversationHistory.push({ role: "user", content: userMessage });

    // Llamar al LLM
    const completion = await openai.chat.completions.create({
      model: process.env.LLM_MODEL || "meta/llama-3.3-70b-instruct",
      messages: conversationHistory,
      temperature: 0.2,
      top_p: 0.7,
      max_tokens: 1024
    });

    const aiMessage = completion.choices[0].message.content;

    // Agregar respuesta al historial
    conversationHistory.push({ role: "assistant", content: aiMessage });

    // Mantener historial corto (10 interacciones = system + 20 pares aprox)
    if (conversationHistory.length > 21) {
      // Dejar system prompt intacto, pero borrar lo muy viejo
      conversationHistory = [
        conversationHistory[0], 
        ...conversationHistory.slice(-20)
      ];
    }

    res.json({ response: aiMessage });

  } catch (error) {
    console.error("Error from LLM:", error.message);
    // Eliminar el último mensaje si falló algo
    conversationHistory.pop();
    res.status(500).json({ error: "Internal Server Error" });
  }
});

app.post('/api/reset', (req, res) => {
  conversationHistory = [
    { role: "system", content: systemPrompt }
  ];
  res.json({ status: "success", message: "Historial borrado." });
});

app.listen(port, () => {
  console.log(`Server listening at http://localhost:${port}`);
});
