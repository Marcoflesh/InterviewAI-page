import json
import re
import time
from typing import Any, Dict, List, Optional
import httpx
from app.config import settings
from app.agents.state import InterviewGraphState

# =============================================================================
# PROMPT DEL AGENTE EVALUADOR CRÍTICO (Escala 0 a 5 — Cero Complacencia)
# Modelos soportados: gemini-3.8-flash (Google Gemini) y gpt-4o-mini (OpenAI)
# =============================================================================
EVALUATOR_SYSTEM_PROMPT = """Eres el Agente Evaluador Senior (LLM-as-a-Judge) de InterviewAI.
Tu función es evaluar de forma crítica, objetiva y rigurosa la respuesta del candidato frente a la pregunta planteada y el contexto de la vacante.
ESTÁ ESTRICTAMENTE PROHIBIDO ser complaciente, condescendiente o regalar puntos.

ESCALA ESTRICTA DE 0 A 5 POR DIMENSIÓN:
- 0 (Nulo / Inexistente / Tontería): No demuestra la habilidad en absoluto, la respuesta es evasiva ("no sé", "nada"), incoherente, broma, o ignora por completo esta dimensión.
- 1 (Muy Deficiente): Mención vaga de una línea sin sustento técnico ni relación clara con el problema.
- 2 (Insuficiente / Superficial): Idea general comprensible pero ambigua, sin detallar el reto real, sin acciones concretas propias o sin ningún resultado verificable.
- 3 (Aceptable / Estándar): Cumple con explicar el punto de forma coherente y pertinente a la vacante, aunque con alcance moderado o métricas parciales.
- 4 (Sólido / Bien Desarrollado): Explicación clara, estructurada, técnicamente precisa y directamente alineada con la pregunta y el contexto de la vacante.
- 5 (Sobresaliente): Dominio total; detalla contexto complejo, responsabilidad crítica, ejecución técnica rigurosa en primera persona e impacto cuantificado (antes/después, %, tiempos, ahorros o indicadores clave).

DIMENSIONES A CALIFICAR (enteros de 0 a 5):
1. star_situation (0-5): Contexto del proyecto, escenario real y problema inicial.
2. star_task (0-5): Objetivo técnico, restricción, meta o responsabilidad asignada al candidato.
3. star_action (0-5): Pasos técnicos/metodológicos ejecutados por el candidato (decisiones, herramientas y ejecución).
4. star_result (0-5): Desenlace real e impacto medible (cualitativo claro = máx 3; con métricas cuantitativas verificables = 4 o 5; sin resultado = 0).
5. technical_clarity (0-5): Rigor conceptual, precisión terminológica y estructura lógica de la explicación.
6. relevance (0-5): Alineación directa con lo que exige la pregunta actual y el contexto de la vacante.

Devuelve ÚNICAMENTE un objeto JSON válido con estas llaves exactas:
{
  "star_situation": int,
  "star_task": int,
  "star_action": int,
  "star_result": int,
  "technical_clarity": int,
  "relevance": int,
  "strengths": "Análisis crítico y objetivo de los puntos bien fundamentados (o indicar directamente si no hubo ninguno)",
  "improvement_areas": "Retroalimentación concisa y accionable señalando exactamente qué carencias técnicas o estructurales tuvo la respuesta"
}"""

STOPWORDS_ES = {
    "sobre", "como", "para", "este", "esta", "estos", "estas", "donde", "cuando",
    "cual", "cuales", "quien", "porque", "algun", "alguna", "proyecto", "ocasion",
    "situacion", "cuentame", "describe", "platicame", "hablame", "recuerda", "relata",
    "comparte", "tuviste", "hiciste", "lograste", "obtuviste", "equipo", "trabajo",
    "entre", "desde", "hasta", "ante", "bajo", "tras", "durante", "mediante", "pero",
    "mas", "menos", "muy", "todo", "toda", "todos", "todas", "otro", "otra",
}

CAREER_LEXICONS: Dict[str, List[str]] = {
    "ITC": [
        "api", "rest", "graphql", "sql", "postgres", "mysql", "mongo", "base de datos", "indice",
        "query", "consulta", "latencia", "cache", "redis", "docker", "contenedor", "kubernetes",
        "git", "rama", "merge", "pull request", "test", "prueba", "unitario", "integracion",
        "ci/cd", "pipeline", "backend", "frontend", "react", "angular", "vue", "python", "fastapi",
        "django", "flask", "node", "java", "c++", "arquitectura", "microservicio", "monolito",
        "autenticacion", "oauth", "jwt", "seguridad", "endpoint", "bug", "error", "debug", "logs",
        "memoria", "ram", "cpu", "algoritmo", "complejidad", "asincrono", "concurrencia", "hilo",
        "esquema", "migracion", "css", "html", "javascript", "typescript", "servidor", "nube", "aws",
    ],
    "ISD": [
        "dataset", "datos", "modelo", "entrenamiento", "validacion", "overfitting", "sobreajuste",
        "regularizacion", "f1", "auc", "roc", "precision", "recall", "exactitud", "rmse", "mae",
        "mape", "regresion", "clasificacion", "clustering", "segmentacion", "feature", "variable",
        "pipeline", "etl", "sql", "python", "pandas", "numpy", "scikit", "pytorch", "tensorflow",
        "llm", "prompt", "agente", "langgraph", "json", "sesgo", "anonimizacion", "correlacion",
        "hipotesis", "estadistica", "series de tiempo", "estacionalidad", "drift", "baseline",
        "smote", "desbalance", "tablero", "dashboard", "kpi", "distribucion", "outliers", "nulos",
    ],
    "IIS": [
        "vsm", "mapa de valor", "tiempo de ciclo", "takt", "cuello de botella", "balanceo", "linea",
        "5s", "kaizen", "lean", "six sigma", "ishikawa", "pareto", "causa raiz", "merma", "defecto",
        "retrabajo", "calidad", "oee", "smed", "tpm", "mantenimiento", "inventario", "abc", "eoq",
        "reorden", "stock", "almacen", "picking", "packing", "otif", "sla", "logistica", "ruta",
        "transporte", "layout", "planta", "estacion", "ergonomia", "seguridad", "sop", "estandar",
        "simulacion", "capacidad", "productividad", "eficiencia", "roi", "costo", "cpk", "control",
    ],
    "IMT": [
        "plc", "ladder", "microcontrolador", "arduino", "esp32", "stm32", "raspberry", "sensor",
        "actuador", "motor", "servomotor", "paso a paso", "pid", "lazo cerrado", "control",
        "sobreimpulso", "pwm", "adc", "ruido", "filtro", "osciloscopio", "multimetro", "senal",
        "cad", "solidworks", "inventor", "cnc", "impresion 3d", "tolerancia", "mecanismo", "pcb",
        "circuito", "potencia", "rele", "transistor", "interrupcion", "isr", "rtos", "firmware",
        "i2c", "spi", "uart", "can", "modbus", "mqtt", "vision", "camara", "cinematica", "robot",
        "torque", "neumatico", "hidraulico", "valvula", "hmi", "scada",
    ],
    "LAF": [
        "dcf", "flujo de caja", "flujo de efectivo", "wacc", "tasa de descuento", "vpn", "van",
        "tir", "retorno", "ebitda", "margen", "utilidad", "rentabilidad", "presupuesto", "variacion",
        "opex", "capex", "costo", "gasto", "liquidez", "solvencia", "apalancamiento", "deuda",
        "riesgo", "var", "beta", "portafolio", "cartera", "credito", "mece", "consultoria",
        "capital de trabajo", "cuentas por cobrar", "cuentas por pagar", "punto de equilibrio",
        "precio", "pricing", "elasticidad", "multiplos", "valuacion", "cobertura", "hedging",
        "tipo de cambio", "inflacion", "tasa de interes", "estado financiero", "balance", "roi",
    ],
    "LMC": [
        "embudo", "funnel", "conversion", "cac", "ltv", "roas", "roi", "ctr", "cpc", "retencion",
        "churn", "abandono", "cohorte", "a/b", "experimento", "hipotesis", "roadmap", "priorizacion",
        "rice", "moscow", "producto", "mvp", "usuario", "cliente", "entrevista", "encuesta",
        "insight", "icp", "segmentacion", "target", "go-to-market", "lanzamiento", "campaña",
        "seo", "sem", "organico", "pauta", "contenido", "crm", "email", "onboarding", "activacion",
        "nps", "csat", "posicionamiento", "benchmarking", "competencia", "b2b", "leads", "ventas",
        "arpu", "monetizacion", "suscripcion", "landing",
    ],
    "IBT": [
        "protocolo", "ensayo", "experimento", "laboratorio", "control", "reproducibilidad",
        "desviacion", "variabilidad", "calibracion", "sensor", "senal", "ecg", "emg", "oximetria",
        "ruido", "filtrado", "iso 13485", "iso 14971", "iec 60601", "amef", "riesgo", "regulatorio",
        "cofepris", "fda", "norma", "anova", "t-student", "p-valor", "estadistica", "clinico",
        "paciente", "medico", "hospital", "bioproceso", "fermentacion", "cultivo", "biorreactor",
        "enzima", "ph", "temperatura", "mantenimiento", "bioetica", "anonimizacion", "biomaterial",
        "sensibilidad", "especificidad", "imagen medica", "pcr", "molecular", "cadena de frio",
    ],
    "ARQ": [
        "usabilidad", "usuario", "ux", "ui", "interfaz", "prototipo", "wireframe", "maqueta",
        "iteracion", "prueba", "presupuesto", "costo", "material", "constructivo", "manufactura",
        "bim", "revit", "autocad", "rhino", "sketchup", "figma", "sistema de diseño", "componente",
        "libreria", "bioclimatico", "ventilacion", "asoleamiento", "iluminacion", "termico",
        "sustentable", "energia", "estructural", "instalaciones", "mep", "cruce", "accesibilidad",
        "ergonomia", "antropometria", "normativa", "plano", "ejecutivo", "detalle", "especificacion",
        "espacio", "circulacion", "zonificacion", "flujo", "jerarquia", "taller", "obra",
    ],
}


def _normalize(text: str) -> str:
    import unicodedata
    s = (text or "").lower()
    return "".join(
        c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn"
    )


def _extract_keywords(text: str) -> List[str]:
    norm = _normalize(text)
    words = re.findall(r"[a-z0-9]{4,}", norm)
    return [w for w in words if w not in STOPWORDS_ES]


def _critical_star_analyzer(
    question_text: str,
    vacancy_context: str,
    response_text: str,
    career_code: str,
    target_role: str,
    aux: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Evaluador determinista crítico (escala 0 a 5):
    - Otorga 0/5 si la respuesta es incoherente, evasiva, broma o carece por completo de la habilidad.
    - Reconoce un amplio espectro de vocabulario profesional y técnico para premiar con 4/5 y 5/5
      las respuestas bien estructuradas sin castigar injustamente por sinónimos.
    """
    clean = (response_text or "").strip()
    norm = _normalize(clean)
    words = re.findall(r"[a-z0-9]+", norm)
    word_count = len(words)
    unique_words = len(set(words))
    metrics_list: List[str] = list(aux.get("detected_metrics_list", []))
    metrics_count = len(metrics_list)

    # 1. Filtro implacable contra respuestas sin sentido, evasivas o ruido (Calificación = 0)
    nonsense_regex = re.compile(
        r"^(no\s*se|ningun[oa]?|nada|paso|hola|test|prueba|asdf\w*|qwerty\w*|ok|bien|si|no|x+|jaja\w*|lol|wtf|cualquier\s*cosa|sin\s*comentarios|todo\s*bien|nose)$"
    )
    # Detectar repetición artificial de las mismas palabras o teclas
    lexical_diversity = unique_words / max(1, word_count)
    if (
        word_count < 6
        or unique_words < 5
        or nonsense_regex.match(norm)
        or (word_count >= 10 and lexical_diversity < 0.30)
    ):
        return {
            "star_situation": 0,
            "star_task": 0,
            "star_action": 0,
            "star_result": 0,
            "technical_clarity": 0,
            "relevance": 0,
            "strengths": "Ninguna fortaleza identificada. La respuesta entregada es nula, evasiva o carece de sentido profesional.",
            "improvement_areas": "Retroalimentación: En una entrevista real esta respuesta descarta automáticamente al candidato. Debes estructurar un caso real especificando el contexto del problema (Situación), tu responsabilidad concreta (Tarea), las acciones técnicas que ejecutaste (Acción) y el resultado medible (Resultado).",
        }

    # 2. Pertinencia con la pregunta actual y el contexto de la vacante
    q_keywords = _extract_keywords(f"{question_text} {vacancy_context}")
    matched_q = [
        kw for kw in set(q_keywords) if kw[:4] in norm
    ]
    overlap_ratio = len(matched_q) / max(1, min(10, len(set(q_keywords))))

    # 3. Léxico técnico de la carrera + palabras técnicas del contexto de la vacante
    base_lexicon = CAREER_LEXICONS.get(career_code, CAREER_LEXICONS["ITC"])
    vacancy_terms = [w for w in _extract_keywords(vacancy_context) if len(w) >= 5]
    combined_lexicon = list(set(base_lexicon + vacancy_terms))
    matched_tech = [term for term in combined_lexicon if _normalize(term) in norm]

    # 4. Amplio espectro de marcadores semánticos para Situación, Tarea, Acción y Resultado
    sit_stems = [
        "proyect", "durante", "cuando", "trabaj", "materia", "practic", "laboratori",
        "ocasion", "context", "ocurri", "enfrent", "exist", "teniam", "situacion",
        "anterior", "semestr", "empres", "client", "equi", "area", "sistem", "proces",
        "plataform", "aplicacion", "servicio", "etapa", "inicio", "detect", "identific",
    ]
    task_stems = [
        "objetiv", "tare", "responsab", "debi", "teni", "encarg", "reto", "meta",
        "requer", "necesit", "rol", "cumpl", "proposit", "asign", "resolv", "problem",
        "urgenc", "prioridad", "solicitud", "alcanc", "compromis", "garantiz", "asegur",
        "reducir", "mejorar", "optimizar", "evitar", "lograr",
    ]
    action_stems = [
        "implement", "disen", "program", "desarroll", "analic", "analiz", "constru",
        "optimic", "optimiz", "configur", "propus", "realic", "realiz", "ejecut",
        "apliqu", "automat", "estructur", "revis", "calibr", "model", "negoci",
        "coordin", "investig", "migr", "valid", "estandar", "document", "medi",
        "calcul", "entren", "limpi", "reorganic", "utilic", "utiliz", "cree", "crea",
        "levant", "diagnostic", "correg", "modific", "integr", "despleg", "prob",
        "reemplac", "sustitu", "divid", "prioric", "lider", "establec", "defini",
    ]
    result_stems = [
        "resultad", "logr", "reduj", "reduci", "increment", "aument", "mejor",
        "ahorr", "permit", "final", "consegu", "impact", "paso de", "bajo a",
        "subio a", "cumplim", "obtuv", "disminuy", "elimina", "estabiliz",
        "entreg", "aprob", "satisfaccion", "exito", "gracias a", "con esto",
    ]

    sit_hits = sum(1 for s in sit_stems if s in norm)
    task_hits = sum(1 for s in task_stems if s in norm)
    act_hits = sum(1 for s in action_stems if s in norm)
    res_hits = sum(1 for s in result_stems if s in norm)

    # Si no tiene relación alguna con la pregunta ni léxico técnico ni estructura, cae a 0-1
    if overlap_ratio == 0 and len(matched_tech) == 0 and act_hits == 0:
        return {
            "star_situation": 1 if sit_hits > 0 else 0,
            "star_task": 0,
            "star_action": 0,
            "star_result": 0,
            "technical_clarity": 0,
            "relevance": 0,
            "strengths": "No se identifican argumentos técnicos ni relación con la pregunta planteada.",
            "improvement_areas": "Tu respuesta no aborda el problema de la pregunta ni demuestra competencias técnicas del puesto. Estructura qué ocurrió, qué debías resolver, qué método técnico aplicaste y qué métrica obtuviste.",
        }

    # --- SITUACIÓN (0 a 5) ---
    if sit_hits == 0 and word_count < 15:
        s_score = 0
    elif sit_hits == 1 or word_count < 22:
        s_score = 2 if sit_hits >= 1 else 1
    elif sit_hits == 2 and word_count >= 22:
        s_score = 3
    elif sit_hits >= 3 and word_count >= 32:
        s_score = 4
    else:
        s_score = 3
    if sit_hits >= 4 and word_count >= 45 and overlap_ratio >= 0.25:
        s_score = 5

    # --- TAREA (0 a 5) ---
    if task_hits == 0:
        t_score = 1 if word_count >= 30 else 0
    elif task_hits == 1:
        t_score = 3 if word_count >= 28 else 2
    elif task_hits == 2:
        t_score = 4 if word_count >= 35 else 3
    else:
        t_score = 5 if word_count >= 42 else 4

    # --- ACCIÓN (0 a 5) ---
    if act_hits == 0:
        a_score = 0
    elif act_hits == 1:
        a_score = 3 if len(matched_tech) >= 1 else 2
    elif act_hits == 2:
        a_score = 4 if len(matched_tech) >= 1 else 3
    else:
        a_score = 5 if (len(matched_tech) >= 2 and word_count >= 40) else 4

    # --- RESULTADO (0 a 5) ---
    if res_hits == 0 and metrics_count == 0:
        r_score = 0
    elif res_hits >= 1 and metrics_count == 0:
        r_score = 3 if word_count >= 40 else 2
    elif metrics_count == 1:
        r_score = 4 if res_hits >= 1 else 3
    else:
        r_score = 5 if res_hits >= 1 else 4

    # --- CLARIDAD TÉCNICA (0 a 5) ---
    if len(matched_tech) == 0 and act_hits == 0:
        tech_score = 0
    elif len(matched_tech) == 0:
        tech_score = 2 if word_count >= 35 else 1
    elif len(matched_tech) == 1:
        tech_score = 3
    elif len(matched_tech) == 2:
        tech_score = 4
    else:
        tech_score = 5 if (act_hits >= 2 and word_count >= 40) else 4

    # --- PERTINENCIA (0 a 5) ---
    if overlap_ratio == 0 and len(matched_tech) == 0:
        rel_score = 0
    elif overlap_ratio < 0.15:
        rel_score = 2 if len(matched_tech) >= 1 else 1
    elif overlap_ratio < 0.30:
        rel_score = 3
    elif overlap_ratio < 0.45:
        rel_score = 4
    else:
        rel_score = 5 if word_count >= 35 else 4

    # Retroalimentación crítica, directa y sin adulación
    good_points = []
    if s_score >= 4:
        good_points.append("planteaste un contexto de problema claro (Situación)")
    if t_score >= 4:
        good_points.append("definiste con precisión el objetivo o restricción a resolver (Tarea)")
    if a_score >= 4:
        good_points.append("detallaste acciones técnicas concretas ejecutadas por ti (Acción)")
    if r_score >= 4 and metrics_list:
        good_points.append(f"sustentaste el desenlace con datos cuantitativos ({', '.join(metrics_list[:3])})")
    if tech_score >= 4 and matched_tech:
        good_points.append(f"integraste terminología técnica pertinente ({', '.join(matched_tech[:4])})")

    if good_points:
        strengths = "Aspectos bien logrados: " + "; ".join(good_points) + "."
    elif max(s_score, t_score, a_score, r_score) >= 3:
        strengths = "La respuesta tiene una idea base comprensible, pero su desarrollo técnico y metodológico es aún parcial."
    else:
        strengths = "La respuesta es superficial y no aporta evidencia suficiente de dominio de la competencia."

    critiques = []
    if rel_score <= 2:
        critiques.append("te desviaste del núcleo de la pregunta o no conectaste con el contexto de la vacante")
    if s_score <= 2:
        critiques.append("omitiste explicar el escenario técnico inicial o la magnitud del problema (Situación)")
    if t_score <= 2:
        critiques.append("no especificaste qué meta, requerimiento o responsabilidad puntual tenías a tu cargo (Tarea)")
    if a_score <= 2:
        critiques.append("hablaste de forma ambigua sin detallar qué pasos técnicos, herramientas o decisiones ejecutaste tú (Acción)")
    if r_score == 0:
        critiques.append("no mencionaste ningún resultado ni desenlace de tus acciones (Resultado = 0/5)")
    elif r_score <= 3 and metrics_count == 0:
        critiques.append("declaraste un resultado subjetivo sin respaldarlo con métricas numéricas (%, tiempos, costos o indicadores)")
    if tech_score <= 2:
        critiques.append(f"faltó rigor técnico y uso de conceptos propios de {career_code}")

    if critiques:
        improvements = "Crítica objetiva: " + "; ".join(critiques) + "."
    else:
        improvements = "Respuesta sólida y bien estructurada en las cuatro dimensiones STAR. Para nivel senior, contrasta brevemente el trade-off técnico frente a otras alternativas."

    return {
        "star_situation": s_score,
        "star_task": t_score,
        "star_action": a_score,
        "star_result": r_score,
        "technical_clarity": tech_score,
        "relevance": rel_score,
        "strengths": strengths,
        "improvement_areas": improvements,
    }


def _call_configured_llm_agent(user_prompt: str) -> Optional[Dict[str, Any]]:
    """
    Invoca al Agente Evaluador usando las llaves API configuradas en `.env`:
    - Si EVALUATOR_PROVIDER="gemini" y GEMINI_API_KEY está configurada -> Usa `gemini-3.8-flash`
      (con fallback automático a `gemini-2.5-flash` si el endpoint regional lo requiere).
    - Si EVALUATOR_PROVIDER="openai" y OPENAI_API_KEY está configurada -> Usa `gpt-4o-mini`.
    - En caso contrario -> Intenta con Ollama local.
    """
    provider = (settings.EVALUATOR_PROVIDER or "gemini").lower()

    # =========================================================================
    # >>> OPCIÓN 1: AGENTE EVALUADOR CON GEMINI 3.8 FLASH (GEMINI_API_KEY EN .env) <<<
    # =========================================================================
    if (
        provider == "gemini"
        and settings.GEMINI_API_KEY
        and not settings.GEMINI_API_KEY.startswith("PON_AQUI")
    ):
        models_to_try = [settings.GEMINI_MODEL or "gemini-3.8-flash", "gemini-2.5-flash"]
        for mdl in models_to_try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{mdl}:generateContent?key={settings.GEMINI_API_KEY}"
            try:
                with httpx.Client(timeout=6.0) as client:
                    resp = client.post(
                        url,
                        json={
                            "systemInstruction": {"parts": [{"text": EVALUATOR_SYSTEM_PROMPT}]},
                            "contents": [{"parts": [{"text": user_prompt}]}],
                            "generationConfig": {
                                "temperature": 0.1,
                                "responseMimeType": "application/json",
                            },
                        },
                    )
                    if resp.status_code == 200:
                        candidates = resp.json().get("candidates", [])
                        if candidates:
                            raw = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "{}")
                            return json.loads(raw)
            except Exception:
                continue

    # =========================================================================
    # >>> OPCIÓN 2: AGENTE EVALUADOR CON GPT-4o MINI (OPENAI_API_KEY EN .env) <<<
    # =========================================================================
    if (
        (provider == "openai" or settings.OPENAI_API_KEY)
        and settings.OPENAI_API_KEY
        and not settings.OPENAI_API_KEY.startswith("PON_AQUI")
    ):
        try:
            with httpx.Client(timeout=6.0) as client:
                resp = client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={"Authorization": f"Bearer {settings.OPENAI_API_KEY}"},
                    json={
                        "model": settings.OPENAI_CHAT_MODEL or "gpt-4o-mini",
                        "messages": [
                            {"role": "system", "content": EVALUATOR_SYSTEM_PROMPT},
                            {"role": "user", "content": user_prompt},
                        ],
                        "response_format": {"type": "json_object"},
                        "temperature": 0.1,
                    },
                )
                if resp.status_code == 200:
                    raw = resp.json()["choices"][0]["message"]["content"]
                    return json.loads(raw)
        except Exception:
            pass

    # =========================================================================
    # >>> OPCIÓN 3: RESPALDO CON OLLAMA LOCAL <<<
    # =========================================================================
    try:
        with httpx.Client(timeout=2.5) as client:
            resp = client.post(
                f"{settings.OLLAMA_BASE_URL}/api/chat",
                json={
                    "model": settings.OLLAMA_MODEL,
                    "messages": [
                        {"role": "system", "content": EVALUATOR_SYSTEM_PROMPT},
                        {"role": "user", "content": user_prompt},
                    ],
                    "format": "json",
                    "stream": False,
                    "options": {"temperature": 0.1},
                },
            )
            if resp.status_code == 200:
                raw = resp.json().get("message", {}).get("content", "{}")
                return json.loads(raw)
    except Exception:
        pass

    return None


def evaluate_candidate_turn_node(state: InterviewGraphState) -> Dict[str, Any]:
    """
    Nodo del Agente Evaluador en LangGraph (Escala 0 a 5).
    """
    start_ts = time.perf_counter()
    aux = state.get("auxiliary_features", {})
    question_text = state.get("current_question_text", "")
    candidate_response = state.get("candidate_response", "")
    career_code = state.get("career_code", "ITC")
    target_role = state.get("target_role", "Practicante")
    vacancy_context = state.get("job_description_text", "")

    user_prompt = (
        f"Carrera: {career_code}\n"
        f"Puesto Objetivo: {target_role} ({state.get('seniority_level')})\n"
        f"Contexto de la Vacante: {vacancy_context[:400]}\n"
        f"Pregunta Actual: {question_text}\n"
        f"Respuesta del Candidato: {candidate_response}\n"
        f"Metadatos Auxiliares Regex: {json.dumps(aux, ensure_ascii=False)}\n"
    )

    eval_data = None
    json_valid = True

    for attempt in range(2):
        try:
            parsed = _call_configured_llm_agent(user_prompt=user_prompt)
            if parsed:
                required = {
                    "star_situation",
                    "star_task",
                    "star_action",
                    "star_result",
                    "technical_clarity",
                    "relevance",
                    "strengths",
                    "improvement_areas",
                }
                if required.issubset(parsed.keys()):
                    eval_data = {
                        "star_situation": max(0, min(5, int(parsed["star_situation"]))),
                        "star_task": max(0, min(5, int(parsed["star_task"]))),
                        "star_action": max(0, min(5, int(parsed["star_action"]))),
                        "star_result": max(0, min(5, int(parsed["star_result"]))),
                        "technical_clarity": max(0, min(5, int(parsed["technical_clarity"]))),
                        "relevance": max(0, min(5, int(parsed["relevance"]))),
                        "strengths": str(parsed["strengths"]),
                        "improvement_areas": str(parsed["improvement_areas"]),
                    }
                    break
        except Exception:
            json_valid = attempt == 0
            continue

    if eval_data is None:
        eval_data = _critical_star_analyzer(
            question_text=question_text,
            vacancy_context=vacancy_context,
            response_text=candidate_response,
            career_code=career_code,
            target_role=target_role,
            aux=aux,
        )

    avg_score = round(
        (
            eval_data["star_situation"]
            + eval_data["star_task"]
            + eval_data["star_action"]
            + eval_data["star_result"]
            + eval_data["technical_clarity"]
            + eval_data["relevance"]
        )
        / 6.0,
        2,
    )
    eval_data["turn_average_score"] = avg_score
    latency_ms = int((time.perf_counter() - start_ts) * 1000)

    return {
        "evaluation_result": eval_data,
        "evaluation_latency_ms": latency_ms,
        "json_format_valid": json_valid,
    }
