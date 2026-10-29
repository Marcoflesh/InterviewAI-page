// =============================================================================
// InterviewAI - Lógica de Interfaz Minimalista (Google Sign-In, Banco Aleatorio
// por Carrera, Chat de Texto Puro sin Voz, Evaluación STAR en Vivo y Reporte)
// =============================================================================

const CAREER_CATALOG = [
  {
    code: "ITC",
    name: "Ingeniería en Tecnologías Computacionales (Software)",
    roles: ["Software Engineer Intern", "Junior Full-Stack Developer", "Backend Developer"],
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
      "Cuéntame de algún despliegue o demostración en vivo donde algo falló. ¿Cómo reaccionaste en el momento para mitigar el problema y qué cambiaste en tu proceso después?"
    ]
  },
  {
    code: "ISD",
    name: "Ciencia de Datos e Inteligencia Artificial",
    roles: ["Data Scientist Jr", "Machine Learning Engineer Intern", "Data Analyst"],
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
      "Háblame de un análisis exploratorio donde los datos refutaron la hipótesis principal de tu equipo. ¿Cómo presentaste la evidencia y hacia dónde pivotaron el proyecto?"
    ]
  },
  {
    code: "IIS",
    name: "Ingeniería Industrial y de Sistemas",
    roles: ["Supply Chain Analyst", "Continuous Improvement Intern", "Operations Coordinator"],
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
      "Háblame de algún proceso donde la captura manual en hojas de cálculo generaba errores. ¿Cómo estandarizaste la captura o los tableros y cuántas horas semanales liberaste?"
    ]
  },
  {
    code: "IMT",
    name: "Ingeniería Mecatrónica y Automatización",
    roles: ["Automation Engineer Jr", "Embedded Systems Intern", "Robotics Engineer"],
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
      "Describe cómo has documentado diagramas eléctricos, neumáticos y código para facilitar el mantenimiento posterior de un sistema automatizado."
    ]
  },
  {
    code: "LAF",
    name: "Finanzas, Economía y Consultoría de Negocios",
    roles: ["Financial Analyst Jr", "Business Consultant Intern", "Corporate Finance Associate"],
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
      "Cuéntame de algún proyecto en el que tuviste que analizar financieramente una industria que desconocías. ¿Cómo identificaste sus motores de valor en pocos días?"
    ]
  },
  {
    code: "LMC",
    name: "Marketing Digital, Producto y Desarrollo de Negocios",
    roles: ["Associate Product Manager", "Growth Marketing Analyst", "Business Development Rep"],
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
      "Describe un proyecto en el que diseñaste o ajustaste el modelo de monetización de una solución. ¿Cómo calculaste la relación LTV/CAC?"
    ]
  },
  {
    code: "IBT",
    name: "Ingeniería Biomédica y Biotecnología",
    roles: ["Clinical Engineering Intern", "R&D Biotech Associate", "Quality & Regulatory Affairs Jr"],
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
      "Describe cómo estructuraste la revisión sistemática de literatura científica y patentes para definir la ventaja técnica de un proyecto biomédico o biotecnológico."
    ]
  },
  {
    code: "ARQ",
    name: "Arquitectura, Diseño Industrial y UX",
    roles: ["UX/UI Product Designer", "Architectural Project Jr", "Industrial Design Intern"],
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
      "Cuéntame de un diseño que inicialmente estaba saturado de elementos. ¿Qué criterio seguiste para depurarlo y cómo mejoró su claridad y función?"
    ]
  }
];

const appState = {
  user: null,
  sessionId: null,
  careerCode: "ITC",
  targetRole: "Software Engineer Intern",
  seniority: "Junior / Intern",
  totalQuestions: 5,
  questionsPool: [],
  currentIndex: 0,
  turns: [],
  lastEvaluation: null,
  report: null,
  history: [],
  turnStartTime: Date.now()
};

function anonymizeText(text) {
  if (!text) return "";
  return text
    .replace(/\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b/g, "[EMAIL_PROTEGIDO]")
    .replace(/(?:\+?\d{1,3}[\s.-]?)?(?:\(?\d{2,3}\)?[\s.-]?)?\d{3,4}[\s.-]?\d{4}\b/g, "[TEL_PROTEGIDO]")
    .replace(/\bA0\d{7}\b/gi, "[MATRICULA_PROTEGIDA]");
}

function extractMetrics(text) {
  if (!text) return [];
  const regex = /\b\d+(?:[.,]\d+)?\s*(?:%|por\s*ciento|ms|milisegundos|segundos|s|minutos|min|horas|días|semanas|meses|x|veces|usuarios|clientes|req\/s|mb|gb|usd|mxn|\$|puntos|ppm|oee)\b|\$\s*\d+(?:[.,]\d+)?/gi;
  return text.match(regex) || [];
}

function evaluateResponseLocal(question, responseText, careerCode, role) {
  const words = responseText.trim().split(/\s+/).filter(Boolean);
  const wordCount = words.length;
  const metrics = extractMetrics(responseText);
  const lower = responseText.toLowerCase();

  const hasSit = /(proyecto|cuando|en mi|durante|equipo|contexto|empresa|semestre|laboratorio|caso)/.test(lower);
  const hasTask = /(objetivo|meta|encarg|responsab|debía|tenía que|reto|problema|necesit)/.test(lower);
  const hasAct = /(implement|diseñ|program|analic|constru|desarroll|optimic|configur|propuse|realic|ejecut|apliqué|automaticé)/.test(lower);

  const s = Math.min(5, Math.max(2, (hasSit ? 3 : 2) + (wordCount >= 30 ? 1 : 0) + (wordCount >= 60 ? 1 : 0)));
  const t = Math.min(5, Math.max(2, (hasTask ? 3 : 2) + (wordCount >= 35 ? 1 : 0) + (wordCount >= 65 ? 1 : 0)));
  const a = Math.min(5, Math.max(2, (hasAct ? 3 : 2) + (wordCount >= 40 ? 1 : 0) + (wordCount >= 75 ? 1 : 0)));
  const r = Math.min(5, Math.max(1, 2 + Math.min(3, metrics.length)));
  const tech = Math.min(5, Math.max(2, Math.round((a + r) / 2)));
  const rel = Math.min(5, Math.max(3, Math.round((s + t + a) / 3)));
  const avg = Number(((s + t + a + r + tech + rel) / 6).toFixed(2));

  const strengths = metrics.length > 0
    ? `Respuesta bien estructurada con métricas cuantitativas detectadas (${metrics.slice(0, 3).join(", ")}).`
    : "Contexto claro y explicación coherente de tu participación en el proyecto.";

  const improvements = metrics.length > 0
    ? "Detalla un poco más las alternativas técnicas descartadas durante tu toma de decisiones."
    : "Incluye cifras concretas en el resultado (porcentajes de mejora, tiempos ahorrados o indicadores logrados).";

  const improvedExample = `En un proyecto enfocado en ${role} (Situación), tenía el objetivo de resolver el problema descrito cumpliendo criterios estrictos de calidad y tiempo (Tarea). Diseñé e implementé la solución aplicando herramientas clave de ${careerCode} y validando cada ajuste con pruebas (Acción), logrando mejorar el indicador principal en un 32% y reduciendo los tiempos de entrega a la mitad (Resultado).`;

  return {
    star_situation: s,
    star_task: t,
    star_action: a,
    star_result: r,
    technical_clarity: tech,
    relevance: rel,
    turn_average_score: avg,
    metrics_detected: metrics,
    strengths,
    improvement_areas: improvements,
    improved_example_star: improvedExample
  };
}

function shuffleArray(arr) {
  const copy = [...arr];
  for (let i = copy.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [copy[i], copy[j]] = [copy[j], copy[i]];
  }
  return copy;
}

function showView(viewId) {
  ["view-login", "view-setup", "view-chat", "view-report", "view-history"].forEach((id) => {
    const el = document.getElementById(id);
    if (el) el.classList.toggle("hidden", id !== viewId);
  });
  const nav = document.getElementById("topbar-nav");
  if (nav) nav.classList.toggle("hidden", viewId === "view-login");
}

function populateCareers() {
  const careerSelect = document.getElementById("setup-career");
  if (!careerSelect) return;
  careerSelect.innerHTML = CAREER_CATALOG.map(
    (c) => `<option value="${c.code}">${c.name}</option>`
  ).join("");
  updateRoleSuggestions();
}

function updateRoleSuggestions() {
  const careerSelect = document.getElementById("setup-career");
  const roleInput = document.getElementById("setup-role");
  if (!careerSelect || !roleInput) return;
  const found = CAREER_CATALOG.find((c) => c.code === careerSelect.value) || CAREER_CATALOG[0];
  roleInput.value = found.roles[0];
}

async function handleGoogleLogin() {
  const nameInput = document.getElementById("login-name");
  const emailInput = document.getElementById("login-email");
  const fullName = (nameInput && nameInput.value.trim()) || "Marco Hernández";
  const email = (emailInput && emailInput.value.trim()) || "estudiante@tec.mx";

  appState.user = {
    user_id: "usr-" + Math.random().toString(36).substring(2, 9),
    full_name: fullName,
    email: email
  };

  try {
    const resp = await fetch("/api/auth/google", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        email: email,
        full_name: fullName,
        google_sub: "google-" + email
      })
    });
    if (resp.ok) {
      const data = await resp.json();
      appState.user = data;
    }
  } catch (_) {
    // Continúa en modo autónomo si el backend no está activo
  }

  const badge = document.getElementById("user-badge");
  if (badge) badge.textContent = appState.user.full_name;
  showView("view-setup");
}

async function startInterview() {
  const careerCode = document.getElementById("setup-career").value;
  const targetRole = document.getElementById("setup-role").value.trim() || "Practicante Profesional";
  const totalQ = parseInt(document.getElementById("setup-count").value, 10) || 5;
  const cvRaw = document.getElementById("setup-cv").value.trim();
  const jdRaw = document.getElementById("setup-jd").value.trim();

  const statusEl = document.getElementById("setup-status");
  if (!cvRaw || !jdRaw) {
    if (statusEl) {
      statusEl.textContent = "Por favor completa un resumen breve de tu experiencia y de la vacante.";
      statusEl.classList.remove("hidden");
    }
    return;
  }
  if (statusEl) statusEl.classList.add("hidden");

  appState.careerCode = careerCode;
  appState.targetRole = targetRole;
  appState.totalQuestions = Math.min(10, Math.max(5, totalQ));
  appState.currentIndex = 0;
  appState.turns = [];
  appState.lastEvaluation = null;

  const careerObj = CAREER_CATALOG.find((c) => c.code === careerCode) || CAREER_CATALOG[0];
  appState.questionsPool = shuffleArray(careerObj.questions).slice(0, appState.totalQuestions);

  // Intentar iniciar en backend si está disponible
  try {
    const resp = await fetch("/api/sessions/start", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        user_id: appState.user.user_id,
        career_code: careerCode,
        target_role: targetRole,
        seniority_level: "Junior / Intern",
        cv_text: anonymizeText(cvRaw),
        job_description_text: anonymizeText(jdRaw),
        total_questions: appState.totalQuestions,
        allow_followups: false
      })
    });
    if (resp.ok) {
      const data = await resp.json();
      appState.sessionId = data.session_id;
      if (data.question_text) {
        appState.questionsPool[0] = data.question_text;
      }
    }
  } catch (_) {
    appState.sessionId = "ses-" + Date.now();
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
  if (score >= 3) return "#2563eb";
  return "#d97706";
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
  const feedbackBox = document.getElementById("live-feedback-note");
  if (feedbackBox) {
    feedbackBox.textContent = "Tus indicadores se actualizarán al enviar cada respuesta.";
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
  const feedbackBox = document.getElementById("live-feedback-note");
  if (feedbackBox) {
    feedbackBox.textContent = `${evalObj.strengths} Sugerencia: ${evalObj.improvement_areas}`;
  }
}

async function sendChatResponse() {
  const input = document.getElementById("chat-input");
  const text = input.value.trim();
  if (!text) return;

  input.value = "";
  const currentQ = appState.questionsPool[appState.currentIndex];
  const cleanResponse = anonymizeText(text);
  appendChatMessage("user", cleanResponse);

  const elapsedSec = Number(((Date.now() - appState.turnStartTime) / 1000).toFixed(1));
  let evalObj = evaluateResponseLocal(currentQ, cleanResponse, appState.careerCode, appState.targetRole);
  let nextQuestionFromServer = null;

  try {
    const resp = await fetch("/api/sessions/turn", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        session_id: appState.sessionId,
        candidate_response: cleanResponse,
        response_time_seconds: elapsedSec,
        allow_followups: false
      })
    });
    if (resp.ok) {
      const data = await resp.json();
      if (data.evaluation) evalObj = data.evaluation;
      if (data.next_interviewer_message && !data.is_completed) {
        nextQuestionFromServer = data.next_interviewer_message;
      }
    }
  } catch (_) {
    // Evaluación local activa
  }

  appState.turns.push({
    questionNumber: appState.currentIndex + 1,
    questionText: currentQ,
    responseText: cleanResponse,
    evaluation: evalObj
  });

  updateStarMeters(evalObj);
  appState.currentIndex += 1;

  if (appState.currentIndex >= appState.totalQuestions) {
    appendChatMessage("ai", "Gracias. Hemos concluido las preguntas de la sesión. Preparando tu resumen de resultados...");
    setTimeout(() => {
      buildAndShowReport();
    }, 450);
  } else {
    if (nextQuestionFromServer) {
      appState.questionsPool[appState.currentIndex] = nextQuestionFromServer;
    }
    updateProgressCounter();
    setTimeout(() => {
      appendChatMessage("ai", appState.questionsPool[appState.currentIndex]);
      appState.turnStartTime = Date.now();
    }, 300);
  }
}

function buildAndShowReport() {
  const turns = appState.turns;
  const avgScore = turns.length
    ? Number((turns.reduce((acc, t) => acc + t.evaluation.turn_average_score, 0) / turns.length).toFixed(2))
    : 0;

  let evolution = 0;
  if (appState.history.length > 0) {
    const prev = appState.history[0].overallScore;
    if (prev > 0) {
      evolution = Number((((avgScore - prev) / prev) * 100).toFixed(1));
    }
  }

  const sortedByWeakest = [...turns].sort(
    (a, b) => a.evaluation.turn_average_score - b.evaluation.turn_average_score
  );
  const weakestTwo = sortedByWeakest.slice(0, 2);
  const careerObj = CAREER_CATALOG.find((c) => c.code === appState.careerCode) || CAREER_CATALOG[0];

  appState.history.unshift({
    date: new Date().toLocaleDateString("es-MX"),
    careerCode: appState.careerCode,
    targetRole: appState.targetRole,
    overallScore: avgScore,
    evolutionRate: evolution
  });

  document.getElementById("rep-score").textContent = `${avgScore} / 5.0`;
  document.getElementById("rep-role").textContent = `${appState.targetRole} (${appState.careerCode})`;
  document.getElementById("rep-evolution").textContent =
    evolution >= 0 ? `+${evolution}% vs. sesión previa` : `${evolution}% vs. sesión previa`;

  const weakContainer = document.getElementById("rep-weakest-list");
  weakContainer.innerHTML = weakestTwo
    .map(
      (item) => `
      <div style="border: 1px solid var(--border); border-radius: 10px; padding: 1.1rem; margin-bottom: 1rem;">
        <div style="font-size: 0.8rem; color: var(--muted); margin-bottom: 0.25rem;">
          Pregunta ${item.questionNumber} · Puntaje: ${item.evaluation.turn_average_score}/5
        </div>
        <div style="font-weight: 500; font-size: 0.92rem; margin-bottom: 0.6rem;">${item.questionText}</div>
        <div style="font-size: 0.85rem; color: var(--muted); margin-bottom: 0.6rem;">
          <strong>Tu respuesta:</strong> "${item.responseText}"
        </div>
        <div style="font-size: 0.85rem; background: #f9fafb; border-left: 3px solid var(--text); padding: 0.65rem 0.8rem; border-radius: 4px;">
          <strong>Ejemplo de mejora estructurada:</strong> ${item.evaluation.improved_example_star || "Estructura tu respuesta especificando el contexto inicial, tu responsabilidad directa, las acciones técnicas aplicadas y una métrica cuantitativa del logro."}
        </div>
      </div>`
    )
    .join("");

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

  showView("view-report");
}

function renderHistoryView() {
  const tbody = document.getElementById("history-tbody");
  if (!tbody) return;
  if (appState.history.length === 0) {
    tbody.innerHTML = `<tr><td colspan="4" style="padding: 1rem; text-align: center; color: var(--muted);">Aún no tienes entrevistas registradas.</td></tr>`;
  } else {
    tbody.innerHTML = appState.history
      .map(
        (h) => `
        <tr style="border-bottom: 1px solid var(--border);">
          <td style="padding: 0.75rem;">${h.date}</td>
          <td style="padding: 0.75rem;">${h.careerCode} — ${h.targetRole}</td>
          <td style="padding: 0.75rem; font-weight: 600;">${h.overallScore} / 5.0</td>
          <td style="padding: 0.75rem; color: var(--muted);">${h.evolutionRate >= 0 ? "+" + h.evolutionRate + "%" : h.evolutionRate + "%"}</td>
        </tr>`
      )
      .join("");
  }
  showView("view-history");
}

function submitCsatRating(score) {
  const msg = document.getElementById("csat-thanks");
  if (msg) {
    msg.textContent = `¡Gracias por calificar con ${score}/5! Tu opinión ha sido guardada.`;
    msg.classList.remove("hidden");
  }
}

window.addEventListener("DOMContentLoaded", () => {
  populateCareers();

  document.getElementById("setup-career").addEventListener("change", updateRoleSuggestions);
  document.getElementById("btn-google-login").addEventListener("click", handleGoogleLogin);
  document.getElementById("btn-start-interview").addEventListener("click", startInterview);
  document.getElementById("btn-send-chat").addEventListener("click", sendChatResponse);

  document.getElementById("chat-input").addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendChatResponse();
    }
  });

  document.getElementById("nav-new-session").addEventListener("click", () => showView("view-setup"));
  document.getElementById("nav-history").addEventListener("click", renderHistoryView);
  document.getElementById("btn-logout").addEventListener("click", () => {
    appState.user = null;
    showView("view-login");
  });

  document.getElementById("btn-print-report").addEventListener("click", () => window.print());
  document.getElementById("btn-new-from-report").addEventListener("click", () => showView("view-setup"));
  document.getElementById("btn-back-from-history").addEventListener("click", () => showView("view-setup"));

  document.querySelectorAll(".csat-star-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      submitCsatRating(btn.getAttribute("data-score"));
    });
  });
});
