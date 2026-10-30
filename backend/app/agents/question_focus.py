"""
Qué pide cada pregunta y cómo se pondera la calificación.

No todas las preguntas piden STAR completo. "¿Cómo estructuraste tu explicación?" pide sobre
todo la Acción; "¿Cuál era tu rol?" pide la Tarea. Antes se promediaban siempre las 6
dimensiones, así que una respuesta muy buena a lo que se preguntó bajaba por no traer un
Resultado que nadie pidió.

Regla (la misma en frontend/js/app.js):
- Dimensiones pedidas = las partes STAR que la pregunta menciona + pertinencia + claridad
  técnica (con medio peso si la pregunta no es técnica).
- El promedio usa solo las pedidas. Las no pedidas solo pueden SUBIR la nota (cuentan con
  medio peso si están por encima del promedio de lo pedido), nunca bajarla.
- Si la pregunta no tiene una sub-pregunta concreta ("Cuéntame de una vez que…"), se espera
  STAR completo y el resultado es el mismo promedio de siempre.
"""
import re
import unicodedata
from typing import Dict, List

STAR = ("star_situation", "star_task", "star_action", "star_result")
DIMS = STAR + ("technical_clarity", "relevance")
NOMBRES = {
    "star_situation": "el contexto (Situación)",
    "star_task": "tu papel o meta (Tarea)",
    "star_action": "qué hiciste y cómo (Acción)",
    "star_result": "el resultado (Resultado)",
    "technical_clarity": "la claridad técnica",
    "relevance": "responder justo lo que se preguntó",
}

_S = re.compile(r"cuentame|platicame|describe|relata|hablame|una vez|ocasion|situacion|alguna vez"
                r"|proyecto|reto|momento|experiencia")
_T = re.compile(r"\btu (rol|papel|responsabilidad|meta|objetivo|tarea|parte|aporte|contribucion)"
                r"|te (toco|pidieron|asignaron|correspond)|que (debias|tenias que)|de que (eras|partes)"
                r"|responsable de|que parte")
# Solo cuenta si la pregunta PREGUNTA por la acción ("¿cómo…?", "¿qué hiciste?", "¿qué plan…?"),
# no si el verbo es parte del tema ("Cuéntame de una vez que resolviste…" es historia completa).
_A = re.compile(r"\bcomo\b|que hiciste|que haces|que harias|estrategia|\bplan\b|pasos|enfoque"
                r"|que (acciones|medidas|decisiones|herramientas|metodo)|que parte (construiste|hiciste|programaste)")
_R = re.compile(r"resultado|lograste|\blogro|impacto|entregable|como (termino|acabo|salio)|que obtuviste"
                r"|que paso (despues|al final)|mediste|metrica|aprendiste|que cambio|como te fue")
_TECNICA = re.compile(r"tecnic|servicio|caida|incidente|falla|codigo|\bapi\b|framework|lenguaje|herramienta|base de datos|arquitect|\bbug|error"
                      r"|sistema|despliegue|deploy|produccion|entorno|servidor|nube|prueba|\btest|algoritmo"
                      r"|rendimiento|datos|modelo|\bgit\b|migracion|backend|frontend|software|programa"
                      r"|analisis|infraestructura|seguridad|integracion")


def _norm(text: str) -> str:
    s = (text or "").lower()
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")


def question_focus(question_text: str) -> Dict[str, object]:
    """Partes STAR que la pregunta pide explícitamente y si es una pregunta técnica."""
    q = _norm(question_text)
    pide: List[str] = []
    if _S.search(q):
        pide.append("star_situation")
    if _T.search(q):
        pide.append("star_task")
    if _A.search(q):
        pide.append("star_action")
    if _R.search(q):
        pide.append("star_result")
    concreta = any(d in pide for d in ("star_task", "star_action", "star_result"))
    if not concreta:
        pide = list(STAR)  # "Cuéntame de una vez que…": se espera la historia completa
    return {"pide": pide, "tecnica": bool(_TECNICA.search(q)), "star_completo": len(pide) == 4}


def weights(focus: Dict[str, object]) -> Dict[str, float]:
    """Peso de cada dimensión pedida. Historia completa = las 6 con el mismo peso (como siempre)."""
    if focus["star_completo"]:
        return {d: 1.0 for d in DIMS}
    w = {d: 1.0 for d in focus["pide"]}
    w["relevance"] = 1.0
    w["technical_clarity"] = 1.0 if focus["tecnica"] else 0.5  # claridad sí; vocabulario técnico no tanto
    return w


def weighted_average(scores: Dict[str, float], focus: Dict[str, object]) -> float:
    w = weights(focus)
    total = sum(float(scores[d]) * p for d, p in w.items())
    peso = sum(w.values())
    base = total / peso
    # Lo que la pregunta no pidió solo puede sumar (medio peso), nunca restar.
    for d in DIMS:
        if d not in w and float(scores[d]) > base:
            total += 0.5 * float(scores[d])
            peso += 0.5
    return round(total / peso, 2)


def describe_focus(focus: Dict[str, object]) -> str:
    """Texto corto para el prompt del evaluador y la retroalimentación."""
    if focus["star_completo"]:
        return "la historia completa: contexto, tu papel, qué hiciste y el resultado"
    partes = [NOMBRES[d] for d in focus["pide"] if d != "star_situation"]
    return " y ".join(partes) if partes else NOMBRES["star_action"]


def not_asked(focus: Dict[str, object]) -> List[str]:
    return [d for d in STAR if d not in focus["pide"]]
