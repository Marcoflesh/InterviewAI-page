// Configuración PÚBLICA del frontend. Aquí NUNCA van API keys (OpenAI/Gemini).
// - Docker / localhost:3000 -> deja API_BASE_URL vacío (nginx redirige /api al backend).
// - GitHub Pages -> el workflow .github/workflows/pages.yml reescribe este archivo con
//   las variables del repositorio API_BASE_URL y GOOGLE_CLIENT_ID.
//   Si API_BASE_URL queda vacío en Pages, la página funciona en "Modo demo".
window.INTERVIEWAI_CONFIG = {
  API_BASE_URL: "",
  GOOGLE_CLIENT_ID: ""
};
