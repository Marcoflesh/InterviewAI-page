"""
Rúbrica analítica STAR (escala anclada por indicadores).

En lugar de pedirle al modelo "califica de 0 a 5", se le pide decidir 30 criterios
observables de sí/no (5 por dimensión) citando la evidencia. La calificación de cada
dimensión es cuántos criterios se cumplen. Esto sigue la recomendación de usar escalas
ancladas en entrevistas estructuradas y de evitar puntajes holísticos en LLM-as-judge.
Fuentes y justificación: research/metodo_star.md
"""
import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Optional

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
DIM_PREFIX = {
    "star_situation": "S", "star_task": "T", "star_action": "A",
    "star_result": "R", "technical_clarity": "C", "relevance": "P",
}
INDICATOR_IDS = [f"{p}{i}" for p in DIM_PREFIX.values() for i in range(1, 6)]


@lru_cache(maxsize=1)
def load_rubric() -> Dict[str, Any]:
    return json.loads((DATA_DIR / "rubrica_star.json").read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def load_fewshot() -> Dict[str, Any]:
    return json.loads((DATA_DIR / "ejemplos_fewshot.json").read_text(encoding="utf-8"))


def _yes(v: Any) -> bool:
    if isinstance(v, bool):
        return v
    if isinstance(v, (int, float)):
        return v == 1
    return isinstance(v, str) and v.strip().lower() in {"true", "si", "sí", "1", "yes"}


def scores_from_indicators(indicators: Dict[str, Any]) -> Dict[str, int]:
    return {dim: sum(1 for i in range(1, 6) if _yes(indicators.get(f"{p}{i}"))) for dim, p in DIM_PREFIX.items()}


def _fewshot_block() -> str:
    lines = []
    for n, ex in enumerate(load_fewshot()["ejemplos"], 1):
        met = [k for k, v in ex["indicadores"].items() if v]
        lines.append(
            f"Ejemplo {n} (nivel {ex['nivel']}):\n"
            f"Pregunta: {ex['pregunta']}\n"
            f"Respuesta: {ex['respuesta']}\n"
            f"Indicadores cumplidos: {', '.join(met) if met else 'ninguno'}"
        )
    return "\n\n".join(lines)


@lru_cache(maxsize=1)
def build_system_prompt() -> str:
    r = load_rubric()
    dims = []
    for dim, data in r["dimensiones"].items():
        items = "\n".join(f"  {k}: {v}" for k, v in data["indicadores"].items())
        dims.append(f"{data['nombre']} ({dim}):\n{items}")
    rules = "\n".join(f"- {x}" for x in r["reglas_generales"])
    schema = (
        '{\n'
        '  "evidencia": {"S": "cita breve o \'sin evidencia\'", "T": "...", "A": "...", "R": "...", "C": "...", "P": "..."},\n'
        '  "indicadores": {"S1": true, "S2": false, ... hasta "P5"},\n'
        '  "strengths": "máximo 2 oraciones, en segunda persona",\n'
        '  "improvement_areas": "máximo 2 oraciones, en segunda persona, con una acción concreta"\n'
        '}'
    )
    return (
        "Eres el Agente Evaluador de InterviewAI: un reclutador técnico riguroso, justo y sin complacencia. "
        "Evalúas UNA respuesta de entrevista conductual con el método STAR usando una rúbrica de indicadores.\n\n"
        f"{r['como_se_califica']}\n{r['nivel_esperado']}\n\n"
        "INDICADORES:\n" + "\n\n".join(dims) + "\n\n"
        "REGLAS:\n" + rules + "\n\n"
        "PROCESO: primero escribe la evidencia (citas breves de la respuesta) para cada dimensión; "
        "después decide cada indicador con base SOLO en esa evidencia.\n\n"
        "Devuelve ÚNICAMENTE un JSON válido con esta forma (los 30 indicadores, de S1 a P5):\n" + schema + "\n\n"
        "Retroalimentación: en español de México, de tú, honesta y respetuosa, basada en lo que dijo la persona. "
        "Prohibido usar emojis, viñetas o Markdown.\n\n"
        "EJEMPLOS RESUELTOS (para calibrarte; no los repitas):\n\n" + _fewshot_block()
    )


def parse_indicator_payload(data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    ind = data.get("indicadores")
    if not isinstance(ind, dict) or not any(k in ind for k in INDICATOR_IDS):
        return None
    out: Dict[str, Any] = scores_from_indicators(ind)
    out["indicadores"] = {k: _yes(ind.get(k)) for k in INDICATOR_IDS}
    out["strengths"] = str(data.get("strengths", ""))[:1200]
    out["improvement_areas"] = str(data.get("improvement_areas", ""))[:1200]
    return out

