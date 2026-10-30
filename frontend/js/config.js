// Configuración PÚBLICA del frontend. Aquí NUNCA van API keys (OpenAI/Gemini).
// - Docker / localhost:3000 -> deja API_BASE_URL vacío (nginx redirige /api al backend).
// - GitHub Pages -> el workflow .github/workflows/pages.yml reescribe este archivo con
//   las variables del repositorio API_BASE_URL y GOOGLE_CLIENT_ID.
//   Si API_BASE_URL queda vacío en Pages, la página funciona en "Modo demo".
window.INTERVIEWAI_CONFIG = {
  API_BASE_URL: "",
  // Público por diseño (Google lo incrusta en cada página con su botón). No es un secreto.
  GOOGLE_CLIENT_ID: "331276943554-avobo5kt8llvuo7tsopufgn27ejfunb9.apps.googleusercontent.com"
};
