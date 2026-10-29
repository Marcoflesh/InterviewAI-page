import json
import re
import time
from typing import Any, Dict, List, Optional
import httpx
from app.config import settings
from app.agents.state import InterviewGraphState

EVALUATOR_SYSTEM_PROMPT = """Eres el Agente Evaluador (LLM-as-a-Judge) de InterviewAI.
Tu tarea es evaluar con rigor realista la respuesta del candidato frente a la pregunta actual, su carrera y el contexto de la vacante.
Reglas de calificación estricta (escala entera de 1 a 5):
- Si la respuesta es evasiva ("no sé", "hola"), irrelevante a la pregunta o tiene menos de 10 palabras, asigna 1 en todas las dimensiones.
- star_situation (1 a 5): ¿Describe un contexto real, proyecto, entorno y problema inicial específico? (1=ausente, 3=mención general, 5=contexto específico y claro).
- star_task (1 a 5): ¿Explica cuál era su responsabilidad concreta, meta, restricción o reto a resolver? (1=ausente, 3=implícito, 5=objetivo y alcance claros).
- star_action (1 a 5): ¿Detalla en primera persona las acciones técnicas y metodológicas que ejecutó directamente? (1=ausente o vago, 3=acciones generales, 5=pasos técnicos precisos y fundamentados).
- star_result (1 a 5): ¿Expone el desenlace real respaldado con métricas cuantitativas verificables (%, tiempos, ahorro, precisión, usuarios)? (1=sin resultado, 2=resultado subjetivo sin números, 4=una métrica clara, 5=impacto cuantificado antes/después).
- technical_clarity (1 a 5): Precisión en el uso de conceptos, herramientas y estándares propios de su carrera.
- relevance (1 a 5): Qué tan directamente responde a la pregunta específica planteada sin divagar.

Devuelve ÚNICAMENTE un objeto JSON válido con estas llaves exactas:
{
  "star_situation": int,
  "star_task": int,
  "star_action": int,
  "star_result": int,
  "technical_clarity": int,
  "relevance": int,
  "strengths": "retroalimentación específica sobre lo que sí hizo bien en esta respuesta",
  "improvement_areas": "retroalimentación accionable indicando qué dimensión STAR o concepto técnico faltó en esta pregunta"
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
        "api", "rest", "sql", "base de datos", "índice", "query", "latencia", "caché", "redis",
        "docker", "contenedor", "git", "rama", "merge", "pr", "test", "unitario", "integración",
        "ci/cd", "backend", "frontend", "react", "python", "fastapi", "node", "arquitectura",
        "microservicio", "autenticación", "oauth", "jwt", "endpoint", "bug", "logs", "memoria",
        "algoritmo", "complejidad", "asíncrono", "concurrencia", "esquema", "migración", "css",
    ],
    "ISD": [
        "dataset", "modelo", "entrenamiento", "validación", "overfitting", "regularización",
        "f1", "auc", "roc", "precisión", "recall", "rmse", "mae", "mape", "regresión",
        "clasificación", "clustering", "feature", "variable", "pipeline", "sql", "python",
        "pandas", "llm", "prompt", "json", "sesgo", "anonimización", "correlación", "hipótesis",
        "series de tiempo", "estacionalidad", "drift", "baseline", "smote", "cross-validation",
    ],
    "IIS": [
        "vsm", "tiempo de ciclo", "takt", "cuello de botella", "balanceo", "línea", "5s",
        "kaizen", "lean", "six sigma", "ishikawa", "pareto", "causa raíz", "merma", "defecto",
        "oee", "smed", "tpm", "inventario", "abc", "eoq", "reorden", "stock", "otif", "sla",
        "layout", "almacén", "picking", "ergonomía", "sop", "estándar", "simulación", "roi", "cpk",
    ],
    "IMT": [
        "plc", "microcontrolador", "sensor", "actuador", "pid", "lazo cerrado", "sobreimpulso",
        "pwm", "adc", "ruido", "filtro", "osciloscopio", "multímetro", "cad", "solidworks",
        "cnc", "impresión 3d", "tolerancia", "pcb", "potencia", "interrupción", "isr", "rtos",
        "i2c", "spi", "uart", "can", "modbus", "mqtt", "visión", "cinemática", "torque", "neumático",
    ],
    "LAF": [
        "dcf", "flujo de caja", "flujo de efectivo", "wacc", "tasa de descuento", "vpn", "van",
        "tir", "ebitda", "margen", "presupuesto", "variación", "opex", "capex", "liquidez",
        "solvencia", "riesgo", "var", "beta", "portafolio", "mece", "capital de trabajo",
        "punto de equilibrio", "precio", "elasticidad", "múltiplos", "valuación", "cobertura", "roi",
    ],
    "LMC": [
        "embudo", "funnel", "conversión", "cac", "ltv", "roas", "ctr", "retención", "churn",
        "cohorte", "a/b", "experimento", "roadmap", "rice", "moscow", "usuario", "entrevista",
        "icp", "go-to-market", "seo", "sem", "orgánico", "crm", "onboarding", "activación",
        "nps", "csat", "posicionamiento", "benchmarking", "b2b", "leads", "arpu", "monetización",
    ],
    "IBT": [
        "protocolo", "ensayo", "control", "reproducibilidad", "desviación", "calibración",
        "señal", "ecg", "emg", "ruido", "filtrado", "iso 13485", "iso 14971", "amef", "riesgo",
        "cofepris", "fda", "anova", "p-valor", "clínico", "bioproceso", "fermentación", "cultivo",
        "ph", "mantenimiento", "bioética", "anonimización", "sensibilidad", "especificidad", "pcr",
    ],
    "ARQ": [
        "usabilidad", "usuario", "prototipo", "wireframe", "iteración", "presupuesto",
        "material", "constructivo", "bim", "revit", "autocad", "figma", "sistema de diseño",
        "componente", "bioclimático", "ventilación", "asoleamiento", "sustentable", "estructural",
        "instalaciones", "mep", "accesibilidad", "ergonomía", "plano", "detalle", "zonificación",
    ],
}


def _extract_question_keywords(question_text: str) -> List[str]:
    words = re.findall(r"[a-záéíóúñü]{4,}", question_text.lower())
    return [w for w in words if w not in STOPWORDS_ES]


def _deep_star_analyzer(
    question_text: str,
    response_text: str,
    career_code: str,
    target_role: str,
    aux: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Analizador semántico y léxico determinista de alta sensibilidad que evalúa:
    1) Detección de respuestas vacías, evasivas o demasiado cortas.
    2) Pertinencia real respecto a los conceptos de la pregunta planteada.
    3) Marcadores lingüísticos independientes para Situación, Tarea, Acción (1ra persona) y Resultado.
    4) Densidad de vocabulario técnico propio de la carrera seleccionada.
    """
    clean = (response_text or "").strip()
    lower = clean.lower()
    words = re.findall(r"[a-záéíóúñü0-9]+", lower)
    word_count = len(words)
    unique_words = len(set(words))
    metrics_list: List[str] = list(aux.get("detected_metrics_list", []))
    metrics_count = len(metrics_list)

    evasive_patterns = re.compile(
        r"^(no\s+s[eé]|ningun[oa]|nada|paso|hola|test|prueba|asdf|qwerty|sin\s+respuesta|ok|bien|x+)$"
    )
    if word_count < 8 or unique_words < 6 or evasive_patterns.match(lower):
        return {
            "star_situation": 1,
            "star_task": 1,
            "star_action": 1,
            "star_result": 1,
            "technical_clarity": 1,
            "relevance": 1,
            "strengths": "Respuesta registrada, pero su extensión o contenido es insuficiente para evaluar competencias.",
            "improvement_areas": "Desarrolla un caso completo de al menos 45 a 80 palabras describiendo el contexto (Situación), tu objetivo (Tarea), qué hiciste paso a paso (Acción) y el impacto medible (Resultado).",
        }

    # 1. Pertinencia respecto a la pregunta actual
    q_keywords = _extract_question_keywords(question_text)
    matched_q_words = [kw for kw in q_keywords if kw[:5] in lower]
    q_overlap_ratio = len(set(matched_q_words)) / max(1, len(set(q_keywords)))

    # 2. Claridad técnica según el léxico de la carrera
    lexicon = CAREER_LEXICONS.get(career_code, CAREER_LEXICONS["ITC"])
    matched_tech_terms = [term for term in lexicon if term in lower]

    # 3. Marcadores independientes por dimensión STAR
    sit_markers = [
        "en el proyecto", "durante", "cuando", "en mi", "trabajando en", "en la materia",
        "en mis prácticas", "en el laboratorio", "en una ocasión", "el contexto", "ocurrió",
        "enfrentamos", "existía", "teníamos un problema", "la situación", "anteriormente",
    ]
    task_markers = [
        "mi objetivo", "mi tarea", "mi responsabilidad", "debía", "tenía que", "me encargué",
        "el reto era", "la meta", "se requería", "necesitábamos lograr", "mi rol consistía",
        "para cumplir", "el propósito", "me asignaron",
    ]
    action_verbs_1p = [
        "implementé", "diseñé", "programé", "desarrollé", "analicé", "construí", "optimicé",
        "configuré", "propuse", "realicé", "ejecuté", "apliqué", "automaticé", "estructuré",
        "revisé", "calibré", "modelé", "negocié", "coordiné", "investigué", "migré", "validé",
        "estandaricé", "documenté", "medí", "calculé", "entrené", "limpié", "reorganicé", "hice",
    ]
    result_markers = [
        "como resultado", "logré", "logramos", "se redujo", "redujimos", "incrementó",
        "aumentó", "mejoró", "ahorramos", "permitió", "al final", "conseguimos", "impactó",
        "pasó de", "bajó a", "subió a", "cumplimos", "obtuvimos", "se logró",
    ]

    sit_hits = sum(1 for m in sit_markers if m in lower)
    task_hits = sum(1 for m in task_markers if m in lower)
    action_hits = sum(1 for m in action_verbs_1p if m in lower)
    result_hits = sum(1 for m in result_markers if m in lower)

    # Cálculo sensible de Situación (1 a 5)
    s_score = 1
    if sit_hits >= 1 or word_count >= 20:
        s_score = 2
    if sit_hits >= 1 and word_count >= 28:
        s_score = 3
    if sit_hits >= 2 and word_count >= 45:
        s_score = 4
    if sit_hits >= 2 and word_count >= 65 and q_overlap_ratio >= 0.2:
        s_score = 5

    # Cálculo sensible de Tarea (1 a 5)
    t_score = 1
    if task_hits >= 1 or (sit_hits >= 1 and word_count >= 25):
        t_score = 2
    if task_hits >= 1 and word_count >= 30:
        t_score = 3
    if task_hits >= 2 or (task_hits >= 1 and word_count >= 50):
        t_score = 4
    if task_hits >= 2 and word_count >= 65:
        t_score = 5

    # Cálculo sensible de Acción (1 a 5)
    a_score = 1
    if action_hits >= 1:
        a_score = 2
    if action_hits >= 2 or (action_hits >= 1 and len(matched_tech_terms) >= 1):
        a_score = 3
    if action_hits >= 2 and len(matched_tech_terms) >= 2 and word_count >= 40:
        a_score = 4
    if action_hits >= 3 and len(matched_tech_terms) >= 3 and word_count >= 60:
        a_score = 5

    # Cálculo sensible de Resultado (1 a 5)
    r_score = 1
    if result_hits >= 1:
        r_score = 2
    if metrics_count >= 1 or (result_hits >= 2 and word_count >= 40):
        r_score = 3
    if metrics_count >= 1 and result_hits >= 1:
        r_score = 4
    if metrics_count >= 2 and result_hits >= 1 and word_count >= 50:
        r_score = 5

    # Cálculo de Claridad Técnica (1 a 5)
    tech_score = 1
    if len(matched_tech_terms) >= 1 or word_count >= 25:
        tech_score = 2
    if len(matched_tech_terms) >= 2:
        tech_score = 3
    if len(matched_tech_terms) >= 3 and action_hits >= 1:
        tech_score = 4
    if len(matched_tech_terms) >= 4 and action_hits >= 2 and word_count >= 55:
        tech_score = 5

    # Cálculo de Pertinencia a la pregunta (1 a 5)
    rel_score = 1
    if q_overlap_ratio >= 0.08 or len(matched_tech_terms) >= 1:
        rel_score = 2
    if q_overlap_ratio >= 0.16:
        rel_score = 3
    if q_overlap_ratio >= 0.28 and word_count >= 35:
        rel_score = 4
    if q_overlap_ratio >= 0.40 and word_count >= 50:
        rel_score = 5

    # Construir retroalimentación personalizada según las fortalezas y debilidades reales
    strengths_parts = []
    if s_score >= 4:
        strengths_parts.append("contextualizaste muy bien la situación inicial")
    if a_score >= 4:
        strengths_parts.append("detallaste tus acciones individuales en primera persona")
    if r_score >= 4 and metrics_list:
        strengths_parts.append(f"respaldaste el resultado con métricas concretas ({', '.join(metrics_list[:3])})")
    if tech_score >= 4 and matched_tech_terms:
        strengths_parts.append(f"empleaste terminología técnica precisa ({', '.join(matched_tech_terms[:3])})")

    if strengths_parts:
        strengths = "Puntos fuertes: " + ", ".join(strengths_parts) + "."
    elif rel_score >= 3:
        strengths = "Tu respuesta aborda el tema de la pregunta, aunque de forma todavía general."
    else:
        strengths = "Intentaste dar una respuesta inicial, pero aún no se conecta directamente con el caso solicitado en la pregunta."

    missing_parts = []
    if rel_score <= 2:
        missing_parts.append("enfocarte directamente en lo que pide la pregunta")
    if s_score <= 2:
        missing_parts.append("especificar el proyecto o contexto inicial (Situación)")
    if t_score <= 2:
        missing_parts.append("aclarar cuál era tu meta o responsabilidad específica (Tarea)")
    if a_score <= 2:
        missing_parts.append("usar verbos en primera persona explicando qué hiciste tú exactamente (Acción)")
    if r_score <= 2:
        missing_parts.append("cerrar con el impacto cuantitativo logrado en porcentaje, tiempo o indicadores (Resultado)")
    if tech_score <= 2:
        missing_parts.append(f"mencionar las herramientas o métodos técnicos de {career_code} que utilizaste")

    if missing_parts:
        improvements = "Para subir de nivel en esta pregunta necesitas: " + "; ".join(missing_parts) + "."
    else:
        improvements = "Excelente estructura STAR; podrías contrastar brevemente qué alternativa descartaste y por qué."

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


def _call_external_or_ollama_llm(
    provider: str,
    api_key: Optional[str],
    model_name: Optional[str],
    user_prompt: str,
) -> Optional[Dict[str, Any]]:
    """
    Permite evaluar con las llaves API que tenga el usuario (Gemini, OpenAI/Groq) o con Ollama local.
    """
    prov = (provider or "ollama").lower()

    if prov == "gemini" and api_key:
        mdl = model_name or "gemini-2.5-flash"
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{mdl}:generateContent?key={api_key}"
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

    elif prov in ("openai", "groq") and api_key:
        base_url = (
            "https://api.groq.com/openai/v1/chat/completions"
            if prov == "groq"
            else "https://api.openai.com/v1/chat/completions"
        )
        mdl = model_name or ("llama-3.3-70b-versatile" if prov == "groq" else "gpt-4o-mini")
        with httpx.Client(timeout=6.0) as client:
            resp = client.post(
                base_url,
                headers={"Authorization": f"Bearer {api_key}"},
                json={
                    "model": mdl,
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

    else:
        with httpx.Client(timeout=2.5) as client:
            resp = client.post(
                f"{settings.OLLAMA_BASE_URL}/api/chat",
                json={
                    "model": model_name or settings.OLLAMA_MODEL,
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

    return None


def evaluate_candidate_turn_node(state: InterviewGraphState) -> Dict[str, Any]:
    """
    Nodo del Agente Evaluador en LangGraph.
    """
    start_ts = time.perf_counter()
    aux = state.get("auxiliary_features", {})
    question_text = state.get("current_question_text", "")
    candidate_response = state.get("candidate_response", "")
    career_code = state.get("career_code", "ITC")
    target_role = state.get("target_role", "Practicante")

    user_prompt = (
        f"Carrera: {career_code}\n"
        f"Puesto Objetivo: {target_role} ({state.get('seniority_level')})\n"
        f"Contexto de la Vacante: {state.get('job_description_text', '')[:300]}\n"
        f"Pregunta Actual: {question_text}\n"
        f"Respuesta del Candidato: {candidate_response}\n"
        f"Metadatos Auxiliares Regex: {json.dumps(aux, ensure_ascii=False)}\n"
    )

    eval_data = None
    json_valid = True

    for attempt in range(2):
        try:
            parsed = _call_external_or_ollama_llm(
                provider=state.get("llm_provider") or "ollama",
                api_key=state.get("llm_api_key"),
                model_name=state.get("llm_model"),
                user_prompt=user_prompt,
            )
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
                        "star_situation": max(1, min(5, int(parsed["star_situation"]))),
                        "star_task": max(1, min(5, int(parsed["star_task"]))),
                        "star_action": max(1, min(5, int(parsed["star_action"]))),
                        "star_result": max(1, min(5, int(parsed["star_result"]))),
                        "technical_clarity": max(1, min(5, int(parsed["technical_clarity"]))),
                        "relevance": max(1, min(5, int(parsed["relevance"]))),
                        "strengths": str(parsed["strengths"]),
                        "improvement_areas": str(parsed["improvement_areas"]),
                    }
                    break
        except Exception:
            json_valid = attempt == 0
            continue

    if eval_data is None:
        eval_data = _deep_star_analyzer(
            question_text=question_text,
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
