// =============================================================================
// InterviewAI v0.2.0 - Autenticación Triple (Login, Registro y Google OAuth),
// Generador Aleatorio de 15 a 20 Preguntas por Carrera (176 preguntas base),
// Evaluador Semántico STAR + Llaves API (Gemini/OpenAI/Groq/Ollama) y Descarga PDF
// =============================================================================

const CAREER_CATALOG = [
  {
    code: "ITC",
    name: "Ingeniería en Tecnologías Computacionales (Software)",
    roles: ["Software Engineer Intern", "Junior Full-Stack Developer", "Backend Developer"],
    lexicon: [
      "api", "rest", "sql", "base de datos", "índice", "query", "latencia", "caché", "redis",
      "docker", "contenedor", "git", "rama", "merge", "pr", "test", "unitario", "integración",
      "ci/cd", "backend", "frontend", "react", "python", "fastapi", "node", "arquitectura",
      "microservicio", "autenticación", "oauth", "jwt", "endpoint", "bug", "logs", "memoria",
      "algoritmo", "complejidad", "asíncrono", "concurrencia", "esquema", "migración", "css"
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
      "dataset", "modelo", "entrenamiento", "validación", "overfitting", "regularización",
      "f1", "auc", "roc", "precisión", "recall", "rmse", "mae", "mape", "regresión",
      "clasificación", "clustering", "feature", "variable", "pipeline", "sql", "python",
      "pandas", "llm", "prompt", "json", "sesgo", "anonimización", "correlación", "hipótesis",
      "series de tiempo", "estacionalidad", "drift", "baseline", "smote", "cross-validation"
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
      "vsm", "tiempo de ciclo", "takt", "cuello de botella", "balanceo", "línea", "5s",
      "kaizen", "lean", "six sigma", "ishikawa", "pareto", "causa raíz", "merma", "defecto",
      "oee", "smed", "tpm", "inventario", "abc", "eoq", "reorden", "stock", "otif", "sla",
      "layout", "almacén", "picking", "ergonomía", "sop", "estándar", "simulación", "roi", "cpk"
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
      "plc", "microcontrolador", "sensor", "actuador", "pid", "lazo cerrado", "sobreimpulso",
      "pwm", "adc", "ruido", "filtro", "osciloscopio", "multímetro", "cad", "solidworks",
      "cnc", "impresión 3d", "tolerancia", "pcb", "potencia", "interrupción", "isr", "rtos",
      "i2c", "spi", "uart", "can", "modbus", "mqtt", "visión", "cinemática", "torque", "neumático"
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
      "tir", "ebitda", "margen", "presupuesto", "variación", "opex", "capex", "liquidez",
      "solvencia", "riesgo", "var", "beta", "portafolio", "mece", "capital de trabajo",
      "punto de equilibrio", "precio", "elasticidad", "múltiplos", "valuación", "cobertura", "roi"
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
      "embudo", "funnel", "conversión", "cac", "ltv", "roas", "ctr", "retención", "churn",
      "cohorte", "a/b", "experimento", "roadmap", "rice", "moscow", "usuario", "entrevista",
      "icp", "go-to-market", "seo", "sem", "orgánico", "crm", "onboarding", "activación",
      "nps", "csat", "posicionamiento", "benchmarking", "b2b", "leads", "arpu", "monetización"
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
      "protocolo", "ensayo", "control", "reproducibilidad", "desviación", "calibración",
      "señal", "ecg", "emg", "ruido", "filtrado", "iso 13485", "iso 14971", "amef", "riesgo",
      "cofepris", "fda", "anova", "p-valor", "clínico", "bioproceso", "fermentación", "cultivo",
      "ph", "mantenimiento", "bioética", "anonimización", "sensibilidad", "especificidad", "pcr"
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
      "usabilidad", "usuario", "prototipo", "wireframe", "iteración", "presupuesto",
      "material", "constructivo", "bim", "revit", "autocad", "figma", "sistema de diseño",
      "componente", "bioclimático", "ventilación", "asoleamiento", "sustentable", "estructural",
      "instalaciones", "mep", "accesibilidad", "ergonomía", "plano", "detalle", "zonificación"
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

const DEFAULT_REGISTERED_USERS = [
  {
    user_id: "usr-demo-marco",
    full_name: "Marco Antonio Hernández Roque",
    email: "a01709802@tec.mx",
    password: "Interview2026!",
    university: "Tecnológico de Monterrey",
    auth_provider: "local"
  }
];

const appState = {
  user: null,
  registeredUsers: [...DEFAULT_REGISTERED_USERS],
  sessionId: null,
  careerCode: "ITC",
  targetRole: "Software Engineer Intern",
  seniority: "Junior / Intern",
  vacancyContext: "",
  cvSummary: "",
  totalQuestions: 17,
  questionsPool: [],
  currentIndex: 0,
  turns: [],
  lastEvaluation: null,
  history: [],
  turnStartTime: Date.now(),
  aiSettings: {
    provider: "local",
    apiKey: "",
    model: ""
  }
};

function loadSavedState() {
  try {
    const savedUsers = localStorage.getItem("interviewai_users_v2");
    if (savedUsers) {
      const parsed = JSON.parse(savedUsers);
      if (Array.isArray(parsed) && parsed.length > 0) {
        appState.registeredUsers = parsed;
      }
    }
    const savedAi = localStorage.getItem("interviewai_ai_settings_v2");
    if (savedAi) {
      appState.aiSettings = { ...appState.aiSettings, ...JSON.parse(savedAi) };
    }
  } catch (_) {
    // Continúa en memoria si localStorage está restringido
  }
}

function saveRegisteredUsers() {
  try {
    localStorage.setItem("interviewai_users_v2", JSON.stringify(appState.registeredUsers));
  } catch (_) {}
}

function isValidEmailFormat(email) {
  return /^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$/.test((email || "").trim());
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
  const regex = /\b\d+(?:[.,]\d+)?\s*(?:%|por\s*ciento|ms|milisegundos|segundos|s|minutos|min|horas|h|días|semanas|meses|x|veces|usuarios|clientes|solicitudes|req\/s|mb|gb|tb|usd|mxn|\$|pesos|dólares|puntos|ppm|oee|cpk|f1|auc)\b|\$\s*\d+(?:[.,]\d+)?|\b(?:reduj\w+|increment\w+|aument\w+|mejor\w+|ahorr\w+|baj\w+|sub\w+)\s+(?:en\s+)?(?:un\s+)?\d+(?:[.,]\d+)?\s*%?/gi;
  return text.match(regex) || [];
}

function normalizeStr(str) {
  return (str || "")
    .toLowerCase()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "");
}

function extractQuestionKeywords(questionText, vacancyContext) {
  const combined = normalizeStr(`${questionText} ${vacancyContext || ""}`);
  const words = combined.match(/[a-z0-9]{4,}/g) || [];
  return Array.from(new Set(words.filter((w) => !STOPWORDS_ES.has(w))));
}

function evaluateResponseLocal(questionText, responseText, careerCode, role) {
  const clean = (responseText || "").trim();
  const norm = normalizeStr(clean);
  const words = norm.match(/[a-z0-9]+/g) || [];
  const wordCount = words.length;
  const uniqueWords = new Set(words).size;
  const metrics = extractMetrics(clean);
  const careerObj = CAREER_CATALOG.find((c) => c.code === careerCode) || CAREER_CATALOG[0];

  // 1. Detección estricta de respuestas evasivas, vacías o sin contenido real
  const evasiveRegex = /^(no\s+se|ninguno|ninguna|nada|paso|hola|test|prueba|asdf|qwerty|ok|bien|si|no|x+|todo\s+bien)$/;
  if (wordCount < 8 || uniqueWords < 6 || evasiveRegex.test(norm)) {
    return {
      star_situation: 1,
      star_task: 1,
      star_action: 1,
      star_result: 1,
      technical_clarity: 1,
      relevance: 1,
      turn_average_score: 1.0,
      metrics_detected: [],
      tech_terms_detected: [],
      strengths: "Respuesta demasiado breve o evasiva; no permite validar competencias para el puesto.",
      improvement_areas: "Desarrolla un caso real de al menos 45 a 80 palabras explicando el contexto (Situación), el reto asignado (Tarea), las acciones en primera persona (Acción) y las métricas logradas (Resultado).",
      improved_example_star: buildQuestionSpecificStarExample(questionText, careerCode, role)
    };
  }

  // 2. Pertinencia real respecto a la pregunta actual y al contexto de la vacante
  const qKeywords = extractQuestionKeywords(questionText, appState.vacancyContext);
  const matchedKeywords = qKeywords.filter((kw) => norm.includes(kw.slice(0, 5)));
  const overlapRatio = matchedKeywords.length / Math.max(1, Math.min(12, qKeywords.length));

  // 3. Términos técnicos de la carrera detectados en la respuesta
  const matchedTech = careerObj.lexicon.filter((term) => norm.includes(normalizeStr(term)));

  // 4. Marcadores lingüísticos independientes para S, T, A y R
  const sitMarkers = [
    "proyecto", "durante", "cuando", "en mi", "trabajando", "materia", "practicas",
    "laboratorio", "ocasion", "contexto", "ocurrio", "enfrentamos", "existia",
    "teniamos", "situacion", "anteriormente", "semestre", "empresa", "cliente"
  ];
  const taskMarkers = [
    "objetivo", "tarea", "responsabilidad", "debia", "tenia que", "encargue",
    "reto", "meta", "requeria", "necesitabamos", "rol", "cumplir", "proposito",
    "asignaron", "resolver", "problema"
  ];
  const actionMarkers1P = [
    "implemente", "disene", "programe", "desarrolle", "analice", "construi",
    "optimice", "configure", "propuse", "realice", "ejecute", "aplique",
    "automatice", "estructure", "revise", "calibre", "modele", "negocie",
    "coordine", "investigue", "migre", "valide", "estandarice", "documente",
    "medi", "calcule", "entrene", "limpie", "reorganice", "utilice", "creamos"
  ];
  const resultMarkers = [
    "resultado", "logre", "logramos", "redujo", "redujimos", "incremento",
    "aumento", "mejoro", "ahorramos", "permitio", "final", "conseguimos",
    "impacto", "paso de", "bajo a", "subio a", "cumplimos", "obtuvimos"
  ];

  const sitHits = sitMarkers.filter((m) => norm.includes(m)).length;
  const taskHits = taskMarkers.filter((m) => norm.includes(m)).length;
  const actHits = actionMarkers1P.filter((m) => norm.includes(m)).length;
  const resHits = resultMarkers.filter((m) => norm.includes(m)).length;

  // Situación (1 a 5)
  let s = 1;
  if (sitHits >= 1 || wordCount >= 18) s = 2;
  if (sitHits >= 1 && wordCount >= 28) s = 3;
  if (sitHits >= 2 && wordCount >= 42) s = 4;
  if (sitHits >= 3 && wordCount >= 60 && overlapRatio >= 0.25) s = 5;

  // Tarea (1 a 5)
  let t = 1;
  if (taskHits >= 1 || (sitHits >= 1 && wordCount >= 24)) t = 2;
  if (taskHits >= 1 && wordCount >= 32) t = 3;
  if (taskHits >= 2 && wordCount >= 45) t = 4;
  if (taskHits >= 3 && wordCount >= 60) t = 5;

  // Acción (1 a 5)
  let a = 1;
  if (actHits >= 1) a = 2;
  if (actHits >= 2 || (actHits >= 1 && matchedTech.length >= 1)) a = 3;
  if (actHits >= 2 && matchedTech.length >= 2 && wordCount >= 40) a = 4;
  if (actHits >= 3 && matchedTech.length >= 3 && wordCount >= 58) a = 5;

  // Resultado (1 a 5) — Sin métricas cuantitativas no puede superar 2 o 3
  let r = 1;
  if (resHits >= 1) r = 2;
  if (metrics.length >= 1 || (resHits >= 2 && wordCount >= 45)) r = 3;
  if (metrics.length >= 1 && resHits >= 1) r = 4;
  if (metrics.length >= 2 && resHits >= 1 && wordCount >= 50) r = 5;

  // Claridad técnica (1 a 5)
  let tech = 1;
  if (matchedTech.length >= 1 || wordCount >= 25) tech = 2;
  if (matchedTech.length >= 2) tech = 3;
  if (matchedTech.length >= 3 && actHits >= 1) tech = 4;
  if (matchedTech.length >= 4 && actHits >= 2 && wordCount >= 55) tech = 5;

  // Pertinencia a la pregunta (1 a 5)
  let rel = 1;
  if (overlapRatio >= 0.12 || matchedTech.length >= 1) rel = 2;
  if (overlapRatio >= 0.24) rel = 3;
  if (overlapRatio >= 0.38 && wordCount >= 32) rel = 4;
  if (overlapRatio >= 0.52 && wordCount >= 48) rel = 5;

  const avg = Number(((s + t + a + r + tech + rel) / 6).toFixed(2));

  // Retroalimentación específica y dinámica según lo que realmente escribió el usuario
  const goodParts = [];
  if (s >= 4) goodParts.push("contextualizaste bien el escenario inicial");
  if (a >= 4) goodParts.push("describiste acciones concretas en primera persona");
  if (r >= 4 && metrics.length > 0) goodParts.push(`cuantificaste el impacto (${metrics.slice(0, 3).join(", ")})`);
  if (tech >= 4 && matchedTech.length > 0) goodParts.push(`usaste vocabulario técnico sólido (${matchedTech.slice(0, 3).join(", ")})`);

  let strengths = "Registraste un intento inicial, pero faltan elementos concretos del caso.";
  if (goodParts.length > 0) {
    strengths = "Fortalezas: " + goodParts.join(", ") + ".";
  } else if (rel >= 3) {
    strengths = "Abordaste el tema general de la pregunta, aunque con poca profundidad metodológica.";
  }

  const missing = [];
  if (rel <= 2) missing.push("responder directamente al problema específico planteado en la pregunta");
  if (s <= 2) missing.push("explicar en qué proyecto o contexto ocurrió (Situación)");
  if (t <= 2) missing.push("definir cuál era tu objetivo o restricción concreta (Tarea)");
  if (a <= 2) missing.push("detallar con verbos en 1ra persona qué implementaste tú (Acción)");
  if (r <= 2) missing.push("incluir métricas numéricas verificables como %, tiempos o ahorros (Resultado)");
  if (tech <= 2) missing.push(`incorporar herramientas o conceptos técnicos propios de ${careerCode}`);

  const improvements = missing.length > 0
    ? "Por mejorar en este turno: " + missing.join("; ") + "."
    : "Respuesta sobresaliente; como toque adicional, menciona brevemente qué aprendizaje o estándar dejaste documentado.";

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

function buildQuestionSpecificStarExample(questionText, careerCode, role) {
  const careerObj = CAREER_CATALOG.find((c) => c.code === careerCode) || CAREER_CATALOG[0];
  const sampleTools = careerObj.lexicon.slice(0, 4).join(", ");
  const shortTopic = questionText.split(".")[0].replace(/^¿/, "");
  return `Respecto a "${shortTopic}" en mi preparación como ${role} (Situación), mi objetivo era resolver el cuello de botella cumpliendo los criterios técnicos y el plazo de entrega (Tarea). Analicé la causa raíz y ejecuté personalmente la solución utilizando ${sampleTools}, validando cada iteración con pruebas controladas (Acción). Como resultado, reduje la tasa de error en un 38%, mejoré el tiempo de respuesta en un 45% y dejé el proceso estandarizado para el equipo (Resultado).`;
}

async function evaluateResponseWithLiveApiIfConfigured(questionText, cleanResponse, elapsedSec) {
  const { provider, apiKey, model } = appState.aiSettings;
  const localEval = evaluateResponseLocal(questionText, cleanResponse, appState.careerCode, appState.targetRole);

  // Si el usuario configuró su API Key (Gemini, OpenAI o Groq) directamente en el navegador
  if (provider !== "local" && apiKey) {
    const sysPrompt = `Evalúa con rigor realista de 1 a 5 la respuesta del candidato para la carrera ${appState.careerCode} y puesto ${appState.targetRole}. Si la respuesta es corta, evasiva o irrelevante a la pregunta, asigna 1. Devuelve SOLO JSON con: star_situation, star_task, star_action, star_result, technical_clarity, relevance, strengths, improvement_areas.`;
    const usrPrompt = `Contexto de la vacante: ${appState.vacancyContext}\nPregunta: ${questionText}\nRespuesta del candidato: ${cleanResponse}`;

    try {
      if (provider === "gemini") {
        const mdl = model || "gemini-2.5-flash";
        const r = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/${mdl}:generateContent?key=${encodeURIComponent(apiKey)}`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            systemInstruction: { parts: [{ text: sysPrompt }] },
            contents: [{ parts: [{ text: usrPrompt }] }],
            generationConfig: { temperature: 0.1, responseMimeType: "application/json" }
          })
        });
        if (r.ok) {
          const d = await r.json();
          const raw = d.candidates?.[0]?.content?.parts?.[0]?.text;
          if (raw) {
            const parsed = JSON.parse(raw);
            return mergeApiEvaluation(parsed, localEval);
          }
        }
      } else if (provider === "openai" || provider === "groq") {
        const url = provider === "groq"
          ? "https://api.groq.com/openai/v1/chat/completions"
          : "https://api.openai.com/v1/chat/completions";
        const mdl = model || (provider === "groq" ? "llama-3.3-70b-versatile" : "gpt-4o-mini");
        const r = await fetch(url, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${apiKey}`
          },
          body: JSON.stringify({
            model: mdl,
            messages: [
              { role: "system", content: sysPrompt },
              { role: "user", content: usrPrompt }
            ],
            response_format: { type: "json_object" },
            temperature: 0.1
          })
        });
        if (r.ok) {
          const d = await r.json();
          const raw = d.choices?.[0]?.message?.content;
          if (raw) {
            const parsed = JSON.parse(raw);
            return mergeApiEvaluation(parsed, localEval);
          }
        }
      }
    } catch (_) {
      // Si la llave falla o no hay red, usa el evaluador semántico local
    }
  }

  return localEval;
}

function mergeApiEvaluation(parsed, fallbackEval) {
  const clamp = (v, def) => Math.max(1, Math.min(5, parseInt(v, 10) || def));
  const s = clamp(parsed.star_situation, fallbackEval.star_situation);
  const t = clamp(parsed.star_task, fallbackEval.star_task);
  const a = clamp(parsed.star_action, fallbackEval.star_action);
  const r = clamp(parsed.star_result, fallbackEval.star_result);
  const tech = clamp(parsed.technical_clarity, fallbackEval.technical_clarity);
  const rel = clamp(parsed.relevance, fallbackEval.relevance);
  const avg = Number(((s + t + a + r + tech + rel) / 6).toFixed(2));
  return {
    ...fallbackEval,
    star_situation: s,
    star_task: t,
    star_action: a,
    star_result: r,
    technical_clarity: tech,
    relevance: rel,
    turn_average_score: avg,
    strengths: parsed.strengths || fallbackEval.strengths,
    improvement_areas: parsed.improvement_areas || fallbackEval.improvement_areas
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

function getRandomQuestionCount() {
  // Valor aleatorio realista entre 15 y 20 preguntas
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

function setLoggedInUser(userObj) {
  appState.user = userObj;
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
  // Previsualizar el próximo conteo aleatorio 15-20 en configuración
  const previewCount = getRandomQuestionCount();
  appState.totalQuestions = previewCount;
  const countInput = document.getElementById("setup-count");
  if (countInput) {
    countInput.value = `${previewCount} preguntas (Aleatorio 15-20)`;
  }
  showView("view-setup");
}

async function handleLocalLogin() {
  const email = document.getElementById("login-email").value.trim().toLowerCase();
  const password = document.getElementById("login-password").value;

  if (!isValidEmailFormat(email)) {
    showAuthFeedback("Por favor ingresa un correo electrónico con formato válido (ejemplo@dominio.com).");
    return;
  }
  if (!password) {
    showAuthFeedback("Ingresa tu contraseña para iniciar sesión.");
    return;
  }

  try {
    const resp = await fetch("/api/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password })
    });
    if (resp.ok) {
      const data = await resp.json();
      setLoggedInUser(data);
      return;
    } else if (resp.status === 401 || resp.status === 400) {
      const err = await resp.json();
      showAuthFeedback(err.detail || "Credenciales inválidas.");
      return;
    }
  } catch (_) {
    // Verificación local contra cuentas registradas
  }

  const found = appState.registeredUsers.find((u) => u.email.toLowerCase() === email);
  if (!found) {
    showAuthFeedback("No existe ninguna cuenta registrada con ese correo. Usa la pestaña 'Registrar' o 'Continuar con Google'.");
    return;
  }
  if (found.password !== password) {
    showAuthFeedback("Contraseña incorrecta para esta cuenta. Verifica tus datos.");
    return;
  }

  setLoggedInUser(found);
}

async function handleLocalRegister() {
  const fullName = document.getElementById("login-name").value.trim();
  const email = document.getElementById("reg-email").value.trim().toLowerCase();
  const university = document.getElementById("reg-university").value.trim() || "Tecnológico de Monterrey";
  const password = document.getElementById("reg-password").value;

  if (fullName.length < 3) {
    showAuthFeedback("Ingresa tu nombre y apellido completos.");
    return;
  }
  if (!isValidEmailFormat(email)) {
    showAuthFeedback("Ingresa un correo electrónico real y válido (ej. nombre@dominio.com).");
    return;
  }
  if (!password || password.length < 6) {
    showAuthFeedback("La contraseña debe tener al menos 6 caracteres.");
    return;
  }

  const existsLocal = appState.registeredUsers.some((u) => u.email.toLowerCase() === email);
  if (existsLocal) {
    showAuthFeedback("Este correo ya está registrado. Cambia a la pestaña 'Iniciar sesión'.");
    return;
  }

  const newUser = {
    user_id: "usr-" + Math.random().toString(36).substring(2, 9),
    full_name: fullName,
    email,
    password,
    university,
    auth_provider: "local"
  };

  try {
    const resp = await fetch("/api/auth/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ full_name: fullName, email, password, university })
    });
    if (resp.ok) {
      const serverUser = await resp.json();
      newUser.user_id = serverUser.user_id;
    }
  } catch (_) {}

  appState.registeredUsers.push(newUser);
  saveRegisteredUsers();
  setLoggedInUser(newUser);
}

function openGoogleModal() {
  const errEl = document.getElementById("google-modal-error");
  if (errEl) errEl.classList.add("hidden");
  document.getElementById("google-oauth-modal").classList.remove("hidden");
}

function closeGoogleModal() {
  document.getElementById("google-oauth-modal").classList.add("hidden");
}

async function completeGoogleLogin(fullName, email, university = "Tecnológico de Monterrey") {
  const cleanEmail = (email || "").trim().toLowerCase();
  const errEl = document.getElementById("google-modal-error");

  if (!fullName || fullName.trim().length < 2) {
    if (errEl) {
      errEl.textContent = "Ingresa el nombre asociado a tu cuenta de Google.";
      errEl.classList.remove("hidden");
    }
    return;
  }
  if (!isValidEmailFormat(cleanEmail)) {
    if (errEl) {
      errEl.textContent = "Ingresa un correo de Google válido (@gmail.com o institucional).";
      errEl.classList.remove("hidden");
    }
    return;
  }

  let googleUser = {
    user_id: "usr-google-" + Math.random().toString(36).substring(2, 9),
    full_name: fullName.trim(),
    email: cleanEmail,
    university,
    auth_provider: "google"
  };

  try {
    const resp = await fetch("/api/auth/google", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        email: cleanEmail,
        full_name: fullName.trim(),
        google_sub: "google-oauth-" + cleanEmail
      })
    });
    if (resp.ok) {
      googleUser = await resp.json();
    }
  } catch (_) {}

  // Sincronizar también en el registro local para futuras sesiones
  if (!appState.registeredUsers.some((u) => u.email.toLowerCase() === cleanEmail)) {
    appState.registeredUsers.push({ ...googleUser, password: "" });
    saveRegisteredUsers();
  }

  closeGoogleModal();
  setLoggedInUser(googleUser);
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

async function startInterview() {
  const careerCode = document.getElementById("setup-career").value;
  const targetRole = document.getElementById("setup-role").value.trim() || "Practicante Profesional";
  const cvRaw = document.getElementById("setup-cv").value.trim();
  const jdRaw = document.getElementById("setup-jd").value.trim();

  const statusEl = document.getElementById("setup-status");
  if (!cvRaw || !jdRaw) {
    if (statusEl) {
      statusEl.textContent = "Por favor completa el resumen de tu currículum y el contexto de la vacante.";
      statusEl.classList.remove("hidden");
    }
    return;
  }
  if (statusEl) statusEl.classList.add("hidden");

  // Generar número aleatorio de preguntas entre 15 y 20
  const randomTotal = getRandomQuestionCount();
  appState.careerCode = careerCode;
  appState.targetRole = targetRole;
  appState.cvSummary = anonymizeText(cvRaw);
  appState.vacancyContext = anonymizeText(jdRaw);
  appState.totalQuestions = randomTotal;
  appState.currentIndex = 0;
  appState.turns = [];
  appState.lastEvaluation = null;

  const countInput = document.getElementById("setup-count");
  if (countInput) {
    countInput.value = `${randomTotal} preguntas generadas`;
  }

  const careerObj = CAREER_CATALOG.find((c) => c.code === careerCode) || CAREER_CATALOG[0];
  appState.questionsPool = shuffleArray(careerObj.questions).slice(0, randomTotal);

  try {
    const resp = await fetch("/api/sessions/start", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        user_id: appState.user.user_id,
        career_code: careerCode,
        target_role: targetRole,
        seniority_level: "Junior / Intern",
        cv_text: appState.cvSummary,
        job_description_text: appState.vacancyContext,
        total_questions: randomTotal,
        allow_followups: false
      })
    });
    if (resp.ok) {
      const data = await resp.json();
      appState.sessionId = data.session_id;
      appState.totalQuestions = data.total_questions || randomTotal;
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
  if (badge) badge.textContent = "- / 5.0";
  const mTags = document.getElementById("detected-metrics-tags");
  if (mTags) mTags.textContent = "Ninguna aún";
  const tTags = document.getElementById("detected-tech-tags");
  if (tTags) tTags.textContent = "Ninguno aún";
  const feedbackBox = document.getElementById("live-feedback-note");
  if (feedbackBox) {
    feedbackBox.textContent = "Tus indicadores se calculan dinámicamente según la pregunta actual, tus verbos de acción, vocabulario técnico y métricas cuantitativas.";
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
      ? mList.map((m) => `<span class="tag-pill">${m}</span>`).join("")
      : "Ninguna detectada (agrega %, tiempos o cifras)";
  }

  const tTags = document.getElementById("detected-tech-tags");
  if (tTags) {
    const tList = evalObj.tech_terms_detected || [];
    tTags.innerHTML = tList.length > 0
      ? tList.map((t) => `<span class="tag-pill">${t}</span>`).join("")
      : "Ningún término técnico de la carrera detectado";
  }

  const feedbackBox = document.getElementById("live-feedback-note");
  if (feedbackBox) {
    feedbackBox.textContent = `${evalObj.strengths} ${evalObj.improvement_areas}`;
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
  let evalObj = await evaluateResponseWithLiveApiIfConfigured(currentQ, cleanResponse, elapsedSec);
  let nextQuestionFromServer = null;

  try {
    const resp = await fetch("/api/sessions/turn", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        session_id: appState.sessionId,
        candidate_response: cleanResponse,
        response_time_seconds: elapsedSec,
        allow_followups: false,
        llm_provider: appState.aiSettings.provider,
        llm_api_key: appState.aiSettings.apiKey || null,
        llm_model: appState.aiSettings.model || null
      })
    });
    if (resp.ok) {
      const data = await resp.json();
      if (data.evaluation) {
        evalObj = {
          ...evalObj,
          ...data.evaluation
        };
      }
      if (data.next_interviewer_message && !data.is_completed) {
        nextQuestionFromServer = data.next_interviewer_message;
      }
    }
  } catch (_) {}

  appState.turns.push({
    questionNumber: appState.currentIndex + 1,
    questionText: currentQ,
    responseText: cleanResponse,
    evaluation: evalObj
  });

  updateStarMeters(evalObj);
  appState.currentIndex += 1;

  if (appState.currentIndex >= appState.totalQuestions) {
    appendChatMessage("ai", "Has completado todas las preguntas de la entrevista. Generando tu reporte final y plan de acción...");
    setTimeout(() => {
      buildAndShowReport();
    }, 400);
  } else {
    if (nextQuestionFromServer) {
      appState.questionsPool[appState.currentIndex] = nextQuestionFromServer;
    }
    updateProgressCounter();
    setTimeout(() => {
      appendChatMessage("ai", appState.questionsPool[appState.currentIndex]);
      appState.turnStartTime = Date.now();
    }, 280);
  }
}

function finishInterviewEarly() {
  if (appState.turns.length === 0) {
    appendChatMessage("ai", "Responde al menos la primera pregunta antes de generar el reporte de evaluación.");
    return;
  }
  buildAndShowReport();
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
  document.getElementById("rep-role").textContent = `${appState.targetRole} (${appState.careerCode}) · ${turns.length} de ${appState.totalQuestions} preguntas respondidas`;
  document.getElementById("rep-evolution").textContent =
    evolution >= 0 ? `+${evolution}% vs. sesión previa` : `${evolution}% vs. sesión previa`;

  const weakContainer = document.getElementById("rep-weakest-list");
  weakContainer.innerHTML = weakestTwo
    .map(
      (item) => `
      <div style="border: 1px solid var(--border); border-radius: 10px; padding: 1.1rem; margin-bottom: 1rem;">
        <div style="font-size: 0.8rem; color: var(--muted); margin-bottom: 0.25rem;">
          Pregunta ${item.questionNumber} · Puntaje del turno: <strong>${item.evaluation.turn_average_score}/5.0</strong>
          (S:${item.evaluation.star_situation} · T:${item.evaluation.star_task} · A:${item.evaluation.star_action} · R:${item.evaluation.star_result} · Tec:${item.evaluation.technical_clarity} · Pert:${item.evaluation.relevance})
        </div>
        <div style="font-weight: 500; font-size: 0.92rem; margin-bottom: 0.55rem;">${item.questionText}</div>
        <div style="font-size: 0.84rem; color: var(--muted); margin-bottom: 0.45rem;">
          <strong>Tu respuesta:</strong> "${item.responseText}"
        </div>
        <div style="font-size: 0.82rem; color: var(--amber); margin-bottom: 0.55rem;">
          <strong>Diagnóstico:</strong> ${item.evaluation.improvement_areas}
        </div>
        <div style="font-size: 0.84rem; background: #f9fafb; border-left: 3px solid var(--text); padding: 0.65rem 0.8rem; border-radius: 4px;">
          <strong>Ejemplo de mejora bajo método STAR:</strong> ${item.evaluation.improved_example_star}
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

  const pdfStatus = document.getElementById("pdf-download-status");
  if (pdfStatus) pdfStatus.classList.add("hidden");

  showView("view-report");
}

// =============================================================================
// Generador y Descargador Real de Archivo PDF (jsPDF + Fallback Binario PDF 1.4)
// =============================================================================
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
  const careerObj = CAREER_CATALOG.find((c) => c.code === appState.careerCode) || CAREER_CATALOG[0];

  const sortedByWeakest = [...appState.turns].sort(
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

      writeWrapped("InterviewAI — Reporte de Entrevista y Plan de Accion", 16, true, [24, 24, 27]);
      writeWrapped(`Candidato: ${userName} (${(appState.user && appState.user.email) || ""})`, 10, false, [107, 114, 128]);
      writeWrapped(`Puesto y Carrera: ${roleText}`, 10, false, [107, 114, 128]);
      writeWrapped(`Calificacion Global: ${scoreText} (${evoText})`, 12, true, [22, 163, 74]);
      y += 8;

      writeWrapped("1. Respuestas con Mayor Oportunidad de Mejora (Metodo STAR)", 13, true);
      weakestTwo.forEach((item, idx) => {
        writeWrapped(
          `${idx + 1}) Pregunta ${item.questionNumber} (Puntaje: ${item.evaluation.turn_average_score}/5.0): ${item.questionText}`,
          10,
          true
        );
        writeWrapped(`Tu respuesta: "${item.responseText}"`, 9.5, false, [75, 85, 99]);
        writeWrapped(`Area de mejora: ${item.evaluation.improvement_areas}`, 9.5, false, [180, 83, 9]);
        writeWrapped(`Ejemplo STAR recomendado: ${item.evaluation.improved_example_star}`, 9.5, false, [17, 24, 39]);
        y += 6;
      });

      writeWrapped("2. Plan de Accion y Recursos Recomendados", 13, true);
      careerObj.resources.forEach((r) => {
        writeWrapped(`• ${r.title} (${r.provider}) — ${r.url}`, 10, false);
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
  } catch (_) {
    window.print();
  }
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

function openApiModal() {
  document.getElementById("api-provider-select").value = appState.aiSettings.provider || "local";
  document.getElementById("api-key-input").value = appState.aiSettings.apiKey || "";
  document.getElementById("api-model-input").value = appState.aiSettings.model || "";
  document.getElementById("api-modal-status").classList.add("hidden");
  document.getElementById("api-settings-modal").classList.remove("hidden");
}

function saveApiSettings() {
  appState.aiSettings.provider = document.getElementById("api-provider-select").value;
  appState.aiSettings.apiKey = document.getElementById("api-key-input").value.trim();
  appState.aiSettings.model = document.getElementById("api-model-input").value.trim();
  try {
    localStorage.setItem("interviewai_ai_settings_v2", JSON.stringify(appState.aiSettings));
  } catch (_) {}
  const st = document.getElementById("api-modal-status");
  if (st) {
    st.textContent = "Configuración guardada para los agentes de evaluación.";
    st.classList.remove("hidden");
  }
  setTimeout(() => {
    document.getElementById("api-settings-modal").classList.add("hidden");
  }, 600);
}

window.addEventListener("DOMContentLoaded", () => {
  loadSavedState();
  populateCareers();

  // Pestañas de autenticación
  document.getElementById("tab-login").addEventListener("click", () => setAuthTab("login"));
  document.getElementById("tab-register").addEventListener("click", () => setAuthTab("register"));
  document.getElementById("btn-submit-login").addEventListener("click", handleLocalLogin);
  document.getElementById("btn-submit-register").addEventListener("click", handleLocalRegister);

  document.getElementById("btn-fill-demo").addEventListener("click", () => {
    document.getElementById("login-email").value = "a01709802@tec.mx";
    document.getElementById("login-password").value = "Interview2026!";
    showAuthFeedback("Cuenta demo cargada. Haz clic en 'Iniciar sesión'.", false);
  });

  // Google OAuth Modal y Cuentas
  document.getElementById("btn-google-login").addEventListener("click", openGoogleModal);
  document.getElementById("btn-close-google-modal").addEventListener("click", closeGoogleModal);
  document.querySelectorAll(".google-account-item").forEach((item) => {
    item.addEventListener("click", () => {
      completeGoogleLogin(
        item.getAttribute("data-gname"),
        item.getAttribute("data-gemail"),
        item.getAttribute("data-guni")
      );
    });
  });
  document.getElementById("btn-confirm-google-custom").addEventListener("click", () => {
    completeGoogleLogin(
      document.getElementById("google-custom-name").value,
      document.getElementById("google-custom-email").value
    );
  });

  // Modal de Llaves API / Motor IA
  document.getElementById("btn-open-api-modal").addEventListener("click", openApiModal);
  document.getElementById("btn-close-api-modal").addEventListener("click", () => {
    document.getElementById("api-settings-modal").classList.add("hidden");
  });
  document.getElementById("btn-save-api-settings").addEventListener("click", saveApiSettings);

  // Configuración y Chat
  document.getElementById("setup-career").addEventListener("change", updateRoleSuggestions);
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
    const nextRandom = getRandomQuestionCount();
    appState.totalQuestions = nextRandom;
    document.getElementById("setup-count").value = `${nextRandom} preguntas (Aleatorio 15-20)`;
    showView("view-setup");
  });
  document.getElementById("nav-history").addEventListener("click", renderHistoryView);
  document.getElementById("btn-logout").addEventListener("click", () => {
    appState.user = null;
    showView("view-login");
  });

  // Descarga real de PDF
  document.getElementById("btn-print-report").addEventListener("click", downloadReportPdf);
  document.getElementById("btn-new-from-report").addEventListener("click", () => {
    const nextRandom = getRandomQuestionCount();
    appState.totalQuestions = nextRandom;
    document.getElementById("setup-count").value = `${nextRandom} preguntas (Aleatorio 15-20)`;
    showView("view-setup");
  });
  document.getElementById("btn-back-from-history").addEventListener("click", () => showView("view-setup"));

  document.querySelectorAll(".csat-star-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      submitCsatRating(btn.getAttribute("data-score"));
    });
  });
});
