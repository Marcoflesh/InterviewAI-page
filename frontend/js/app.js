// =============================================================================
// InterviewAI v0.4.0
// - Agentes de IA: GPT-4o mini (Entrevistador) y Gemini 3.8 Flash (Evaluador),
//   ejecutados SOLO en el backend. Ninguna API key vive en el navegador.
// - Escala crítica de evaluación 0 a 5 y aislamiento de historial por usuario.
// - Sin backend (GitHub Pages sin API) la página funciona en "modo demo" con el
//   analizador local; con backend usa los agentes de IA.
// =============================================================================

// Configuración pública (frontend/js/config.js). Aquí NO van llaves secretas.
const PUBLIC_CONFIG = Object.assign(
  { API_BASE_URL: "", GOOGLE_CLIENT_ID: "" },
  window.INTERVIEWAI_CONFIG || {}
);
// En GitHub Pages no hay servidor: la página funciona en "Modo demo". Con ?local=1 usa el backend
// que corre en TU computadora (Docker encendido), y lo recuerda en este navegador (?local=0 lo quita).
// Solo se permite localhost: un enlace no puede mandar tus datos a otro servidor.
const LOCAL_BACKEND = "http://localhost:8000";
const ON_STATIC_HOST = !/^(localhost|127\.0\.0\.1|)$/.test(location.hostname);
const USE_LOCAL_BACKEND = (() => {
  if (!ON_STATIC_HOST || PUBLIC_CONFIG.API_BASE_URL) return false;
  try {
    const flag = new URLSearchParams(location.search).get("local");
    if (flag === "1") localStorage.setItem("interviewai_local_backend", "1");
    if (flag === "0") localStorage.removeItem("interviewai_local_backend");
    return localStorage.getItem("interviewai_local_backend") === "1";
  } catch (_) { return false; }
})();
const API_BASE = USE_LOCAL_BACKEND ? LOCAL_BACKEND : String(PUBLIC_CONFIG.API_BASE_URL || "").replace(/\/+$/, "");
const TOKEN_KEY = "interviewai_token";

function escapeHtml(value) {
  return String(value ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

function getToken() {
  try { return sessionStorage.getItem(TOKEN_KEY) || ""; } catch (_) { return ""; }
}

function setToken(token) {
  try {
    if (token) sessionStorage.setItem(TOKEN_KEY, token);
    else sessionStorage.removeItem(TOKEN_KEY);
  } catch (_) {}
}

// Llama al backend. Devuelve { ok, status, data, offline }.
// offline = true solo cuando no hubo respuesta del servidor (red caída o sin backend).
async function apiFetch(path, options = {}, timeoutMs = 45000) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  const headers = Object.assign({ "Content-Type": "application/json" }, options.headers || {});
  const token = getToken();
  if (token) headers.Authorization = `Bearer ${token}`;
  try {
    const resp = await fetch(API_BASE + path, Object.assign({}, options, { headers, signal: controller.signal }));
    let data = null;
    try { data = await resp.json(); } catch (_) {}
    // Un 404 de un hosting estático (sin /api) equivale a "no hay backend".
    const looksStatic = resp.status === 404 && (!data || !("detail" in data));
    return { ok: resp.ok, status: resp.status, data, offline: looksStatic };
  } catch (_) {
    return { ok: false, status: 0, data: null, offline: true };
  } finally {
    clearTimeout(timer);
  }
}

function apiErrorMessage(result, fallback) {
  const d = result && result.data && result.data.detail;
  if (typeof d === "string") return d;
  if (Array.isArray(d) && d.length) return "Revisa los datos: " + d.map((e) => e.msg).join("; ");
  return fallback;
}

async function detectBackend() {
  const r = await apiFetch("/api/health", { method: "GET" }, 5000);
  // Si el servidor responde (aunque sea con error de base de datos) NO se pasa a modo demo:
  // se muestra la causa real para que se pueda arreglar.
  appState.backendOnline = !!(r.data && r.data.service);
  const badge = document.getElementById("mode-badge");
  if (badge) {
    badge.classList.toggle("hidden", appState.backendOnline);
    if (ON_STATIC_HOST && !appState.backendOnline) {
      // Enlace para usar el InterviewAI completo que corre en la computadora de quien presenta.
      const link = USE_LOCAL_BACKEND ? "?local=0" : "?local=1";
      badge.innerHTML = USE_LOCAL_BACKEND
        ? `Modo demo · no encontré InterviewAI en esta computadora (<a href="${link}">quitar</a>)`
        : `Modo demo · <a href="${link}" title="Usa el servidor de esta computadora (Docker encendido)">usar mi computadora</a>`;
    }
  }
  if (appState.backendOnline && r.data.database && !r.data.database.ok) {
    showAuthFeedback("Servidor con problema: " + r.data.database.detail);
  }
  return appState.backendOnline;
}

// Contraseñas del modo demo: se guardan con PBKDF2 (nunca en texto plano).
async function hashDemoPassword(password, saltHex) {
  const salt = saltHex || Array.from(crypto.getRandomValues(new Uint8Array(16)))
    .map((b) => b.toString(16).padStart(2, "0")).join("");
  const key = await crypto.subtle.importKey("raw", new TextEncoder().encode(password), "PBKDF2", false, ["deriveBits"]);
  const bits = await crypto.subtle.deriveBits(
    { name: "PBKDF2", salt: new TextEncoder().encode(salt), iterations: 210000, hash: "SHA-256" }, key, 256);
  const hex = Array.from(new Uint8Array(bits)).map((b) => b.toString(16).padStart(2, "0")).join("");
  return `${salt}$${hex}`;
}

const CAREER_CATALOG = [
  {
    code: "ITC",
    name: "Ingeniería en Tecnologías Computacionales (Software)",
    roles: ["Software Engineer Intern", "Junior Full-Stack Developer", "Backend Developer"],
    lexicon: [
      "api", "rest", "graphql", "sql", "postgres", "mysql", "mongo", "base de datos", "indice",
      "query", "consulta", "latencia", "cache", "redis", "docker", "contenedor", "kubernetes",
      "git", "rama", "merge", "pull request", "test", "prueba", "unitario", "integracion",
      "ci/cd", "pipeline", "backend", "frontend", "react", "angular", "vue", "python", "fastapi",
      "django", "flask", "node", "java", "c++", "arquitectura", "microservicio", "monolito",
      "autenticacion", "oauth", "jwt", "seguridad", "endpoint", "bug", "error", "debug", "logs",
      "memoria", "ram", "cpu", "algoritmo", "complejidad", "asincrono", "concurrencia", "hilo",
      "esquema", "migracion", "css", "html", "javascript", "typescript", "servidor", "nube", "aws"
    ],
    resources: [
      { title: "Cómo cuantificar impacto de ingeniería en entrevistas", provider: "Tech Interview Handbook", url: "https://www.techinterviewhandbook.org/behavioral-interview/" },
      { title: "Arquitectura Backend y Diseño de APIs", provider: "roadmap.sh", url: "https://roadmap.sh/backend" }
    ],
    questions: [
      "Cuéntame sobre una ocasión en la que detectaste un error crítico en un proyecto de software poco antes de la entrega. ¿Cuál era el contexto, qué acciones técnicas ejecutaste para aislarlo y cuál fue el impacto medible en el despliegue?",
      "Describe algún proyecto donde una consulta a base de datos o endpoint de API era demasiado lento. ¿Qué diagnóstico realizaste, qué cambios implementaste y en qué porcentaje o milisegundos mejoró la latencia?",
      "Platícame de una situación en la que tuviste que trabajar sobre código legado o mal documentado. ¿Qué estrategia seguiste para modificarlo sin romper funcionalidades existentes y qué resultado obtuviste?",
      "Háblame de un sistema o aplicación que hayas construido desde cero en equipo. ¿Qué responsabilidad técnica asumiste tú directamente y qué resultados lograron en la evaluación o producción?",
      "Recuerda alguna vez en que tuviste un desacuerdo técnico o un conflicto de integración en Git con otro desarrollador. ¿Cómo lo abordaste y cómo mejoró el flujo de trabajo del equipo?",
      "Describe una experiencia implementando autenticación, manejo de sesiones o protección de rutas en una aplicación web. ¿Qué vulnerabilidades preveniste y cuál fue el resultado final?",
      "Cuéntame de algún proyecto en el que tuviste que aprender un lenguaje, framework o herramienta de nube desconocido en pocos días. ¿Qué plan seguiste y qué entregable lograste?",
      "Comparte un caso donde el proceso de pruebas o despliegue manual consumía demasiado tiempo. ¿Qué automatizaste mediante scripts o pruebas unitarias y cuánto tiempo ahorraron?",
      "Platícame sobre una ocasión en la que enfrentaste problemas de compatibilidad entre entornos. ¿Cómo estandarizaste la configuración con Docker o variables de entorno y qué impacto tuvo?",
      "Describe un sprint o entrega final donde los requerimientos cambiaron a mitad del desarrollo. ¿Cómo renegociaste el alcance técnico y qué porcentaje de los objetivos se cumplió?",
      "Cuéntame sobre un proyecto donde integraste una API externa que tenía fallos o límites de tasa. ¿Cómo manejaste los errores o reintentos y qué experiencia obtuvo el usuario final?",
      "Relata una situación en la que el procesamiento de una colección grande de datos en memoria causaba lentitud. ¿Qué estructura de datos o algoritmo aplicaste y qué mejora lograste?",
      "Háblame de una vez en que trabajaste con un usuario o cliente no técnico cuyos requerimientos eran ambiguos. ¿Cómo aterrizaste la especificación y cuál fue el resultado?",
      "Describe un reto importante que hayas resuelto en el frontend para que una interfaz fuera rápida, limpia y responsiva. ¿Qué decisiones de diseño tomaste y cómo impactó la usabilidad?",
      "Cuéntame de algún despliegue o demostración en vivo donde algo falló. ¿Cómo reaccionaste en el momento para mitigar el problema y qué cambiaste en tu proceso después?",
      "Cuéntame sobre un problema de condiciones de carrera (race conditions), bloqueos o manejo asíncrono que hayas enfrentado. ¿Cómo lo reprodujiste y qué mecanismo de sincronización aplicaste?",
      "Describe una situación en la que tuviste que modificar el esquema de una base de datos que ya contenía información importante. ¿Cómo diseñaste la migración sin perder datos?",
      "Platícame de alguna tarea de programación cuya complejidad subestimaste inicialmente. ¿Cómo lo comunicaste al equipo y qué ajuste técnico hiciste para cumplir con la entrega?",
      "Háblame de un error que ocurría únicamente en un entorno compartido y no en tu máquina local. ¿Qué logs estructurados o trazas implementaste para descubrir la causa raíz?",
      "Describe alguna ocasión en la que un servicio o interfaz web incrementaba su consumo de RAM con el tiempo. ¿Cómo perfilaste la memoria y qué cambio liberó los recursos?",
      "Cuéntame de una vez en que ayudaste a un compañero de equipo a destrabar un problema técnico o a configurar su entorno. ¿Cómo documentaste la solución para el resto del equipo?",
      "Platícame sobre un módulo donde datos malformados de entrada provocaban caídas del sistema. ¿Qué capa de validación de esquemas implementaste y cómo mejoró la estabilidad?"
    ]
  },
  {
    code: "ISD",
    name: "Ciencia de Datos e Inteligencia Artificial",
    roles: ["Data Scientist Jr", "Machine Learning Engineer Intern", "Data Analyst"],
    lexicon: [
      "dataset", "datos", "modelo", "entrenamiento", "validacion", "overfitting", "sobreajuste",
      "regularizacion", "f1", "auc", "roc", "precision", "recall", "exactitud", "rmse", "mae",
      "mape", "regresion", "clasificacion", "clustering", "segmentacion", "feature", "variable",
      "pipeline", "etl", "sql", "python", "pandas", "numpy", "scikit", "pytorch", "tensorflow",
      "llm", "prompt", "agente", "langgraph", "json", "sesgo", "anonimizacion", "correlacion",
      "hipotesis", "estadistica", "series de tiempo", "estacionalidad", "drift", "baseline",
      "smote", "desbalance", "tablero", "dashboard", "kpi", "distribucion", "outliers", "nulos"
    ],
    resources: [
      { title: "Traducción de Métricas ML (F1, AUC, RMSE) a KPIs de Negocio", provider: "Google Developers ML", url: "https://developers.google.com/machine-learning/crash-course" },
      { title: "Orquestación de Agentes con LangGraph", provider: "LangChain Docs", url: "https://docs.langchain.com/oss/python/langgraph/overview" }
    ],
    questions: [
      "Cuéntame sobre un proyecto de datos donde el dataset original tenía valores faltantes, ruido o inconsistencias severas. ¿Qué pipeline de limpieza diseñaste y cómo impactó en el desempeño del modelo?",
      "Describe una ocasión en la que tuviste que explicar los resultados de un modelo predictivo o análisis estadístico a una audiencia no técnica. ¿Cómo tradujiste las métricas y qué decisión se tomó?",
      "Platícame de un problema de clasificación donde la clase de interés era muy minoritaria. ¿Qué técnicas de muestreo o métricas elegiste en lugar de accuracy y qué F1-score o ROC-AUC alcanzaste?",
      "Háblame de un modelo que obtenía excelentes métricas en entrenamiento pero fallaba en validación. ¿Cómo diagnosticaste el sobreajuste y cuánto mejoró en datos nuevos?",
      "Describe un proyecto en el que utilizaste modelos de lenguaje (LLMs) o agentes para automatizar una tarea. ¿Cómo estructuraste los prompts para asegurar salidas JSON válidas y qué tasa de éxito lograste?",
      "Cuéntame de una situación en la que identificaste un riesgo de privacidad de datos personales o sesgo en un dataset. ¿Qué acciones de anonimización o auditoría implementaste?",
      "Relata un caso donde los algoritmos estándar no superaban la línea base. ¿Qué nuevas variables (feature engineering) creaste y cuánto incrementó el poder predictivo?",
      "Describe una experiencia extrayendo y agregando información compleja desde bases de datos SQL con múltiples tablas. ¿Cómo estructuraste tus consultas y qué hallazgo clave descubriste?",
      "Platícame de alguna vez en que el equipo quería usar un modelo complejo pero una solución más simple resolvía mejor el problema. ¿Cómo evaluaste el costo-beneficio en latencia y precisión?",
      "Háblame de cómo has validado la calidad de un sistema de IA cuando no existían etiquetas limpias al inicio. ¿Cómo construiste el conjunto de validación y qué concordancia lograste?",
      "Describe un proyecto de pronóstico de series de tiempo. ¿Cómo manejaste la estacionalidad y en cuánto redujiste el error (MAE o MAPE) frente al método anterior?",
      "Cuéntame sobre un proyecto en equipo donde era difícil rastrear qué versión de datos y código produjo el mejor modelo. ¿Qué prácticas de reproducibilidad implementaste?",
      "Platícame de un tablero analítico que hayas diseñado para monitorear un proceso. ¿Qué indicadores seleccionaste y cómo ayudó a detectar anomalías?",
      "Describe una ocasión en la que necesitabas extraer patrones o métricas cuantitativas de texto libre. ¿Cómo combinaste expresiones regulares o NLP y qué precisión obtuviste?",
      "Háblame de un análisis exploratorio donde los datos refutaron la hipótesis principal de tu equipo. ¿Cómo presentaste la evidencia y hacia dónde pivotaron el proyecto?",
      "Cuéntame sobre un proyecto donde detectaste fuga de información (data leakage) entre entrenamiento y prueba. ¿Cómo identificaste la variable filtrada y corregiste la validación?",
      "Describe una ocasión en la que un modelo de IA o pipeline era demasiado lento de ejecutar. ¿Qué técnicas de optimización, caché o batching aplicaste y cuánto bajó la latencia?",
      "Platícame de un proyecto donde antes de entrenar un modelo complejo construiste una heurística o baseline simple. ¿Qué aprendiste de ese baseline?",
      "Háblame de un proyecto de clustering o segmentación no supervisada. ¿Cómo elegiste el número óptimo de clusters y validaste que tuvieran sentido práctico?",
      "Describe un reto al cruzar fuentes de datos con distintas granularidades o zonas horarias. ¿Cómo normalizaste el modelo de datos sin duplicar registros?",
      "Cuéntame de una solicitud ambigua donde tuviste que definir cuál era realmente la variable objetivo (target) y la métrica de evaluación.",
      "Platícame sobre cómo has evaluado o diseñado el monitoreo de deriva de datos (data drift) cuando cambia la distribución de entrada con el tiempo."
    ]
  },
  {
    code: "IIS",
    name: "Ingeniería Industrial y de Sistemas",
    roles: ["Supply Chain Analyst", "Continuous Improvement Intern", "Operations Coordinator"],
    lexicon: [
      "vsm", "mapa de valor", "tiempo de ciclo", "takt", "cuello de botella", "balanceo", "linea",
      "5s", "kaizen", "lean", "six sigma", "ishikawa", "pareto", "causa raiz", "merma", "defecto",
      "retrabajo", "calidad", "oee", "smed", "tpm", "mantenimiento", "inventario", "abc", "eoq",
      "reorden", "stock", "almacen", "picking", "packing", "otif", "sla", "logistica", "ruta",
      "transporte", "layout", "planta", "estacion", "ergonomia", "seguridad", "sop", "estandar",
      "simulacion", "capacidad", "productividad", "eficiencia", "roi", "costo", "cpk", "control"
    ],
    resources: [
      { title: "Cuantificación de Proyectos Lean Six Sigma (OEE y Tiempo de Ciclo)", provider: "ASQ Six Sigma", url: "https://asq.org/quality-resources/six-sigma" }
    ],
    questions: [
      "Cuéntame sobre un proyecto donde analizaste un proceso productivo o de servicio con tiempos de espera elevados. ¿Qué herramientas aplicaste y en qué porcentaje redujiste el tiempo de ciclo?",
      "Describe una situación en la que propusiste un nuevo estándar operativo y encontraste resistencia al cambio. ¿Qué acciones tomaste para involucrar al equipo y qué adopción lograste?",
      "Platícame de un caso donde existía exceso de inventario o quiebres de stock frecuentes. ¿Qué modelo de punto de reorden o clasificación ABC implementaste y qué impacto generó?",
      "Háblame de un problema recurrente de defectos o retrabajo. ¿Cómo utilizaste herramientas de calidad (Ishikawa, Pareto o Six Sigma) para erradicar la causa raíz y cuánto bajó la merma?",
      "Describe una ocasión en la que el retraso de un proveedor puso en riesgo una entrega crítica. ¿Qué plan de contingencia ejecutaste y cómo aseguraste el nivel de servicio?",
      "Cuéntame de algún proyecto donde optimizaste el layout de un almacén o celda de manufactura. ¿Cómo analizaste el flujo y cuántos metros o minutos por lote ahorraste?",
      "Relata una experiencia utilizando simulación de procesos para evaluar escenarios antes de invertir recursos. ¿Qué variables modelaste y qué recomendación validaste?",
      "Platícame de un proyecto donde coordinaste a personas de distintas áreas con prioridades encontradas. ¿Cómo alineaste los entregables mediante indicadores y qué resultado obtuvieron?",
      "Describe un análisis realizado para incrementar el OEE o reducir paros no programados. ¿Qué pérdidas atacaste mediante SMED o TPM y cuántos puntos subió la disponibilidad?",
      "Háblame de un reto logístico relacionado con costos de transporte o rutas de entrega. ¿Cómo reestructuraste las rutas y qué porcentaje de ahorro lograste?",
      "Cuéntame de una ocasión en la que detectaste un riesgo ergonómico o de seguridad industrial en una estación de trabajo. ¿Qué controles implementaste y cómo impactó al área?",
      "Describe un proceso que dependía de la experiencia informal de una sola persona. ¿Cómo lo estandarizaste en un SOP y cuánto se redujo la curva de aprendizaje?",
      "Platícame de una propuesta de mejora en la que tuviste que justificar la inversión. ¿Cómo calculaste el ROI o periodo de recuperación y qué decisión se tomó?",
      "Relata un momento en el que un imprevisto detuvo una operación importante. ¿Cómo priorizaste las acciones en las primeras horas y qué resultado obtuviste?",
      "Háblame de algún proceso donde la captura manual en hojas de cálculo generaba errores. ¿Cómo estandarizaste la captura o los tableros y cuántas horas semanales liberaste?",
      "Cuéntame sobre un proyecto donde utilizaste gráficos de control estadístico (CEP) o capacidad de proceso (Cp, Cpk) para reducir la variabilidad de una operación.",
      "Describe una ocasión en la que existían estaciones sobrecargadas y otras con tiempo ocioso. ¿Cómo redistribuiste las cargas respecto al Takt Time y qué eficiencia alcanzaste?",
      "Platícame de una situación en la que acordaste niveles de servicio (SLA) entre dos departamentos como almacén y producción. ¿Cómo lograste un acuerdo medible?",
      "Háblame de una mejora enfocada en reducir el tiempo de preparación de pedidos (picking/packing) reorganizando las ubicaciones por rotación ABC.",
      "Describe un recorrido en piso donde identificaste desperdicios (mudas Lean) de transporte o movimientos innecesarios. ¿Qué evento Kaizen ejecutaste?",
      "Cuéntame cómo implementaste y auditaste una iniciativa de orden y limpieza 5S para lograr que se sostuviera en el tiempo.",
      "Platícame de un proyecto donde estructuraste la explosión de materiales (BOM / MRP) y tiempos de entrega (lead times) para evitar faltantes en línea."
    ]
  },
  {
    code: "IMT",
    name: "Ingeniería Mecatrónica y Automatización",
    roles: ["Automation Engineer Jr", "Embedded Systems Intern", "Robotics Engineer"],
    lexicon: [
      "plc", "ladder", "microcontrolador", "arduino", "esp32", "stm32", "raspberry", "sensor",
      "actuador", "motor", "servomotor", "paso a paso", "pid", "lazo cerrado", "control",
      "sobreimpulso", "pwm", "adc", "ruido", "filtro", "osciloscopio", "multimetro", "senal",
      "cad", "solidworks", "inventor", "cnc", "impresion 3d", "tolerancia", "mecanismo", "pcb",
      "circuito", "potencia", "rele", "transistor", "interrupcion", "isr", "rtos", "firmware",
      "i2c", "spi", "uart", "can", "modbus", "mqtt", "vision", "camara", "cinematica", "robot",
      "torque", "neumatico", "hidraulico", "valvula", "hmi", "scada"
    ],
    resources: [
      { title: "Diagnóstico Electromecánico y Sistemas de Control", provider: "IEEE Robotics & Automation", url: "https://www.ieee-ras.org/" }
    ],
    questions: [
      "Cuéntame sobre un proyecto mecatrónico donde integraste sensores, actuadores y un microcontrolador o PLC. ¿Qué problema de ruido o sincronización resolviste y qué precisión alcanzaste?",
      "Describe una ocasión en la que un prototipo o sistema automatizado presentaba fallas intermitentes. ¿Qué metodología de diagnóstico con instrumentos seguiste para aislar la falla?",
      "Platícame de algún sistema de control en lazo cerrado (PID) que hayas implementado. ¿Cómo lo sintonizaste para reducir el sobreimpulso y qué respuesta temporal lograste?",
      "Háblame de un proyecto donde las decisiones del diseño mecánico afectaban a la electrónica o al firmware. ¿Cómo coordinaste las restricciones y qué retrabajos evitaste?",
      "Describe una secuencia de automatización industrial programada en PLC. ¿Cómo incluiste las condiciones de paro de emergencia e interbloqueos de seguridad?",
      "Cuéntame de una pieza o mecanismo que diseñaste en CAD y fabricaste mediante impresión 3D o CNC. ¿Qué problema de tolerancias o resistencia resolviste en tus iteraciones?",
      "Relata una situación en la que un componente electrónico o actuador clave no estaba disponible. ¿Cómo evaluaste alternativas en hojas de datos (datasheets) y qué resultado obtuviste?",
      "Platícame sobre un desarrollo en C/C++ para microcontroladores donde el uso de bloqueos afectaba la respuesta. ¿Cómo reestructuraste el código con interrupciones o timers?",
      "Describe un proyecto donde utilizaste visión artificial o sensores para guiar un mecanismo. ¿Cómo compensaste las variaciones del entorno y qué tasa de acierto lograste?",
      "Cuéntame de una experiencia realizando pruebas con potencia eléctrica o neumática. ¿Qué protocolo de verificación aplicaste antes de energizar para prevenir daños?",
      "Háblame de una tarjeta PCB o etapa de potencia que hayas diseñado. ¿Cómo manejaste la disipación térmica y el aislamiento entre etapa lógica y de potencia?",
      "Describe un reto al comunicar dispositivos mediante I2C, SPI, UART, CAN o Modbus. ¿Cómo identificaste pérdidas de datos y qué solución implementaste?",
      "Platícame de una entrega final o competencia donde un subsistema falló a pocas horas de la demostración. ¿Cómo priorizaste las reparaciones y qué resultado lograron?",
      "Cuéntame de algún proyecto donde conectaste sensores físicos a un dashboard de monitoreo en tiempo real. ¿Qué arquitectura de adquisición y transmisión utilizaste?",
      "Describe cómo has documentado diagramas eléctricos, neumáticos y código para facilitar el mantenimiento posterior de un sistema automatizado.",
      "Cuéntame sobre un proyecto donde calculaste o programaste la cinemática directa o inversa de un brazo robótico o robot móvil para evitar colisiones.",
      "Describe una ocasión en la que las lecturas de un sensor analógico tenían ruido que afectaba el control. ¿Qué filtro analógico o digital implementaste?",
      "Platícame de la puesta en marcha (commissioning) de un prototipo donde los subsistemas funcionaban por separado pero fallaron al integrarse.",
      "Háblame de cómo calculaste el torque, velocidad e inercia necesarios para dimensionar y seleccionar un motor y su transmisión mecánica.",
      "Describe un circuito electroneumático o hidráulico que hayas diseñado y cómo resolviste caídas de presión o sincronización de válvulas.",
      "Cuéntame de algún momento en que un driver o componente de potencia se dañó en pruebas y qué protección agregaste al rediseñar.",
      "Platícame de una interfaz HMI o SCADA que hayas diseñado para operar un sistema automatizado con alarmas claras y modos manual/automático."
    ]
  },
  {
    code: "LAF",
    name: "Finanzas, Economía y Consultoría de Negocios",
    roles: ["Financial Analyst Jr", "Business Consultant Intern", "Corporate Finance Associate"],
    lexicon: [
      "dcf", "flujo de caja", "flujo de efectivo", "wacc", "tasa de descuento", "vpn", "van",
      "tir", "retorno", "ebitda", "margen", "utilidad", "rentabilidad", "presupuesto", "variacion",
      "opex", "capex", "costo", "gasto", "liquidez", "solvencia", "apalancamiento", "deuda",
      "riesgo", "var", "beta", "portafolio", "cartera", "credito", "mece", "consultoria",
      "capital de trabajo", "cuentas por cobrar", "cuentas por pagar", "punto de equilibrio",
      "precio", "pricing", "elasticidad", "multiplos", "valuacion", "cobertura", "hedging",
      "tipo de cambio", "inflacion", "tasa de interes", "estado financiero", "balance", "roi"
    ],
    resources: [
      { title: "Valuación Financiera y Presentación de Impacto en EBITDA", provider: "Corporate Finance Institute", url: "https://corporatefinanceinstitute.com/resources/valuation/" }
    ],
    questions: [
      "Cuéntame sobre un modelo financiero o valuación por flujos descontados (DCF) que hayas construido. ¿Cómo fundamentaste los supuestos de crecimiento y WACC, y a qué conclusión llegaste?",
      "Describe una ocasión en la que detectaste una desviación importante entre el presupuesto planeado y los costos reales. ¿Cómo desglosaste las causas y qué ajustes propusiste?",
      "Platícame de alguna vez en que presentaste una recomendación financiera ante un comité o jurado que cuestionó tus números. ¿Cómo defendiste tu metodología con escenarios de sensibilidad?",
      "Háblame de un análisis donde evaluaste el riesgo de liquidez, solvencia o volatilidad de un portafolio. ¿Qué métricas de riesgo calculaste y qué estrategia de mitigación diseñaste?",
      "Describe un caso de consultoría donde el problema del cliente era ambiguo. ¿Cómo estructuraste el árbol de problemas (MECE) y qué impacto proyectó tu solución?",
      "Cuéntame de una situación en la que encontraste un error en una hoja de cálculo o reporte que alteraba los resultados. ¿Cómo actuaste para corregirlo y validarlo?",
      "Platícame de un análisis enfocado en mejorar el flujo de efectivo operativo mediante el ciclo de conversión de efectivo. ¿Qué políticas recomendaste y qué impacto tuvieron?",
      "Háblame de un proyecto en el que analizaste costos fijos, costos variables y punto de equilibrio. ¿Qué estrategia de precios propusiste y cuánto mejoró el margen?",
      "Describe una entrega financiera bajo una fecha límite muy estricta y con fuentes incompletas. ¿Cómo organizaste la validación cruzada de datos para entregar sin errores?",
      "Cuéntame sobre una plantilla financiera compleja que era propensa a errores manuales. ¿Cómo la rediseñaste o automatizaste y cuánto tiempo de análisis ahorraste?",
      "Relata un proyecto donde incorporaste variables macroeconómicas (inflación, tasas o tipo de cambio) en la planeación financiera. ¿Qué escenarios de estrés construiste?",
      "Platícame de una negociación donde el área comercial buscaba crecer rápido pero finanzas debía cuidar el margen. ¿Cómo encontraste un punto medio sustentado en números?",
      "Describe una experiencia realizando una valuación por múltiplos comparables. ¿Cómo seleccionaste la muestra de empresas comparables y a qué rango de valor llegaste?",
      "Háblame de un diagnóstico de gastos operativos (OPEX) donde identificaste ineficiencias. ¿Qué partidas priorizaste optimizar y qué porcentaje de ahorro proyectaste?",
      "Cuéntame de algún proyecto en el que tuviste que analizar financieramente una industria que desconocías. ¿Cómo identificaste sus motores de valor en pocos días?",
      "Cuéntame sobre un proyecto donde evaluaste la viabilidad de una inversión de capital (CAPEX) modelando flujos incrementales, VPN y TIR.",
      "Describe un análisis en el que evaluaste el nivel de apalancamiento y cobertura de intereses de una empresa para optimizar su costo de capital.",
      "Platícame de una ocasión en la que ayudaste a un equipo operativo no financiero a entender cómo sus decisiones impactaban el flujo de caja.",
      "Háblame de un caso donde analizaste la exposición cambiaria o de tasas de interés y evaluaste estrategias de cobertura (hedging).",
      "Describe una situación en la que dos fuentes contables o reportes de ventas presentaban discrepancias y cómo estandarizaste su conciliación.",
      "Cuéntame de algún proyecto donde manejaste información financiera confidencial y qué controles aplicaste para proteger su integridad.",
      "Platícame de un análisis de rentabilidad por producto o cliente (Unit Economics) donde descubriste qué segmentos aportaban o destruían margen neto."
    ]
  },
  {
    code: "LMC",
    name: "Marketing Digital, Producto y Desarrollo de Negocios",
    roles: ["Associate Product Manager", "Growth Marketing Analyst", "Business Development Rep"],
    lexicon: [
      "embudo", "funnel", "conversion", "cac", "ltv", "roas", "roi", "ctr", "cpc", "retencion",
      "churn", "abandono", "cohorte", "a/b", "experimento", "hipotesis", "roadmap", "priorizacion",
      "rice", "moscow", "producto", "mvp", "usuario", "cliente", "entrevista", "encuesta",
      "insight", "icp", "segmentacion", "target", "go-to-market", "lanzamiento", "campaña",
      "seo", "sem", "organico", "pauta", "contenido", "crm", "email", "onboarding", "activacion",
      "nps", "csat", "posicionamiento", "benchmarking", "competencia", "b2b", "leads", "ventas",
      "arpu", "monetizacion", "suscripcion", "landing"
    ],
    resources: [
      { title: "Métricas de Producto y Growth (CAC, LTV, Conversión)", provider: "Product School", url: "https://productschool.com/blog/product-fundamentals" }
    ],
    questions: [
      "Cuéntame sobre un proyecto o campaña donde detectaste una alta tasa de abandono en el embudo (funnel) de conversión. ¿Qué experimento implementaste y en qué porcentaje subió la conversión?",
      "Describe una situación en la que tenías múltiples solicitudes de funcionalidades para un producto pero tiempo limitado. ¿Qué matriz de priorización (RICE, MoSCoW) aplicaste y cuál fue el resultado?",
      "Platícame de un proyecto donde las suposiciones iniciales sobre el cliente cambiaron tras entrevistar a usuarios reales. ¿Qué insight descubriste y cómo ajustaste la propuesta de valor?",
      "Háblame de una campaña digital donde el costo de adquisición (CAC) era alto. ¿Cómo redistribuiste la segmentación o los creativos y qué mejora lograste en ROAS o CTR?",
      "Describe una ocasión en la que colaboraste con ingeniería y diseño para llevar una idea hasta un prototipo funcional. ¿Cómo definiste los criterios de aceptación?",
      "Cuéntame sobre el plan Go-To-Market de un producto o iniciativa. ¿Cómo definiste el perfil de cliente ideal (ICP) y qué tracción o registros conseguiste?",
      "Relata un caso en el que los usuarios probaban un servicio una vez pero no regresaban. ¿Cómo identificaste la causa de abandono y qué implementaste para elevar la retención?",
      "Platícame de alguna vez en que una propuesta o campaña recibió críticas fuertes de los usuarios. ¿Cómo procesaste el feedback y qué cambios rápidos ejecutaste?",
      "Describe un experimento A/B que hayas diseñado para validar un mensaje o interfaz. ¿Qué métrica principal definiste y qué mejora porcentual obtuvo la versión ganadora?",
      "Háblame de una experiencia buscando alianzas estratégicas, patrocinios o clientes B2B. ¿Cómo estructuraste tu prospección y qué tasa de cierre lograste?",
      "Cuéntame de una ocasión en la que convenciste a tu equipo de detener una iniciativa de bajo impacto para reenfocar recursos en otra con mayor retorno.",
      "Describe un análisis de competencia en un mercado saturado. ¿Qué diferenciador identificaste y cómo posicionaste tu oferta para destacar?",
      "Platícame de un proyecto donde debías generar tráfico o comunidad sin presupuesto publicitario. ¿Qué estrategia orgánica ejecutaste y qué crecimiento porcentual lograste?",
      "Háblame de un lanzamiento o activación que hayas coordinado con múltiples proveedores. ¿Qué imprevisto resolviste y qué nivel de satisfacción o asistencia obtuvieron?",
      "Describe un proyecto en el que diseñaste o ajustaste el modelo de monetización de una solución. ¿Cómo calculaste la relación LTV/CAC?",
      "Cuéntame sobre una mejora que hayas propuesto en el flujo de onboarding de un producto para que el usuario percibiera valor en menos tiempo.",
      "Describe una campaña de CRM o email segmentada por comportamiento del usuario. ¿Qué tasa de apertura y conversión lograste frente a envíos genéricos?",
      "Platícame de una negociación donde cerraste un acuerdo con un patrocinador o aliado comercial utilizando métricas de audiencia y retorno.",
      "Háblame de cómo utilizaste un análisis de cohortes para detectar en qué semana caía la retención de usuarios y qué acción correctiva implementaste.",
      "Describe una ocasión en la que rediseñaste la jerarquía de mensajes de una landing page o presentación comercial para elevar el registro de prospectos.",
      "Cuéntame de un proyecto donde alineaste criterios de calificación de prospectos (MQL/SQL) entre marketing y ventas para subir el cierre comercial.",
      "Platícame de un estudio de sensibilidad de precios o diseño de paquetes (bundling) que hayas realizado para incrementar el ticket promedio (ARPU)."
    ]
  },
  {
    code: "IBT",
    name: "Ingeniería Biomédica y Biotecnología",
    roles: ["Clinical Engineering Intern", "R&D Biotech Associate", "Quality & Regulatory Affairs Jr"],
    lexicon: [
      "protocolo", "ensayo", "experimento", "laboratorio", "control", "reproducibilidad",
      "desviacion", "variabilidad", "calibracion", "sensor", "senal", "ecg", "emg", "oximetria",
      "ruido", "filtrado", "iso 13485", "iso 14971", "iec 60601", "amef", "riesgo", "regulatorio",
      "cofepris", "fda", "norma", "anova", "t-student", "p-valor", "estadistica", "clinico",
      "paciente", "medico", "hospital", "bioproceso", "fermentacion", "cultivo", "biorreactor",
      "enzima", "ph", "temperatura", "mantenimiento", "bioetica", "anonimizacion", "biomaterial",
      "sensibilidad", "especificidad", "imagen medica", "pcr", "molecular", "cadena de frio"
    ],
    resources: [
      { title: "Validación de Dispositivos Médicos y Normativa Clínica", provider: "WHO Medical Devices", url: "https://www.who.int/health-topics/medical-devices" }
    ],
    questions: [
      "Cuéntame sobre un protocolo experimental o ensayo de laboratorio cuyos resultados tenían alta variabilidad inicial. ¿Cómo aislaste la fuente de error y lograste reproducibilidad estadística?",
      "Describe una experiencia diseñando o calibrando un instrumento biomédico o sensor fisiológico. ¿Cómo filtraste el ruido de la señal y contra qué referencia validaste su exactitud?",
      "Platícame de un proyecto donde alineaste un desarrollo médico o biotecnológico con normas regulatorias o de gestión de riesgos (ISO 13485 / ISO 14971). ¿Cómo estructuraste la matriz de riesgos?",
      "Háblame de un estudio donde analizaste datos experimentales o clínicos. ¿Qué pruebas estadísticas aplicaste y qué conclusión validada obtuviste?",
      "Describe una ocasión en la que colaboraste con personal médico o clínico para entender una necesidad. ¿Cómo tradujiste sus observaciones en especificaciones técnicas medibles?",
      "Cuéntame sobre algún bioproceso, fermentación o cultivo celular donde optimizaste parámetros fisicoquímicos. ¿En qué porcentaje incrementaste el rendimiento o viabilidad?",
      "Relata un caso relacionado con la gestión de equipo médico o de laboratorio para reducir tiempos de inactividad. ¿Qué plan de mantenimiento preventivo propusiste?",
      "Platícame de una situación en la que manejaste información sensible de salud o muestras biológicas. ¿Qué protocolos de anonimización y bioseguridad aplicaste?",
      "Describe un proyecto de innovación en salud donde redujiste el costo unitario de un prototipo sustituyendo materiales o componentes sin comprometer la seguridad.",
      "Háblame de algún algoritmo o script que hayas desarrollado para procesar señales fisiológicas o imágenes médicas. ¿Qué sensibilidad o especificidad alcanzaste?",
      "Cuéntame de una investigación donde tras varias semanas los resultados experimentales fueron negativos. ¿Cómo replanteaste la metodología a tiempo y qué entregable lograste?",
      "Describe una situación en la que protegiste la cadena de frío o estabilidad de muestras termosensibles ante una contingencia logística o de equipo.",
      "Platícame de un proyecto donde caracterizaste las propiedades mecánicas, químicas o de biocompatibilidad de un biomaterial o formulación.",
      "Háblame de una mejora que hayas implementado en el orden, etiquetado o manejo de residuos biológicos/químicos (RPBI) en laboratorio para reducir riesgos.",
      "Describe cómo estructuraste la revisión sistemática de literatura científica y patentes para definir la ventaja técnica de un proyecto biomédico o biotecnológico.",
      "Cuéntame sobre un ensayo de biología molecular o analítico (como PCR, electroforesis o espectrofotometría) donde optimizaste variables para obtener señales claras.",
      "Describe una experiencia verificando seguridad eléctrica, aislamiento o corrientes de fuga en instrumentación biomédica conforme a estándares clínicos.",
      "Platícame de un proyecto interdisciplinario de salud donde integraste requerimientos de médicos, químicos o programadores en un solo prototipo funcional.",
      "Háblame de un proyecto donde modelaste matemáticamente la cinética enzimática, liberación de un compuesto o dinámica de un sistema fisiológico.",
      "Describe cómo analizarías y documentarías un incidente de tecnovigilancia de un dispositivo médico aplicando acciones correctivas y preventivas (CAPA).",
      "Cuéntame de una ocasión en la que un reactivo o equipo especializado tardaba en llegar y adaptaste el protocolo experimental manteniendo la validez científica.",
      "Platícame de algún desarrollo biomecánico, órtesis o dispositivo de rehabilitación donde evaluaste la ergonomía y distribución de cargas para el paciente."
    ]
  },
  {
    code: "ARQ",
    name: "Arquitectura, Diseño Industrial y UX",
    roles: ["UX/UI Product Designer", "Architectural Project Jr", "Industrial Design Intern"],
    lexicon: [
      "usabilidad", "usuario", "ux", "ui", "interfaz", "prototipo", "wireframe", "maqueta",
      "iteracion", "prueba", "presupuesto", "costo", "material", "constructivo", "manufactura",
      "bim", "revit", "autocad", "rhino", "sketchup", "figma", "sistema de diseño", "componente",
      "libreria", "bioclimatico", "ventilacion", "asoleamiento", "iluminacion", "termico",
      "sustentable", "energia", "estructural", "instalaciones", "mep", "cruce", "accesibilidad",
      "ergonomia", "antropometria", "normativa", "plano", "ejecutivo", "detalle", "especificacion",
      "espacio", "circulacion", "zonificacion", "flujo", "jerarquia", "taller", "obra"
    ],
    resources: [
      { title: "Presentación de Proyectos UX y Diseño con Métricas de Usabilidad", provider: "Nielsen Norman Group", url: "https://www.nngroup.com/articles/ux-research-cheat-sheet/" }
    ],
    questions: [
      "Cuéntame sobre un proyecto de diseño (arquitectónico, industrial o UX) donde las pruebas con usuarios revelaron fricciones no previstas. ¿Qué iteraciones realizaste y cómo mejoró el resultado?",
      "Describe una ocasión en la que tu propuesta de diseño superaba el presupuesto o tenía restricciones constructivas. ¿Cómo aplicaste ingeniería de valor para reducir costos manteniendo la calidad?",
      "Platícame de una entrega donde recibiste críticas fuertes sobre tu concepto. ¿Cómo separaste las opiniones subjetivas de los requerimientos funcionales para evolucionar el proyecto?",
      "Háblame de un proyecto en equipo donde estandarizaste un modelo BIM, librería de bloques o sistema de diseño UI. ¿Cuánto tiempo de retrabajo ahorraron?",
      "Describe un proyecto en el que integraste criterios de diseño bioclimático, eficiencia energética o sustentabilidad de materiales. ¿Qué mejora cuantificable lograste?",
      "Cuéntame de una situación en la que negociaste una solución entre diseño e ingeniería (estructural, manufactura o desarrollo de software) sin sacrificar la experiencia del usuario.",
      "Platícame de un proyecto donde aplicaste normativas de accesibilidad universal o ergonomía. ¿Cómo verificaste que el espacio, producto o interfaz fuera inclusivo?",
      "Háblame de una vez en que construiste maquetas, prototipos físicos o wireframes rápidos para validar una decisión crítica en pocos días.",
      "Describe un proyecto donde el alcance o programa cambió a pocos días de la entrega. ¿Cómo reorganizaste la producción de planos, renders o prototipos para llegar a tiempo?",
      "Cuéntame sobre la elaboración de un paquete de planos ejecutivos, especificaciones de manufactura o handoff de desarrollo. ¿Cómo aseguraste que no hubiera errores de interpretación?",
      "Relata un proyecto donde resolviste un programa complejo dentro de un espacio o pantalla muy reducida. ¿Cómo optimizaste los flujos de circulación o jerarquía visual?",
      "Platícame de alguna experiencia supervisando la fabricación de un prototipo, mobiliario o elemento constructivo con un taller externo para corregir un detalle de calidad a tiempo.",
      "Describe cómo el análisis de sitio, contexto urbano o investigación de usuarios determinó el concepto rector de uno de tus proyectos más importantes.",
      "Háblame de una entrega donde optimizaste los tiempos de modelado, renderizado o postproducción del equipo para cumplir una fecha límite crítica.",
      "Cuéntame de un diseño que inicialmente estaba saturado de elementos. ¿Qué criterio seguiste para depurarlo y cómo mejoró su claridad y función?",
      "Cuéntame sobre un proyecto donde reorganizaste la arquitectura de información o señalética espacial porque los usuarios tardaban en encontrar lo que buscaban.",
      "Describe una ocasión en la que detectaste colisiones (clashes) entre estructura, ductos de instalaciones (MEP) y diseño, y cómo lo resolviste en el modelo.",
      "Platícame de una vez en que utilizaste vistas axonométricas, maquetas o prototipos interactivos para que un cliente no especializado comprendiera el proyecto.",
      "Háblame de cómo especificaste materiales y acabados para un proyecto de uso intensivo equilibrando estética, mantenimiento y costo de ciclo de vida.",
      "Describe un proyecto donde utilizaste modulación geométrica o prefabricación para reducir la merma de material y acelerar el montaje.",
      "Cuéntame de un taller intensivo o Design Sprint donde en pocas horas convergieron en equipo desde el problema hasta un prototipo validado.",
      "Platícame de un proyecto donde diseñaste la estrategia de iluminación natural/artificial o contraste visual para mejorar el confort y la jerarquía."
    ]
  }
];

const STOPWORDS_ES = new Set([
  "sobre", "como", "para", "este", "esta", "estos", "estas", "donde", "cuando",
  "cual", "cuales", "quien", "porque", "algun", "alguna", "proyecto", "ocasion",
  "situacion", "cuentame", "describe", "platicame", "hablame", "recuerda", "relata",
  "comparte", "tuviste", "hiciste", "lograste", "obtuviste", "equipo", "trabajo",
  "entre", "desde", "hasta", "ante", "bajo", "tras", "durante", "mediante", "pero",
  "mas", "menos", "muy", "todo", "toda", "todos", "todas", "otro", "otra"
]);

// Dominios falsos, temporales o de prueba bloqueados por el validador de correos
const BLOCKED_FAKE_EMAIL_DOMAINS = new Set([
  "ejemplo.com", "example.com", "test.com", "prueba.com", "correo.com",
  "dominio.com", "usuario.com", "mailinator.com", "tempmail.com",
  "10minutemail.com", "guerrillamail.com", "yopmail.com", "trashmail.com",
  "sharklasers.com", "fakeinbox.com", "getnada.com", "maildrop.cc",
  "dispostable.com", "fake.com", "asdf.com", "qwerty.com", "none.com",
  "xyz.com", "abc.com", "hola.com", "email.com", "nada.com", "patito.com",
  "gnial.com", "gmal.com", "gmial.com", "gamil.com", "gmai.com", "gmail.co",
  "hotmial.com", "hotmal.com", "outlok.com", "outllok.com", "yaho.com"
]);

// Proveedores de correo oficiales e institucionales verificados
const VERIFIED_EMAIL_DOMAINS = new Set([
  "gmail.com", "googlemail.com",
  "outlook.com", "outlook.es", "outlook.com.mx",
  "hotmail.com", "hotmail.es", "hotmail.com.mx",
  "live.com", "live.com.mx", "msn.com",
  "icloud.com", "me.com", "mac.com",
  "yahoo.com", "yahoo.com.mx", "yahoo.es", "ymail.com",
  "proton.me", "protonmail.com", "zoho.com", "fastmail.com", "gmx.com", "aol.com",
  "tec.mx", "itesm.mx", "exatec.tec.mx",
  "unam.mx", "comunidad.unam.mx", "ipn.mx", "alumno.ipn.mx", "uam.mx",
  "ibero.mx", "iberopuebla.mx", "anahuac.mx", "udem.edu.mx", "up.edu.mx",
  "udg.mx", "uanl.mx", "uaq.mx", "buap.mx", "uv.mx", "uaslp.mx", "ugto.mx",
  "javeriana.edu.co", "uniandes.edu.co", "unal.edu.co", "udea.edu.co"
]);

// Solo se buscan errores de dedo contra proveedores largos y muy usados
const CANONICAL_PROVIDERS = ["gmail.com", "hotmail.com", "outlook.com", "yahoo.com", "icloud.com"];

function computeEditDistance(a, b) {
  const m = a.length;
  const n = b.length;
  const dp = Array.from({ length: m + 1 }, () => Array(n + 1).fill(0));
  for (let i = 0; i <= m; i++) dp[i][0] = i;
  for (let j = 0; j <= n; j++) dp[0][j] = j;
  for (let i = 1; i <= m; i++) {
    for (let j = 1; j <= n; j++) {
      const cost = a[i - 1] === b[j - 1] ? 0 : 1;
      dp[i][j] = Math.min(dp[i - 1][j] + 1, dp[i][j - 1] + 1, dp[i - 1][j - 1] + cost);
      if (i > 1 && j > 1 && a[i - 1] === b[j - 2] && a[i - 2] === b[j - 1]) {
        dp[i][j] = Math.min(dp[i][j], dp[i - 2][j - 2] + 1);
      }
    }
  }
  return dp[m][n];
}

const appState = {
  user: null,
  registeredUsers: [],
  historiesByUser: {}, // Diccionario aislado por email: { "correo@dominio.com": [ ...sesiones ] }
  sessionId: null,
  careerCode: "ITC",
  targetRole: "",
  seniority: "Junior / Intern",
  vacancyContext: "",
  cvSummary: "",
  totalQuestions: 17,
  questionsPool: [],
  currentIndex: 0,
  turns: [],
  turnStartTime: Date.now(),
  googleClientId: PUBLIC_CONFIG.GOOGLE_CLIENT_ID,
  backendOnline: false,
  serverSession: false,
  sending: false,          // evita enviar la misma respuesta dos veces (Enter repetido)
  reportInProgress: false, // evita generar y guardar el mismo reporte dos veces
  reportData: null         // lo que muestra la vista de reporte y lo que va al PDF
};

function loadSavedState() {
  try {
    const savedUsers = localStorage.getItem("interviewai_users_v3");
    if (savedUsers) {
      const parsed = JSON.parse(savedUsers);
      if (Array.isArray(parsed)) {
        appState.registeredUsers = parsed;
      }
    }
    const savedHistories = localStorage.getItem("interviewai_histories_by_user_v3");
    if (savedHistories) {
      const parsedH = JSON.parse(savedHistories);
      if (parsedH && typeof parsedH === "object") {
        appState.historiesByUser = parsedH;
        dedupeLocalHistories();
      }
    }
  } catch (_) {}
}

// v0.3.0 guardaba contraseñas en texto plano: se convierten a hash y se borra el texto plano.
async function migrateLegacyDemoUsers() {
  let changed = false;
  for (const u of appState.registeredUsers) {
    if (typeof u.password === "string") {
      try { u.password_hash = await hashDemoPassword(u.password); } catch (_) {}
      delete u.password;
      changed = true;
    }
  }
  if (changed) saveRegisteredUsers();
}

function saveRegisteredUsers() {
  try {
    localStorage.setItem("interviewai_users_v3", JSON.stringify(appState.registeredUsers));
  } catch (_) {}
}

// Versiones anteriores guardaban la misma entrevista varias veces: se eliminan las repetidas.
function dedupeLocalHistories() {
  Object.keys(appState.historiesByUser).forEach((key) => {
    const list = appState.historiesByUser[key];
    if (!Array.isArray(list)) return;
    const seen = new Set();
    appState.historiesByUser[key] = list.filter((h) => {
      const id = h.id || [h.date, h.careerCode, h.targetRole, h.overallScore].join("|");
      if (seen.has(id)) return false;
      seen.add(id);
      return true;
    });
  });
  saveHistoriesByUser();
}

function saveHistoriesByUser() {
  try {
    localStorage.setItem("interviewai_histories_by_user_v3", JSON.stringify(appState.historiesByUser));
  } catch (_) {}
}

function getCurrentUserHistoryList() {
  if (!appState.user || !appState.user.email) return [];
  const key = appState.user.email.toLowerCase();
  if (!Array.isArray(appState.historiesByUser[key])) {
    appState.historiesByUser[key] = [];
  }
  return appState.historiesByUser[key];
}

// =============================================================================
// VALIDADOR DE CORREOS REALES (Sintaxis RFC 5322 + Bloqueo de Dominios Falsos
// + Verificación en vivo de Registros MX en servidores DNS de Google)
// =============================================================================
async function validateRealEmailAccount(email) {
  const clean = (email || "").trim().toLowerCase();
  const rfcRegex = /^[A-Za-z0-9](?:[A-Za-z0-9._%+-]{0,62}[A-Za-z0-9])?@[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?(?:\.[A-Za-z]{2,})+$/;

  if (!rfcRegex.test(clean) || clean.includes("..")) {
    return { valid: false, reason: "El formato del correo electrónico es inválido (debe incluir @ y un dominio válido como .com o .mx)." };
  }

  const [localPart, domain] = clean.split("@");
  if (localPart.length < 2) {
    return { valid: false, reason: "El nombre de usuario antes de '@' es demasiado corto." };
  }

  if (/^(\d+|test|prueba|asdf|qwerty|admin|user|usuario|correo|ejemplo|fake)$/.test(localPart)) {
    return { valid: false, reason: `El usuario '${localPart}@...' no es válido. Ingresa tu correo personal o institucional.` };
  }

  if (BLOCKED_FAKE_EMAIL_DOMAINS.has(domain)) {
    return { valid: false, reason: `El dominio '@${domain}' no es un proveedor de correo válido.` };
  }

  // 1. Aceptar proveedores verificados o dominios académicos oficiales (.edu, .edu.mx, .edu.co, .ac.uk, .gob.mx)
  const isOfficialAcademic = /\.(edu|edu\.[a-z]{2}|ac\.[a-z]{2}|gob\.[a-z]{2})$/.test(domain);
  if (VERIFIED_EMAIL_DOMAINS.has(domain) || isOfficialAcademic) {
    return { valid: true, email: clean };
  }

  // 2. Detectar errores de dedo como @gnial.com, @gmal.com, @hotmial.com, @outlok.com
  for (const canonical of CANONICAL_PROVIDERS) {
    const dist = computeEditDistance(domain, canonical);
    if (dist > 0 && dist <= 2) {
      return {
        valid: false,
        reason: `El dominio '@${domain}' parece mal escrito (¿quisiste escribir '@${canonical}'?).`
      };
    }
  }

  // Con backend activo, el servidor hace la verificación de registros MX.
  if (appState.backendOnline) {
    return { valid: true, email: clean };
  }

  // 3. Para dominios corporativos personalizados, exigir verificación real de servidores de correo empresariales (MX)
  try {
    const dnsResp = await fetch(`https://dns.google/resolve?name=${encodeURIComponent(domain)}&type=MX`);
    if (dnsResp.ok) {
      const dnsData = await dnsResp.json();
      const answers = Array.isArray(dnsData.Answer) ? dnsData.Answer : [];
      const validMx = answers.some((ans) => {
        const data = String(ans.data || "").toLowerCase().trim();
        // Rechazar Null MX ("0 .") y servicios de parking de dominios
        if (!data || data === "0 ." || data.endsWith(" .") || data.includes("sedoparking") || data.includes("bodis") || data.includes("parking")) {
          return false;
        }
        return (
          data.includes("google.com") ||
          data.includes("googlemail.com") ||
          data.includes("outlook.com") ||
          data.includes("pphosted.com") ||
          data.includes("mimecast.com") ||
          data.includes("zoho.com") ||
          data.includes("protonmail.ch") ||
          data.includes("yahoodns.net") ||
          data.includes("icloud.com") ||
          data.includes("amazonses.com")
        );
      });
      if (dnsData.Status === 0 && validMx) {
        return { valid: true, email: clean };
      }
    }
  } catch (_) {}

  return {
    valid: false,
    reason: `El dominio '@${domain}' no pudo ser verificado como un proveedor de correo válido. Usa un correo real (@gmail.com, @outlook.com, @hotmail.com, @icloud.com o institucional @tec.mx / .edu).`
  };
}

function anonymizeText(text) {
  if (!text) return "";
  return text
    .replace(/\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b/g, "[EMAIL_PROTEGIDO]")
    .replace(/(?:\+?\d{1,3}[\s.-]?)?(?:\(?\d{2,3}\)?[\s.-]?)?\d{3,4}[\s.-]?\d{4}\b/g, "[TEL_PROTEGIDO]")
    .replace(/\bA0\d{7}\b/gi, "[MATRICULA_PROTEGIDA]");
}

function extractMetrics(text) {
  if (!text) return [];
  const regex = /\b\d+(?:[.,]\d+)?\s*(?:%|por\s*ciento|ms|milisegundos|segundos|s|minutos|min|horas|h|días|semanas|meses|x|veces|usuarios|clientes|solicitudes|req\/s|mb|gb|tb|usd|mxn|\$|pesos|dólares|puntos|ppm|oee|cpk|f1|auc)\b|\$\s*\d+(?:[.,]\d+)?|\b(?:reduj\w+|increment\w+|aument\w+|mejor\w+|ahorr\w+|baj\w+|sub\w+|optimiz\w+|disminuy\w+|pas\w+\s+de)\s+(?:en\s+)?(?:un\s+)?\d+(?:[.,]\d+)?\s*%?/gi;
  return text.match(regex) || [];
}

function normalizeStr(str) {
  return (str || "")
    .toLowerCase()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "");
}

function extractKeywords(text) {
  const norm = normalizeStr(text);
  const words = norm.match(/[a-z0-9]{4,}/g) || [];
  return Array.from(new Set(words.filter((w) => !STOPWORDS_ES.has(w))));
}

// =============================================================================
// GENERADOR DE PREGUNTAS ADAPTADAS AL CONTEXTO DE LA VACANTE Y CV DEL USUARIO
// =============================================================================
function buildVacancyTailoredQuestions(careerObj, targetRole, cvText, vacancyContext, totalCount) {
  const contextTokens = extractKeywords(`${targetRole} ${vacancyContext} ${cvText}`);

  // Calificar cada pregunta del banco según su afinidad con el contexto de la vacante + factor aleatorio
  const scoredQuestions = careerObj.questions.map((qText) => {
    const qTokens = extractKeywords(qText);
    let overlap = 0;
    contextTokens.forEach((ct) => {
      if (qTokens.some((qt) => qt.includes(ct.slice(0, 4)) || ct.includes(qt.slice(0, 4)))) {
        overlap += 1;
      }
    });
    return {
      qText,
      score: overlap * 2.0 + Math.random() * 1.5
    };
  });

  scoredQuestions.sort((a, b) => b.score - a.score);
  const selectedRaw = scoredQuestions.slice(0, totalCount).map((item) => item.qText);

  // Transiciones naturales y neutras (sin elogiar ni juzgar la respuesta anterior)
  const acks = ["Gracias.", "Entiendo, gracias.", "Gracias por contarme.", "De acuerdo.",
    "Muy bien, sigamos.", "Ok, pasemos a otro tema.", "Gracias por el detalle.", "Va, cambiemos de tema."];
  let lastAck = "";
  return selectedRaw.map((baseQ, idx) => {
    if (idx === 0) return `Hola, gracias por tu tiempo. Empecemos. ${baseQ}`;
    const options = acks.filter((a) => a !== lastAck);
    lastAck = options[Math.floor(Math.random() * options.length)];
    if (idx === selectedRaw.length - 1) return `${lastAck} Vamos con la última pregunta. ${baseQ}`;
    return `${lastAck} ${baseQ}`;
  });
}

// =============================================================================
// EVALUADOR CRÍTICO STAR (ESCALA 0 A 5 — CERO COMPLACENCIA, ESPECTRO AMPLIO)
// =============================================================================
function evaluateResponseCritical(questionText, responseText, careerCode, role) {
  const clean = (responseText || "").trim();
  const norm = normalizeStr(clean);
  const words = norm.match(/[a-z0-9]+/g) || [];
  const wordCount = words.length;
  const uniqueWords = new Set(words).size;
  const lexicalDiversity = uniqueWords / Math.max(1, wordCount);
  const metrics = extractMetrics(clean);
  const careerObj = CAREER_CATALOG.find((c) => c.code === careerCode) || CAREER_CATALOG[0];

  // 1. FILTRO ESTRICTO DE TONTERÍAS / EVASIVAS / SIN SENTIDO -> CALIFICACIÓN 0/5
  const nonsenseRegex = /^(no\s*se|ningun[oa]?|nada|paso|hola|test|prueba|asdf\w*|qwerty\w*|ok|bien|si|no|x+|jaja\w*|lol|wtf|cualquier\s*cosa|sin\s*comentarios|todo\s*bien|nose)$/;
  if (
    wordCount < 6 ||
    uniqueWords < 5 ||
    nonsenseRegex.test(norm) ||
    (wordCount >= 10 && lexicalDiversity < 0.30)
  ) {
    return {
      star_situation: 0,
      star_task: 0,
      star_action: 0,
      star_result: 0,
      technical_clarity: 0,
      relevance: 0,
      turn_average_score: 0.0,
      metrics_detected: [],
      tech_terms_detected: [],
      strengths: "Ninguna fortaleza identificada (0/5). La respuesta entregada carece de contenido profesional, es evasiva o no tiene sentido.",
      improvement_areas: "Retroalimentación: Una respuesta vacía o incoherente recibe 0/5 porque no demuestra ninguna competencia. Debes describir un caso real detallando el problema inicial (Situación), tu responsabilidad concreta (Tarea), las acciones técnicas que ejecutaste (Acción) y el resultado medible (Resultado).",
      improved_example_star: buildQuestionSpecificStarExample(questionText, careerCode, role)
    };
  }

  // 2. PERTINENCIA CON LA PREGUNTA Y EL CONTEXTO DE LA VACANTE
  const qKeywords = extractKeywords(`${questionText} ${appState.vacancyContext}`);
  const matchedKeywords = qKeywords.filter((kw) => norm.includes(kw.slice(0, 4)));
  const overlapRatio = matchedKeywords.length / Math.max(1, Math.min(10, qKeywords.length));

  // 3. EVIDENCIA TÉCNICA (Léxico de la carrera + términos del contexto de la vacante y CV)
  const vacancyTechWords = extractKeywords(`${appState.vacancyContext} ${appState.cvSummary}`).filter((w) => w.length >= 5);
  const combinedLexicon = Array.from(new Set([...careerObj.lexicon, ...vacancyTechWords]));
  const matchedTech = combinedLexicon.filter((term) => norm.includes(normalizeStr(term)));

  // 4. RAÍCES SEMÁNTICAS AMPLIAS PARA RECONOCER BUENAS RESPUESTAS NATURALES
  const sitStems = [
    "proyect", "durante", "cuando", "trabaj", "materia", "practic", "laboratori",
    "ocasion", "context", "ocurri", "enfrent", "exist", "teniam", "situacion",
    "anterior", "semestr", "empres", "client", "equi", "area", "sistem", "proces",
    "plataform", "aplicacion", "servicio", "etapa", "inicio", "detect", "identific"
  ];
  const taskStems = [
    "objetiv", "tare", "responsab", "debi", "teni", "encarg", "reto", "meta",
    "requer", "necesit", "rol", "cumpl", "proposit", "asign", "resolv", "problem",
    "urgenc", "prioridad", "solicitud", "alcanc", "compromis", "garantiz", "asegur",
    "reducir", "mejorar", "optimizar", "evitar", "lograr"
  ];
  const actionStems = [
    "implement", "disen", "program", "desarroll", "analic", "analiz", "constru",
    "optimic", "optimiz", "configur", "propus", "realic", "realiz", "ejecut",
    "apliqu", "automat", "estructur", "revis", "calibr", "model", "negoci",
    "coordin", "investig", "migr", "valid", "estandar", "document", "medi",
    "calcul", "entren", "limpi", "reorganic", "utilic", "utiliz", "cree", "crea",
    "levant", "diagnostic", "correg", "modific", "integr", "despleg", "prob",
    "reemplac", "sustitu", "divid", "prioric", "lider", "establec", "defini"
    ];
  // Verbos en primera persona: solo suman si hay varios (una secuencia de pasos).
  const firstPersonSteps = ["pedi", "explique", "escribi", "agregue", "instale", "cambie", "ensene", "mostre", "compare", "busque", "organice", "priorice", "hice", "resolvi", "hable con", "decidi", "prepare", "separe", "actualice", "comprobe", "reproduje", "aisle"];
  const resultStems = [
    "resultad", "logr", "reduj", "reduci", "increment", "aument", "mejor",
    "ahorr", "permit", "final", "consegu", "impact", "paso de", "bajo a",
    "subio a", "cumplim", "obtuv", "disminuy", "elimina", "estabiliz",
    "entreg", "aprob", "satisfaccion", "exito", "gracias a", "con esto"
  ];

  const sitHits = sitStems.filter((s) => norm.includes(s)).length;
  const taskHits = taskStems.filter((s) => norm.includes(s)).length;
  const steps = firstPersonSteps.filter((s) => norm.includes(s)).length;
  const actHits = actionStems.filter((s) => norm.includes(s)).length + Math.max(0, steps - 1);
  const resHits = resultStems.filter((s) => norm.includes(s)).length;

  // Si el usuario escribió texto desconectado de la pregunta, sin acciones y sin términos técnicos -> 0/5
  if (overlapRatio === 0 && matchedTech.length === 0 && actHits === 0) {
    return {
      star_situation: sitHits > 0 ? 1 : 0,
      star_task: 0,
      star_action: 0,
      star_result: 0,
      technical_clarity: 0,
      relevance: 0,
      turn_average_score: Number(((sitHits > 0 ? 1 : 0) / 6).toFixed(2)),
      metrics_detected: [],
      tech_terms_detected: [],
      strengths: "No se identifican argumentos técnicos ni relación con la pregunta planteada.",
      improvement_areas: "Retroalimentación: Tu respuesta divaga y no demuestra la habilidad evaluada. Explica el problema concreto, tu objetivo, las acciones técnicas aplicadas y el impacto medible.",
      improved_example_star: buildQuestionSpecificStarExample(questionText, careerCode, role)
    };
  }

  // --- SITUACIÓN (0 a 5) ---
  let s = 0;
  if (sitHits === 0 && wordCount < 15) s = 0;
  else if (sitHits === 1 || wordCount < 22) s = sitHits >= 1 ? 2 : 1;
  else if (sitHits === 2 && wordCount >= 22) s = 3;
  else if (sitHits >= 3 && wordCount >= 30) s = 4;
  else s = 3;
  if (sitHits >= 4 && wordCount >= 42 && overlapRatio >= 0.25) s = 5;

  // --- TAREA (0 a 5) ---
  let t = 0;
  if (taskHits === 0) t = wordCount >= 30 ? 1 : 0;
  else if (taskHits === 1) t = wordCount >= 26 ? 3 : 2;
  else if (taskHits === 2) t = wordCount >= 34 ? 4 : 3;
  else t = wordCount >= 40 ? 5 : 4;

  // --- ACCIÓN (0 a 5) ---
  let a = 0;
  if (actHits === 0) a = 0;
  else if (actHits === 1) a = matchedTech.length >= 1 ? 3 : 2;
  else if (actHits === 2) a = matchedTech.length >= 1 ? 4 : 3;
  else a = matchedTech.length >= 2 && wordCount >= 38 ? 5 : 4;

  // --- RESULTADO (0 a 5) ---
  let r = 0;
  if (resHits === 0 && metrics.length === 0) r = 0;
  else if (resHits >= 1 && metrics.length === 0) r = wordCount >= 38 ? 3 : 2;
  else if (metrics.length === 1) r = resHits >= 1 ? 4 : 3;
  else r = resHits >= 1 ? 5 : 4;

  // --- CLARIDAD TÉCNICA (0 a 5) ---
  let tech = 0;
  if (matchedTech.length === 0 && actHits === 0) tech = 0;
  else if (matchedTech.length === 0) tech = wordCount >= 35 ? 2 : 1;
  else if (matchedTech.length === 1) tech = 3;
  else if (matchedTech.length === 2) tech = 4;
  else tech = actHits >= 2 && wordCount >= 38 ? 5 : 4;

  // --- PERTINENCIA (0 a 5) ---
  let rel = 0;
  if (overlapRatio === 0 && matchedTech.length === 0) rel = 0;
  else if (overlapRatio < 0.15) rel = matchedTech.length >= 1 ? 2 : 1;
  else if (overlapRatio < 0.30) rel = 3;
  else if (overlapRatio < 0.45) rel = 4;
  else rel = wordCount >= 34 ? 5 : 4;

  // Misma regla que backend/app/agents/question_focus.py: se pondera lo que la pregunta pide.
  const focus = questionFocus(questionText);
  if (!focus.full) {
    const core = [["star_task", t], ["star_action", a], ["star_result", r]].filter(([d]) => focus.asks.includes(d)).map(([, v]) => v);
    if (core.length) rel = Math.max(rel, Math.min(...core) - 1);
  }
  const avg = weightedAverage({ star_situation: s, star_task: t, star_action: a, star_result: r, technical_clarity: tech, relevance: rel }, focus);

  // Retroalimentación crítica, objetiva y concisa
  const goodParts = [];
  if (s >= 4) goodParts.push("contexto del problema bien planteado (Situación)");
  if (t >= 4) goodParts.push("objetivo o reto claramente delimitado (Tarea)");
  if (a >= 4) goodParts.push("ejecución técnica bien fundamentada (Acción)");
  if (r >= 4 && metrics.length > 0) goodParts.push(`impacto cuantificado (${metrics.slice(0, 3).join(", ")})`);
  if (tech >= 4 && matchedTech.length > 0) goodParts.push(`uso preciso de conceptos (${matchedTech.slice(0, 4).join(", ")})`);

  let strengths = "La respuesta carece de profundidad técnica suficiente en este turno.";
  if (goodParts.length > 0) {
    strengths = "Evidencia sólida: " + goodParts.join("; ") + ".";
  } else if (avg >= 2.5) {
    strengths = "Se comprende la idea general del caso, pero faltó rigor en la ejecución y medición del impacto.";
  }

  const critiques = [];
  const asks = (d) => focus.asks.includes(d);
  if (rel <= 2) critiques.push("no respondiste al núcleo específico de la pregunta ni al contexto de la vacante");
  if (s <= 2 && asks("star_situation")) critiques.push("falta ubicar el caso: en qué proyecto o situación fue (Situación)");
  if (t <= 2 && asks("star_task")) critiques.push("no queda claro cuál era tu papel o qué te tocaba resolver a ti (Tarea)");
  if (a <= 2 && asks("star_action")) critiques.push("hace falta decir qué hiciste tú, paso por paso, y con qué herramientas o decisiones (Acción)");
  if (asks("star_result")) {
    if (r === 0) critiques.push("la pregunta pide el resultado y no lo mencionaste (Resultado)");
    else if (r <= 3 && metrics.length === 0) critiques.push("el resultado se queda en algo general; respáldalo con un dato (tiempo, %, usuarios o entrega concreta)");
  }
  if (tech <= 2 && focus.technical) critiques.push(`faltan detalles técnicos concretos propios de ${careerCode}`);

  const improvements = critiques.length > 0
    ? `La pregunta pedía ${describeFocus(focus)}. Para mejorar: ` + critiques.join("; ") + "."
    : `Respondiste bien lo que se pedía (${describeFocus(focus)}).`;

  return {
    star_situation: s,
    star_task: t,
    star_action: a,
    star_result: r,
    technical_clarity: tech,
    relevance: rel,
    turn_average_score: avg,
    metrics_detected: metrics.slice(0, 5),
    tech_terms_detected: matchedTech.slice(0, 5),
    strengths,
    improvement_areas: improvements,
    improved_example_star: buildQuestionSpecificStarExample(questionText, careerCode, role)
  };
}

// Qué partes STAR pide la pregunta (misma lógica que backend/app/agents/question_focus.py).
function questionFocus(questionText) {
  const q = normalizeStr(questionText || "");
  const asks = [];
  if (/cuentame|platicame|describe|relata|hablame|una vez|ocasion|situacion|alguna vez|proyecto|reto|momento|experiencia/.test(q)) asks.push("star_situation");
  if (/\btu (rol|papel|responsabilidad|meta|objetivo|tarea|parte|aporte|contribucion)|te (toco|pidieron|asignaron|correspond)|que (debias|tenias que)|de que (eras|partes)|responsable de|que parte/.test(q)) asks.push("star_task");
  if (/\bcomo\b|que hiciste|que haces|que harias|estrategia|\bplan\b|pasos|enfoque|que (acciones|medidas|decisiones|herramientas|metodo)|que parte (construiste|hiciste|programaste)/.test(q)) asks.push("star_action");
  if (/resultado|lograste|\blogro|impacto|entregable|como (termino|acabo|salio)|que obtuviste|que paso (despues|al final)|mediste|metrica|aprendiste|que cambio|como te fue/.test(q)) asks.push("star_result");
  const concrete = asks.some((d) => d !== "star_situation");
  const finalAsks = concrete ? asks : ["star_situation", "star_task", "star_action", "star_result"];
  const technical = /tecnic|servicio|caida|incidente|falla|codigo|\bapi\b|framework|lenguaje|herramienta|base de datos|arquitect|\bbug|error|sistema|despliegue|deploy|produccion|entorno|servidor|nube|prueba|\btest|algoritmo|rendimiento|datos|modelo|\bgit\b|migracion|backend|frontend|software|programa|analisis|infraestructura|seguridad|integracion/.test(q);
  return { asks: finalAsks, technical, full: finalAsks.length === 4 };
}

function weightedAverage(scores, focus) {
  const dims = ["star_situation", "star_task", "star_action", "star_result", "technical_clarity", "relevance"];
  const w = {};
  if (focus.full) dims.forEach((d) => { w[d] = 1; });
  else {
    focus.asks.forEach((d) => { w[d] = 1; });
    w.relevance = 1;
    w.technical_clarity = focus.technical ? 1 : 0.5;
  }
  let total = 0, weight = 0;
  Object.keys(w).forEach((d) => { total += scores[d] * w[d]; weight += w[d]; });
  const base = total / weight;
  dims.forEach((d) => {
    if (!(d in w) && scores[d] > base) { total += 0.5 * scores[d]; weight += 0.5; }
  });
  return Number((total / weight).toFixed(2));
}

function describeFocus(focus) {
  if (focus.full) return "la historia completa: contexto, tu papel, qué hiciste y el resultado";
  const names = { star_task: "tu papel o meta (Tarea)", star_action: "qué hiciste y cómo (Acción)", star_result: "el resultado (Resultado)" };
  const parts = focus.asks.filter((d) => d !== "star_situation").map((d) => names[d]);
  return parts.length ? parts.join(" y ") : names.star_action;
}

function buildQuestionSpecificStarExample(questionText, careerCode, role) {
  const careerObj = CAREER_CATALOG.find((c) => c.code === careerCode) || CAREER_CATALOG[0];
  const sampleTools = careerObj.lexicon.slice(0, 4).join(", ");
  // Tema de la pregunta sin saludos ni transiciones ("Hola, gracias por tu tiempo. Empecemos.")
  const sentences = String(questionText || "").split(/(?<=[.?!])\s+/).map((x) => x.trim());
  const greeting = /^(hola|gracias|muchas gracias|empecemos|entiendo|de acuerdo|perfecto|muy bien|vamos con|ok)\b/i;
  const topic = (sentences.find((x) => x.length > 25 && !greeting.test(x)) || sentences.pop() || "")
    .replace(/^¿|[?.!]$/g, "");
  const shortTopic = topic.length > 110 ? topic.slice(0, 107) + "…" : topic;
  return `Sobre "${shortTopic}", para el puesto de ${role} (Situación), mi objetivo era resolver la falla cumpliendo los requerimientos técnicos y el tiempo límite (Tarea). Diagnosticué la causa raíz e implementé directamente la solución utilizando ${sampleTools}, validando cada cambio con pruebas controladas (Acción). Como resultado, reduje la tasa de incidentes en un [X %] y optimicé el tiempo de respuesta en un [Y %] (Resultado; usa tus cifras reales).`;
}

// =============================================================================
// EVALUACIÓN LOCAL INMEDIATA (los agentes de IA corren en el backend)
// La evaluación de gemini-3.8-flash / gpt-4o-mini llega desde /api/sessions/turn
// y reemplaza a esta. Sin backend (modo demo) se usa solo esta evaluación local.
// =============================================================================
async function evaluateTurnWithConfiguredAgents(questionText, cleanResponse) {
  return evaluateResponseCritical(questionText, cleanResponse, appState.careerCode, appState.targetRole);
}

function getRandomQuestionCount() {
  return Math.floor(Math.random() * 6) + 15;
}

function showView(viewId) {
  ["view-login", "view-setup", "view-chat", "view-report", "view-history"].forEach((id) => {
    const el = document.getElementById(id);
    if (el) el.classList.toggle("hidden", id !== viewId);
  });
  const nav = document.getElementById("topbar-nav");
  if (nav) nav.classList.toggle("hidden", viewId === "view-login");
}

function setAuthTab(mode) {
  const tabLogin = document.getElementById("tab-login");
  const tabReg = document.getElementById("tab-register");
  const panelLogin = document.getElementById("form-login-panel");
  const panelReg = document.getElementById("form-register-panel");
  const feedback = document.getElementById("auth-feedback");

  if (feedback) feedback.classList.add("hidden");

  if (mode === "login") {
    tabLogin.classList.add("active");
    tabReg.classList.remove("active");
    panelLogin.classList.remove("hidden");
    panelReg.classList.add("hidden");
  } else {
    tabReg.classList.add("active");
    tabLogin.classList.remove("active");
    panelReg.classList.remove("hidden");
    panelLogin.classList.add("hidden");
  }
}

function showAuthFeedback(message, isError = true) {
  const el = document.getElementById("auth-feedback");
  if (!el) return;
  el.textContent = message;
  el.style.color = isError ? "var(--red)" : "var(--green)";
  el.classList.remove("hidden");
}

// =============================================================================
// REINICIO ESTRICTO DE FORMULARIO Y SESIÓN AL CAMBIAR DE USUARIO
// =============================================================================
function resetPracticeFormAndSession() {
  appState.sessionId = null;
  appState.sending = false;
  appState.reportInProgress = false;
  setChatLocked(false);
  appState.turns = [];
  appState.questionsPool = [];
  appState.currentIndex = 0;
  appState.targetRole = "";
  appState.cvSummary = "";
  appState.vacancyContext = "";

  const careerSelect = document.getElementById("setup-career");
  if (careerSelect && careerSelect.options.length > 0) {
    careerSelect.selectedIndex = 0;
  }
  const roleInput = document.getElementById("setup-role");
  if (roleInput) roleInput.value = "";
  const cvInput = document.getElementById("setup-cv");
  if (cvInput) cvInput.value = "";
  const jdInput = document.getElementById("setup-jd");
  if (jdInput) jdInput.value = "";
  const chatInput = document.getElementById("chat-input");
  if (chatInput) chatInput.value = "";
  const chatMessages = document.getElementById("chat-messages");
  if (chatMessages) chatMessages.innerHTML = "";
  const setupStatus = document.getElementById("setup-status");
  if (setupStatus) setupStatus.classList.add("hidden");

  resetStarMeters();
}

function setLoggedInUser(userObj) {
  appState.user = userObj;
  // Limpiar siempre el apartado de nueva práctica y sesión previa para no mezclar datos de otro usuario
  resetPracticeFormAndSession();

  const badge = document.getElementById("user-badge");
  const avatar = document.getElementById("user-avatar-chip");
  if (badge) {
    badge.textContent = `${userObj.full_name} (${userObj.email})`;
  }
  if (avatar) {
    const initials = (userObj.full_name || "U")
      .split(/\s+/)
      .map((p) => p[0])
      .join("")
      .substring(0, 2)
      .toUpperCase();
    avatar.textContent = initials;
  }

  // Limpiar campos de login/registro
  ["login-email", "login-password", "login-name", "reg-email", "reg-university", "reg-password"].forEach((id) => {
    const el = document.getElementById(id);
    if (el) el.value = "";
  });

  showView("view-setup");
}

async function handleLocalLogin() {
  const email = document.getElementById("login-email").value.trim().toLowerCase();
  const password = document.getElementById("login-password").value;

  if (!email || !password) {
    showAuthFeedback("Ingresa tu correo electrónico y tu contraseña.");
    return;
  }

  if (appState.backendOnline) {
    const r = await apiFetch("/api/auth/login", { method: "POST", body: JSON.stringify({ email, password }) });
    if (r.ok) {
      setToken(r.data.access_token);
      setLoggedInUser(r.data);
      return;
    }
    if (!r.offline) {
      showAuthFeedback(apiErrorMessage(r, "No se pudo iniciar sesión."));
      return;
    }
    appState.backendOnline = false;
  }

  // Modo demo (sin servidor): cuentas guardadas solo en este navegador
  const found = appState.registeredUsers.find((u) => u.email.toLowerCase() === email);
  const ok = found && found.password_hash
    && (await hashDemoPassword(password, found.password_hash.split("$")[0])) === found.password_hash;
  if (!ok) {
    showAuthFeedback("Correo o contraseña incorrectos.");
    return;
  }
  setLoggedInUser(found);
}

async function handleLocalRegister() {
  const fullName = document.getElementById("login-name").value.trim();
  const email = document.getElementById("reg-email").value.trim().toLowerCase();
  const university = document.getElementById("reg-university").value.trim();
  const password = document.getElementById("reg-password").value;

  if (fullName.length < 3 || !fullName.includes(" ")) {
    showAuthFeedback("Ingresa tu nombre y apellido reales.");
    return;
  }

  if (!university || university.length < 2) {
    showAuthFeedback("Ingresa el nombre de tu universidad o institución.");
    return;
  }

  if (!password || password.length < 8) {
    showAuthFeedback("La contraseña debe tener al menos 8 caracteres.");
    return;
  }

  showAuthFeedback("Verificando tu correo...", false);
  const emailValidation = await validateRealEmailAccount(email);
  if (!emailValidation.valid) {
    showAuthFeedback(emailValidation.reason, true);
    return;
  }

  if (appState.backendOnline) {
    const r = await apiFetch("/api/auth/register", {
      method: "POST",
      body: JSON.stringify({ full_name: fullName, email: emailValidation.email, password, university })
    });
    if (r.ok) {
      setToken(r.data.access_token);
      setLoggedInUser(r.data);
      return;
    }
    if (!r.offline) {
      showAuthFeedback(apiErrorMessage(r, "No se pudo registrar la cuenta."));
      return;
    }
    appState.backendOnline = false;
  }

  // Modo demo (sin servidor)
  if (appState.registeredUsers.some((u) => u.email.toLowerCase() === emailValidation.email)) {
    showAuthFeedback("Ya existe una cuenta con este correo electrónico. Inicia sesión en la primera pestaña.");
    return;
  }
  const newUser = {
    user_id: "demo-" + crypto.getRandomValues(new Uint32Array(2)).join(""),
    full_name: fullName,
    email: emailValidation.email,
    password_hash: await hashDemoPassword(password),
    university,
    auth_provider: "local"
  };
  appState.registeredUsers.push(newUser);
  saveRegisteredUsers();
  setLoggedInUser(newUser);
}

// =============================================================================
// VERIFICADOR OFICIAL DE GOOGLE IDENTITY SERVICES (accounts.google.com/gsi/client)
// =============================================================================
function decodeJwtPayload(token) {
  try {
    const base64Url = token.split(".")[1];
    const base64 = base64Url.replace(/-/g, "+").replace(/_/g, "/");
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split("")
        .map((c) => "%" + ("00" + c.charCodeAt(0).toString(16)).slice(-2))
        .join("")
    );
    return JSON.parse(jsonPayload);
  } catch (_) {
    return null;
  }
}

async function handleGoogleCredentialResponse(response) {
  if (!response || !response.credential) {
    showAuthFeedback("Google no entregó una credencial. Intenta de nuevo.");
    return;
  }

  if (appState.backendOnline) {
    // Verificación criptográfica en el servidor (firma, emisor, expiración y Client ID)
    const r = await apiFetch("/api/auth/google", {
      method: "POST",
      body: JSON.stringify({ credential: response.credential })
    });
    if (r.ok) {
      setToken(r.data.access_token);
      setLoggedInUser(r.data);
      return;
    }
    if (!r.offline) {
      showAuthFeedback(apiErrorMessage(r, "Google rechazó la credencial."));
      return;
    }
    appState.backendOnline = false;
  }

  // Modo demo (sin servidor): solo identifica al usuario en ESTE navegador.
  const payload = decodeJwtPayload(response.credential);
  if (!payload || !payload.email || !payload.email_verified) {
    showAuthFeedback("La credencial de Google no pudo leerse.");
    return;
  }
  setLoggedInUser({
    user_id: "google-" + payload.sub,
    full_name: payload.name || payload.email.split("@")[0],
    email: payload.email.toLowerCase(),
    avatar_url: payload.picture || null,
    university: payload.hd || "Cuenta de Google",
    auth_provider: "google"
  });
}

async function initOfficialGoogleVerifier() {
  // El Client ID del backend (.env) tiene prioridad sobre config.js
  if (appState.backendOnline) {
    const r = await apiFetch("/api/auth/google-config", { method: "GET" }, 5000);
    if (r.ok && r.data && r.data.is_configured && r.data.google_client_id) {
      appState.googleClientId = r.data.google_client_id;
    }
  }

  // El script de Google carga con async: esperarlo hasta 5 s
  for (let i = 0; i < 25 && !(window.google && window.google.accounts && window.google.accounts.id); i++) {
    await new Promise((res) => setTimeout(res, 200));
  }

  if (appState.googleClientId && window.google && window.google.accounts && window.google.accounts.id) {
    window.google.accounts.id.initialize({
      client_id: appState.googleClientId,
      callback: handleGoogleCredentialResponse,
      auto_select: false,
      use_fedcm_for_prompt: true
    });
    const container = document.getElementById("google-gsi-button-container");
    if (container) {
      window.google.accounts.id.renderButton(container, {
        theme: "outline",
        size: "large",
        width: 340,
        text: "signin_with",
        locale: "es"
      });
      const fallbackBtn = document.getElementById("btn-google-login");
      if (fallbackBtn) fallbackBtn.classList.add("hidden");
    }
  }
}

function handleGoogleLoginButtonClick() {
  if (location.protocol === "file:") {
    showAuthFeedback("Google no funciona abriendo el archivo directamente. Abre la página desde http://localhost:3000.");
    return;
  }
  if (!appState.googleClientId) {
    showAuthFeedback("El inicio con Google aún no está configurado (falta GOOGLE_CLIENT_ID). Puedes usar 'Registrar' e 'Iniciar sesión'.");
    return;
  }
  if (window.google && window.google.accounts && window.google.accounts.id) {
    window.google.accounts.id.prompt();
    return;
  }
  showAuthFeedback("No se pudo cargar el script de Google (revisa tu conexión o el bloqueador de anuncios).");
}

function populateCareers() {
  const careerSelect = document.getElementById("setup-career");
  if (!careerSelect) return;
  careerSelect.innerHTML = CAREER_CATALOG.map(
    (c) => `<option value="${c.code}">${c.name}</option>`
  ).join("");
}

async function startInterview() {
  const careerCode = document.getElementById("setup-career").value;
  const targetRole = document.getElementById("setup-role").value.trim();
  const cvRaw = document.getElementById("setup-cv").value.trim();
  const jdRaw = document.getElementById("setup-jd").value.trim();

  const statusEl = document.getElementById("setup-status");
  if (!targetRole || !cvRaw || !jdRaw) {
    if (statusEl) {
      statusEl.textContent = "Completa el puesto objetivo, el resumen de tu currículum y el contexto de la vacante.";
      statusEl.classList.remove("hidden");
    }
    return;
  }
  if (statusEl) statusEl.classList.add("hidden");

  const randomTotal = getRandomQuestionCount();
  appState.careerCode = careerCode;
  appState.targetRole = targetRole;
  appState.cvSummary = anonymizeText(cvRaw);
  appState.vacancyContext = anonymizeText(jdRaw);
  appState.totalQuestions = randomTotal;
  appState.currentIndex = 0;
  appState.turns = [];

  const careerObj = CAREER_CATALOG.find((c) => c.code === careerCode) || CAREER_CATALOG[0];
  appState.questionsPool = buildVacancyTailoredQuestions(
    careerObj,
    targetRole,
    appState.cvSummary,
    appState.vacancyContext,
    randomTotal
  );

  appState.sessionId = null;
  appState.serverSession = false;
  appState.reportInProgress = false;
  appState.sending = false;
  setChatLocked(false);
  if (appState.backendOnline && getToken()) {
    const btn = document.getElementById("btn-start-interview");
    if (btn) btn.disabled = true;
    const r = await apiFetch("/api/sessions/start", {
      method: "POST",
      body: JSON.stringify({
        career_code: careerCode,
        target_role: targetRole,
        seniority_level: "Junior / Intern",
        cv_text: appState.cvSummary,
        job_description_text: appState.vacancyContext,
        total_questions: randomTotal,
        allow_followups: false
      })
    });
    if (btn) btn.disabled = false;
    if (r.ok) {
      appState.sessionId = r.data.session_id;
      appState.serverSession = true;
      appState.totalQuestions = r.data.total_questions || randomTotal;
      if (r.data.question_text) {
        appState.questionsPool[0] = r.data.question_text;
      }
    } else if (r.status === 401) {
      setToken("");
      appState.user = null;
      showView("view-login");
      showAuthFeedback("Tu sesión expiró. Inicia sesión de nuevo.");
      return;
    } else if (!r.offline && statusEl) {
      statusEl.textContent = apiErrorMessage(r, "No se pudo iniciar la entrevista en el servidor.");
      statusEl.classList.remove("hidden");
      return;
    }
  }

  renderChatInitial();
  showView("view-chat");
}

function renderChatInitial() {
  const list = document.getElementById("chat-messages");
  list.innerHTML = "";
  appendChatMessage("ai", appState.questionsPool[0]);
  updateProgressCounter();
  resetStarMeters();
  appState.turnStartTime = Date.now();
}

function appendChatMessage(sender, text) {
  const list = document.getElementById("chat-messages");
  const div = document.createElement("div");
  div.className = `msg ${sender === "ai" ? "msg-ai" : "msg-user"}`;
  div.textContent = text;
  list.appendChild(div);
  list.scrollTop = list.scrollHeight;
}

function updateProgressCounter() {
  const el = document.getElementById("chat-progress-label");
  if (el) {
    el.textContent = `Pregunta ${Math.min(appState.currentIndex + 1, appState.totalQuestions)} de ${appState.totalQuestions}`;
  }
}

function getBarColor(score) {
  if (score >= 4) return "#16a34a";
  if (score === 3) return "#2563eb";
  if (score === 2) return "#d97706";
  return "#dc2626";
}

function resetStarMeters() {
  const keys = ["situation", "task", "action", "result", "clarity", "relevance"];
  keys.forEach((k) => {
    const bar = document.getElementById(`bar-${k}`);
    const val = document.getElementById(`val-${k}`);
    if (bar) {
      bar.style.width = "0%";
      bar.style.backgroundColor = "#e5e7eb";
    }
    if (val) val.textContent = "-";
  });
  const badge = document.getElementById("turn-avg-badge");
  if (badge) {
    badge.textContent = "- / 5.0";
    badge.style.color = "var(--muted)";
  }
  const mTags = document.getElementById("detected-metrics-tags");
  if (mTags) mTags.textContent = "Ninguna";
  const tTags = document.getElementById("detected-tech-tags");
  if (tTags) tTags.textContent = "Ninguna";
  const feedbackBox = document.getElementById("live-feedback-note");
  if (feedbackBox) {
    feedbackBox.textContent = "El evaluador califica de 0 a 5 cada dimensión sin complacencia. Una habilidad no demostrada o respuesta sin sentido recibe 0/5.";
  }
}

function updateStarMeters(evalObj) {
  const map = {
    situation: evalObj.star_situation,
    task: evalObj.star_task,
    action: evalObj.star_action,
    result: evalObj.star_result,
    clarity: evalObj.technical_clarity,
    relevance: evalObj.relevance
  };
  Object.entries(map).forEach(([k, score]) => {
    const bar = document.getElementById(`bar-${k}`);
    const val = document.getElementById(`val-${k}`);
    if (bar) {
      bar.style.width = `${(score / 5) * 100}%`;
      bar.style.backgroundColor = getBarColor(score);
    }
    if (val) val.textContent = `${score}/5`;
  });

  const badge = document.getElementById("turn-avg-badge");
  if (badge) {
    badge.textContent = `${evalObj.turn_average_score} / 5.0`;
    badge.style.color = getBarColor(Math.round(evalObj.turn_average_score));
  }

  const mTags = document.getElementById("detected-metrics-tags");
  if (mTags) {
    const mList = evalObj.metrics_detected || [];
    mTags.innerHTML = mList.length > 0
      ? mList.map((m) => `<span class="tag-pill">${escapeHtml(m)}</span>`).join("")
      : "0 métricas cuantitativas";
  }

  const tTags = document.getElementById("detected-tech-tags");
  if (tTags) {
    const tList = evalObj.tech_terms_detected || [];
    tTags.innerHTML = tList.length > 0
      ? tList.map((t) => `<span class="tag-pill">${escapeHtml(t)}</span>`).join("")
      : "Sin términos técnicos detectados";
  }

  const feedbackBox = document.getElementById("live-feedback-note");
  if (feedbackBox) {
    feedbackBox.textContent = `${evalObj.strengths} ${evalObj.improvement_areas}`;
  }
}

function showTypingIndicator() {
  const list = document.getElementById("chat-messages");
  const div = document.createElement("div");
  div.className = "msg msg-typing";
  div.id = "typing-indicator";
  div.setAttribute("aria-live", "polite");
  div.textContent = "Escribiendo…";
  list.appendChild(div);
  list.scrollTop = list.scrollHeight;
}

function hideTypingIndicator() {
  const el = document.getElementById("typing-indicator");
  if (el) el.remove();
}

// La evaluación de la IA llega unos segundos después (se calcula en segundo plano).
async function pollTurnEvaluation(turn, turnId) {
  const sessionId = appState.sessionId;
  for (let i = 0; i < 40; i++) {
    await new Promise((res) => setTimeout(res, i < 5 ? 1000 : 2000));
    if (appState.sessionId !== sessionId) return; // el usuario cambió de sesión
    const r = await apiFetch(
      `/api/sessions/${encodeURIComponent(sessionId)}/turns/${encodeURIComponent(turnId)}/evaluation`,
      { method: "GET" }, 8000
    );
    if (r.ok && r.data && r.data.ready) {
      turn.evaluation = { ...turn.evaluation, ...r.data.evaluation };
      // Solo actualiza el panel si sigue siendo la respuesta más reciente
      if (appState.turns[appState.turns.length - 1] === turn) {
        updateStarMeters(turn.evaluation);
      }
      return;
    }
    if (r.status === 401 || r.status === 404) return;
  }
}

function setChatLocked(locked) {
  ["chat-input", "btn-send-chat", "btn-finish-early"].forEach((id) => {
    const el = document.getElementById(id);
    if (el) el.disabled = locked;
  });
}

async function sendChatResponse() {
  const input = document.getElementById("chat-input");
  const text = input.value.trim();
  if (!text || appState.sending || appState.reportInProgress) return;
  if (appState.currentIndex >= appState.totalQuestions) return;
  appState.sending = true;
  try {
    await sendChatResponseInner(input, text);
  } finally {
    appState.sending = false;
  }
}

async function sendChatResponseInner(input, text) {

  input.value = "";
  const currentQ = appState.questionsPool[appState.currentIndex];
  const cleanResponse = anonymizeText(text);
  appendChatMessage("user", cleanResponse);

  const elapsedSec = Number(((Date.now() - appState.turnStartTime) / 1000).toFixed(1));
  // Evaluación local inmediata; la del agente de IA la reemplaza al llegar.
  let evalObj = await evaluateTurnWithConfiguredAgents(currentQ, cleanResponse);
  let nextMessageFromServer = null;
  let pendingTurnId = null;

  if (appState.serverSession) {
    const sendBtn = document.getElementById("btn-send-chat");
    if (sendBtn) sendBtn.disabled = true;
    showTypingIndicator();
    const r = await apiFetch("/api/sessions/turn", {
      method: "POST",
      body: JSON.stringify({
        session_id: appState.sessionId,
        candidate_response: cleanResponse.slice(0, 4000),
        response_time_seconds: elapsedSec,
        allow_followups: false
      })
    });
    hideTypingIndicator();
    if (sendBtn) sendBtn.disabled = false;
    if (r.ok && r.data) {
      if (r.data.evaluation) {
        evalObj = { ...evalObj, ...r.data.evaluation };
      }
      if (r.data.evaluation_pending && r.data.turn_id) {
        pendingTurnId = r.data.turn_id;
      }
      nextMessageFromServer = r.data.next_interviewer_message || null;
    }
  }

  const turn = {
    questionNumber: appState.currentIndex + 1,
    questionText: currentQ,
    responseText: cleanResponse,
    evaluation: evalObj
  };
  appState.turns.push(turn);
  updateStarMeters(evalObj);
  if (pendingTurnId) pollTurnEvaluation(turn, pendingTurnId);
  appState.currentIndex += 1;

  if (appState.currentIndex >= appState.totalQuestions) {
    appendChatMessage("ai", nextMessageFromServer ||
      "Eso es todo por hoy, gracias por tus respuestas. Dame un momento y te muestro tu evaluación con recomendaciones.");
    setTimeout(() => {
      buildAndShowReport();
    }, 400);
  } else {
    if (nextMessageFromServer) {
      appState.questionsPool[appState.currentIndex] = nextMessageFromServer;
    }
    updateProgressCounter();
    appendChatMessage("ai", appState.questionsPool[appState.currentIndex]);
    appState.turnStartTime = Date.now();
  }
}

function finishInterviewEarly() {
  if (appState.turns.length === 0) {
    appendChatMessage("ai", "Debes responder al menos una pregunta para generar el reporte de evaluación.");
    return;
  }
  buildAndShowReport();
}

async function buildAndShowReport() {
  if (appState.reportInProgress) return; // doble clic en "Terminar" o Enter repetido
  appState.reportInProgress = true;
  setChatLocked(true);
  const turns = appState.turns;

  // Ejemplos STAR redactados por el Agente Sintetizador (backend), si hay sesión en servidor
  if (appState.serverSession && appState.sessionId) {
    const r = await apiFetch(`/api/sessions/${encodeURIComponent(appState.sessionId)}/report`, { method: "GET" }, 60000);
    if (r.ok && r.data) mergeServerReportIntoTurns(turns, r.data);
  }
  const avgScore = turns.length
    ? Number((turns.reduce((acc, t) => acc + t.evaluation.turn_average_score, 0) / turns.length).toFixed(2))
    : 0.0;

  const userHistory = getCurrentUserHistoryList();
  let evolution = 0.0;
  if (userHistory.length > 0) {
    const prev = userHistory[0].overallScore;
    if (prev > 0) {
      evolution = Number((((avgScore - prev) / prev) * 100).toFixed(1));
    } else if (avgScore > 0) {
      evolution = 100.0;
    }
  }

  // Una sola entrada por entrevista. Con servidor solo se guarda el resumen; la conversación
  // se consulta al servidor (no se deja texto de respuestas en el navegador).
  const entryId = appState.sessionId || `local-${Date.now()}`;
  const entry = {
    id: entryId,
    server: Boolean(appState.serverSession && appState.sessionId),
    date: new Date().toLocaleDateString("es-MX"),
    careerCode: appState.careerCode,
    targetRole: appState.targetRole,
    overallScore: avgScore,
    evolutionRate: evolution
  };
  if (!entry.server) entry.turns = JSON.parse(JSON.stringify(turns));
  const existing = userHistory.findIndex((h) => h.id === entryId);
  if (existing >= 0) userHistory.splice(existing, 1);
  userHistory.unshift(entry);
  saveHistoriesByUser();

  renderReport({
    turns, overallScore: avgScore, evolution, careerCode: appState.careerCode,
    targetRole: appState.targetRole, dateLabel: entry.date, sessionId: appState.sessionId, fromHistory: false
  });
}

function mergeServerReportIntoTurns(turns, data) {
  (data.turn_evaluations || []).forEach((ev) => {
    const t = turns.find((x) => x.questionNumber === ev.question_number);
    if (t) t.evaluation = { ...t.evaluation, ...ev };
  });
  (data.weakest_responses || []).forEach((w) => {
    const t = turns.find((x) => x.questionNumber === w.question_number);
    if (t && w.improved_star_example) t.evaluation.improved_example_star = w.improved_star_example;
  });
}

const EMPTY_EVAL = {
  star_situation: 0, star_task: 0, star_action: 0, star_result: 0, technical_clarity: 0, relevance: 0,
  turn_average_score: 0, strengths: "", improvement_areas: "Esta respuesta no alcanzó a evaluarse.",
  improved_example_star: ""
};

function renderReport(data) {
  appState.reportData = data;
  const turns = data.turns;
  const careerObj = CAREER_CATALOG.find((c) => c.code === data.careerCode) || CAREER_CATALOG[0];
  const weakestTwo = [...turns]
    .sort((a, b) => a.evaluation.turn_average_score - b.evaluation.turn_average_score)
    .slice(0, 2);

  document.getElementById("rep-score").textContent = `${data.overallScore} / 5.0`;
  document.getElementById("rep-role").textContent =
    `${data.targetRole} (${data.careerCode}) · ${turns.length} respuestas evaluadas · ${data.dateLabel || ""}`;
  document.getElementById("rep-evolution").textContent =
    data.evolution >= 0 ? `+${data.evolution}% vs. tu sesión previa` : `${data.evolution}% vs. tu sesión previa`;

  const weakContainer = document.getElementById("rep-weakest-list");
  weakContainer.innerHTML = weakestTwo
    .map(
      (item) => `
      <div style="border: 1px solid var(--border); border-radius: 10px; padding: 1.1rem; margin-bottom: 1rem;">
        <div style="font-size: 0.8rem; color: var(--muted); margin-bottom: 0.25rem;">
          Pregunta ${item.questionNumber} · Puntaje obtenido: <strong>${item.evaluation.turn_average_score} / 5.0</strong>
          (S:${item.evaluation.star_situation} · T:${item.evaluation.star_task} · A:${item.evaluation.star_action} · R:${item.evaluation.star_result} · Tec:${item.evaluation.technical_clarity} · Pert:${item.evaluation.relevance})
        </div>
        <div style="font-weight: 500; font-size: 0.92rem; margin-bottom: 0.55rem;">${escapeHtml(item.questionText)}</div>
        <div style="font-size: 0.84rem; color: var(--muted); margin-bottom: 0.45rem;">
          <strong>Tu respuesta:</strong> "${escapeHtml(item.responseText)}"
        </div>
        <div style="font-size: 0.82rem; color: var(--red); margin-bottom: 0.55rem;">
          <strong>${escapeHtml(item.evaluation.improvement_areas)}</strong>
        </div>
        ${item.evaluation.improved_example_star ? `
        <div style="font-size: 0.84rem; background: #f9fafb; border-left: 3px solid var(--text); padding: 0.65rem 0.8rem; border-radius: 4px;">
          <strong>Ejemplo de respuesta nivel 5/5 bajo método STAR:</strong> ${escapeHtml(item.evaluation.improved_example_star)}
        </div>` : ""}
      </div>`
    )
    .join("");

  const transcript = document.getElementById("rep-transcript");
  if (transcript) {
    transcript.innerHTML = turns
      .map(
        (t) => `
        <div style="padding: 0.75rem 0; border-bottom: 1px solid var(--border);">
          <div style="font-size: 0.8rem; color: var(--muted);">Pregunta ${t.questionNumber} · ${t.evaluation.turn_average_score} / 5.0</div>
          <div style="font-weight: 500; font-size: 0.88rem; margin: 0.2rem 0 0.35rem;">${escapeHtml(t.questionText)}</div>
          <div style="font-size: 0.84rem; color: var(--muted);">${escapeHtml(t.responseText)}</div>
        </div>`
      )
      .join("");
  }

  const resourcesContainer = document.getElementById("rep-resources-list");
  resourcesContainer.innerHTML = careerObj.resources
    .map(
      (r) => `
      <div style="display: flex; justify-content: space-between; align-items: center; padding: 0.75rem 0; border-bottom: 1px solid var(--border);">
        <div>
          <div style="font-weight: 500; font-size: 0.9rem;">${r.title}</div>
          <div style="font-size: 0.8rem; color: var(--muted);">${r.provider}</div>
        </div>
        <a href="${r.url}" target="_blank" rel="noopener noreferrer" class="btn btn-outline" style="padding: 0.4rem 0.8rem; font-size: 0.8rem;">Abrir</a>
      </div>`
    )
    .join("");

  const pdfStatus = document.getElementById("pdf-download-status");
  if (pdfStatus) pdfStatus.classList.add("hidden");
  const csat = document.getElementById("csat-block");
  if (csat) csat.classList.toggle("hidden", Boolean(data.fromHistory));
  const back = document.getElementById("btn-back-to-history");
  if (back) back.classList.toggle("hidden", !data.fromHistory);

  showView("view-report");
}

function buildMinimalPdfBinary(lines) {
  const sanitize = (s) =>
    normalizeStr(s)
      .replace(/[()\\]/g, "")
      .substring(0, 95);

  let streamContent = "BT\n/F1 11 Tf\n50 760 Td\n14 TL\n";
  lines.slice(0, 48).forEach((line) => {
    streamContent += `(${sanitize(line)}) Tj T*\n`;
  });
  streamContent += "ET";

  const objects = [
    "1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n",
    "2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n",
    "3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>\nendobj\n",
    "4 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n",
    `5 0 obj\n<< /Length ${streamContent.length} >>\nstream\n${streamContent}\nendstream\nendobj\n`
  ];

  let pdf = "%PDF-1.4\n";
  const offsets = [0];
  objects.forEach((obj) => {
    offsets.push(pdf.length);
    pdf += obj;
  });
  const xrefStart = pdf.length;
  pdf += `xref\n0 ${objects.length + 1}\n0000000000 65535 f \n`;
  for (let i = 1; i <= objects.length; i++) {
    pdf += String(offsets[i]).padStart(10, "0") + " 00000 n \n";
  }
  pdf += `trailer\n<< /Size ${objects.length + 1} /Root 1 0 R >>\nstartxref\n${xrefStart}\n%%EOF`;
  return new Blob([pdf], { type: "application/pdf" });
}

function downloadReportPdf() {
  const userName = (appState.user && appState.user.full_name) || "Candidato";
  const safeFileName = `Reporte_InterviewAI_${normalizeStr(userName).replace(/\s+/g, "_")}.pdf`;
  const scoreText = document.getElementById("rep-score").textContent;
  const roleText = document.getElementById("rep-role").textContent;
  const evoText = document.getElementById("rep-evolution").textContent;
  const report = appState.reportData || { turns: appState.turns, careerCode: appState.careerCode };
  const careerObj = CAREER_CATALOG.find((c) => c.code === report.careerCode) || CAREER_CATALOG[0];

  const sortedByWeakest = [...report.turns].sort(
    (a, b) => a.evaluation.turn_average_score - b.evaluation.turn_average_score
  );
  const weakestTwo = sortedByWeakest.slice(0, 2);

  try {
    if (window.jspdf && window.jspdf.jsPDF) {
      const { jsPDF } = window.jspdf;
      const doc = new jsPDF({ unit: "pt", format: "letter" });
      const margin = 45;
      const maxWidth = 522;
      let y = 50;

      const writeWrapped = (text, fontSize = 10, isBold = false, color = [17, 24, 39]) => {
        doc.setFont("helvetica", isBold ? "bold" : "normal");
        doc.setFontSize(fontSize);
        doc.setTextColor(color[0], color[1], color[2]);
        const split = doc.splitTextToSize(String(text || ""), maxWidth);
        split.forEach((line) => {
          if (y > 730) {
            doc.addPage();
            y = 50;
          }
          doc.text(line, margin, y);
          y += fontSize + 4;
        });
        y += 4;
      };

      writeWrapped("InterviewAI — Reporte Critico de Entrevista y Plan de Accion", 16, true, [24, 24, 27]);
      writeWrapped(`Candidato: ${userName} (${(appState.user && appState.user.email) || ""})`, 10, false, [107, 114, 128]);
      writeWrapped(`Puesto y Carrera: ${roleText}`, 10, false, [107, 114, 128]);
      writeWrapped(`Calificacion Global (Escala 0-5): ${scoreText} (${evoText})`, 12, true, [24, 24, 27]);
      y += 8;

      writeWrapped("1. Analisis Critico de Respuestas Mas Debiles", 13, true);
      weakestTwo.forEach((item, idx) => {
        writeWrapped(
          `${idx + 1}) Pregunta ${item.questionNumber} (Puntaje: ${item.evaluation.turn_average_score}/5.0): ${item.questionText}`,
          10,
          true
        );
        writeWrapped(`Tu respuesta: "${item.responseText}"`, 9.5, false, [75, 85, 99]);
        writeWrapped(`${item.evaluation.improvement_areas}`, 9.5, false, [180, 35, 24]);
        if (item.evaluation.improved_example_star) {
          writeWrapped(`Ejemplo STAR recomendado: ${item.evaluation.improved_example_star}`, 9.5, false, [17, 24, 39]);
        }
        y += 6;
      });

      writeWrapped("2. Plan de Accion y Recursos Recomendados", 13, true);
      careerObj.resources.forEach((r) => {
        writeWrapped(`• ${r.title} (${r.provider}) — ${r.url}`, 10, false);
      });
      y += 6;

      writeWrapped("3. Conversacion completa", 13, true);
      report.turns.forEach((t) => {
        writeWrapped(`Pregunta ${t.questionNumber} (${t.evaluation.turn_average_score}/5.0): ${t.questionText}`, 10, true);
        writeWrapped(`Tu respuesta: ${t.responseText}`, 9.5, false, [75, 85, 99]);
      });

      doc.save(safeFileName);
    } else {
      const lines = [
        "InterviewAI - Reporte Final de Entrevista",
        `Candidato: ${userName}`,
        `Puesto: ${roleText}`,
        `Calificacion Global: ${scoreText} (${evoText})`,
        "------------------------------------------------------------",
        "Respuestas con mayor oportunidad de mejora:"
      ];
      weakestTwo.forEach((item) => {
        lines.push(`Pregunta ${item.questionNumber} (${item.evaluation.turn_average_score}/5): ${item.questionText}`);
        lines.push(`Tu respuesta: ${item.responseText}`);
        lines.push(`Diagnostico: ${item.evaluation.improvement_areas}`);
        lines.push(`Mejora STAR: ${item.evaluation.improved_example_star}`);
        lines.push(" ");
      });
      const blob = buildMinimalPdfBinary(lines);
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = safeFileName;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      setTimeout(() => URL.revokeObjectURL(url), 1500);
    }

    const pdfStatus = document.getElementById("pdf-download-status");
    if (pdfStatus) {
      pdfStatus.textContent = `PDF descargado (${safeFileName})`;
      pdfStatus.classList.remove("hidden");
    }
  } catch (_) {}
}

async function renderHistoryView() {
  const tbody = document.getElementById("history-tbody");
  const ownerLabel = document.getElementById("history-owner-label");
  if (ownerLabel && appState.user) {
    ownerLabel.textContent = `Cuenta activa: ${appState.user.full_name} (${appState.user.email})`;
  }
  if (!tbody) return;
  showView("view-history");
  tbody.innerHTML = `<tr><td colspan="5" style="padding: 1rem; text-align: center; color: var(--muted);">Cargando…</td></tr>`;

  // Con servidor, el historial sale de la base de datos (una fila por entrevista terminada).
  let rows = null;
  if (appState.backendOnline && getToken()) {
    const r = await apiFetch("/api/users/me/history", { method: "GET" });
    if (r.ok && Array.isArray(r.data)) {
      rows = r.data.map((h) => ({
        id: h.session_id, server: true,
        date: h.started_at ? new Date(h.started_at).toLocaleDateString("es-MX") : "",
        careerCode: h.career_code, targetRole: h.target_role,
        overallScore: h.overall_score, evolutionRate: Number(h.score_evolution_rate || 0)
      }));
    }
  }
  if (!rows) rows = getCurrentUserHistoryList().filter((h) => !h.server || !appState.backendOnline);
  appState.historyRows = rows;

  if (rows.length === 0) {
    tbody.innerHTML = `<tr><td colspan="5" style="padding: 1rem; text-align: center; color: var(--muted);">Esta cuenta aún no tiene entrevistas terminadas.</td></tr>`;
    return;
  }
  tbody.innerHTML = rows
    .map(
      (h, i) => `
      <tr style="border-bottom: 1px solid var(--border);">
        <td style="padding: 0.75rem;">${escapeHtml(h.date)}</td>
        <td style="padding: 0.75rem;">${escapeHtml(h.careerCode)} — ${escapeHtml(h.targetRole)}</td>
        <td style="padding: 0.75rem; font-weight: 600;">${escapeHtml(h.overallScore)} / 5.0</td>
        <td style="padding: 0.75rem; color: var(--muted);">${h.evolutionRate >= 0 ? "+" + h.evolutionRate + "%" : h.evolutionRate + "%"}</td>
        <td style="padding: 0.75rem; text-align: right;">
          <button type="button" class="btn btn-outline history-view-btn" data-index="${i}" style="padding: 0.35rem 0.75rem; font-size: 0.8rem;">Ver</button>
        </td>
      </tr>`
    )
    .join("");
  tbody.querySelectorAll(".history-view-btn").forEach((btn) => {
    btn.addEventListener("click", () => openPastInterview(appState.historyRows[Number(btn.dataset.index)], btn));
  });
}

async function openPastInterview(h, btn) {
  if (!h) return;
  let turns = h.turns || null;
  if (h.server) {
    if (btn) { btn.disabled = true; btn.textContent = "Abriendo…"; }
    const r = await apiFetch(`/api/sessions/${encodeURIComponent(h.id)}/detail`, { method: "GET" });
    if (btn) { btn.disabled = false; btn.textContent = "Ver"; }
    if (!r.ok || !r.data) {
      alertInHistory("No se pudo abrir esta entrevista. Revisa que el servidor esté encendido.");
      return;
    }
    turns = r.data.turns.map((t) => ({
      questionNumber: t.question_number,
      questionText: t.interviewer_question,
      responseText: t.candidate_response,
      evaluation: { ...EMPTY_EVAL, ...(t.evaluation || {}) }
    }));
    if (r.data.report) mergeServerReportIntoTurns(turns, r.data.report);
  }
  if (!turns || turns.length === 0) {
    alertInHistory("Esta entrevista se guardó con una versión anterior y no tiene la conversación.");
    return;
  }
  renderReport({
    turns, overallScore: h.overallScore, evolution: h.evolutionRate, careerCode: h.careerCode,
    targetRole: h.targetRole, dateLabel: h.date, sessionId: h.server ? h.id : null, fromHistory: true
  });
}

function alertInHistory(message) {
  const el = document.getElementById("history-owner-label");
  if (el) el.textContent = message;
}

async function submitCsatRating(score) {
  if (appState.serverSession && appState.sessionId) {
    await apiFetch("/api/sessions/csat", {
      method: "POST",
      body: JSON.stringify({ session_id: appState.sessionId, csat_score: Number(score) })
    });
  }
  const msg = document.getElementById("csat-thanks");
  if (msg) {
    msg.textContent = `Calificación registrada (${score}/5).`;
    msg.classList.remove("hidden");
  }
}

window.addEventListener("DOMContentLoaded", async () => {
  loadSavedState();
  await migrateLegacyDemoUsers();
  populateCareers();
  await detectBackend();
  initOfficialGoogleVerifier();

  // Pestañas de autenticación
  document.getElementById("tab-login").addEventListener("click", () => setAuthTab("login"));
  document.getElementById("tab-register").addEventListener("click", () => setAuthTab("register"));
  document.getElementById("btn-submit-login").addEventListener("click", handleLocalLogin);
  document.getElementById("btn-submit-register").addEventListener("click", handleLocalRegister);
  document.getElementById("btn-google-login").addEventListener("click", handleGoogleLoginButtonClick);

  // Configuración y Chat
  document.getElementById("btn-start-interview").addEventListener("click", startInterview);
  document.getElementById("btn-send-chat").addEventListener("click", sendChatResponse);
  document.getElementById("btn-finish-early").addEventListener("click", finishInterviewEarly);

  document.getElementById("chat-input").addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendChatResponse();
    }
  });

  document.getElementById("nav-new-session").addEventListener("click", () => {
    resetPracticeFormAndSession();
    showView("view-setup");
  });
  document.getElementById("nav-history").addEventListener("click", renderHistoryView);
  document.getElementById("btn-logout").addEventListener("click", () => {
    setToken("");
    appState.user = null;
    if (window.google && window.google.accounts && window.google.accounts.id) {
      window.google.accounts.id.disableAutoSelect();
    }
    resetPracticeFormAndSession();
    showView("view-login");
  });

  document.getElementById("btn-print-report").addEventListener("click", downloadReportPdf);
  document.getElementById("btn-new-from-report").addEventListener("click", () => {
    resetPracticeFormAndSession();
    showView("view-setup");
  });
  document.getElementById("btn-back-from-history").addEventListener("click", () => showView("view-setup"));
  document.getElementById("btn-back-to-history").addEventListener("click", renderHistoryView);

  document.querySelectorAll(".csat-star-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      submitCsatRating(btn.getAttribute("data-score"));
    });
  });
});
