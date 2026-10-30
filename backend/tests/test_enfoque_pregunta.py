"""La calificación pondera lo que la pregunta pide (no siempre STAR completo)."""
import json
from pathlib import Path

from app.agents.evaluator import _critical_star_analyzer
from app.agents.question_focus import question_focus, weighted_average
from app.services.anonymizer import extract_auxiliary_features

DATA = Path(__file__).resolve().parents[1] / "app" / "data"
DIMS = ("star_situation", "star_task", "star_action", "star_result", "technical_clarity", "relevance")


def test_detecta_lo_que_pide_cada_pregunta():
    como = question_focus("Cuéntame de una vez en que ayudaste a un compañero. ¿Cómo estructuraste tu explicación?")
    assert como["pide"] == ["star_situation", "star_action"] and not como["star_completo"]
    plan = question_focus("¿Qué plan de acción seguiste para implementarlo a tiempo y qué entregable lograste?")
    assert "star_action" in plan["pide"] and "star_result" in plan["pide"]
    rol = question_focus("En el último proyecto en equipo, ¿cuál fue exactamente tu rol?")
    assert "star_task" in rol["pide"] and "star_result" not in rol["pide"]
    # El verbo como tema no convierte la pregunta en "¿cómo?": es historia completa.
    assert question_focus("Cuéntame de una vez que resolviste un problema difícil con un cliente.")["star_completo"]


def test_historia_completa_es_el_promedio_de_siempre():
    s = dict(star_situation=4, star_task=2, star_action=5, star_result=1, technical_clarity=3, relevance=3)
    assert weighted_average(s, question_focus("Cuéntame de una vez que cometiste un error.")) == round(sum(s.values()) / 6, 2)


def test_lo_no_pedido_nunca_baja_la_nota():
    f = question_focus("¿Cómo estructuraste la documentación para tu equipo?")
    sin_resultado = dict(star_situation=4, star_task=4, star_action=5, star_result=0, technical_clarity=4, relevance=5)
    con_resultado = dict(sin_resultado, star_result=5)
    assert weighted_average(sin_resultado, f) >= 4.0
    assert weighted_average(con_resultado, f) >= weighted_average(sin_resultado, f)


def test_respuestas_enfocadas_buenas_aprueban_y_debiles_no():
    items = json.loads((DATA / "pruebas_enfoque.json").read_text(encoding="utf-8"))["items"]
    for it in items:
        if not it["etiqueta"]:
            continue
        r = _critical_star_analyzer(it["pregunta"], "", it["respuesta"], it["career_code"], "Puesto",
                                    extract_auxiliary_features(it["respuesta"]))
        avg = weighted_average(r, question_focus(it["pregunta"]))
        if it["etiqueta"] == "buena":
            assert avg >= 3.0, (it["id"], avg)
            assert "Resultado = 0/5" not in r["improvement_areas"]
        else:
            assert avg < 2.5, (it["id"], avg)


def test_retro_no_exige_lo_que_no_se_pidio_y_detecta_respuesta_hipotetica():
    q = "Cuéntame de una vez que ayudaste a un compañero. ¿Cómo estructuraste tu explicación?"
    resp = ("Le pedí que compartiera pantalla, vi que su versión de Node no coincidía, le expliqué con un diagrama "
            "cómo se conectaban la API y la base de datos en Docker y escribí una guía en el README con los comandos.")
    r = _critical_star_analyzer(q, "", resp, "ITC", "Puesto", extract_auxiliary_features(resp))
    assert "pide el resultado" not in r["improvement_areas"]
    h = "la verdad no he tenido problemas así pero en todo caso sería investigar a profundidad el código y la documentación"
    r2 = _critical_star_analyzer("¿Qué estrategia seguiste con el código legado y qué resultado obtuviste?", "", h,
                                 "ITC", "Puesto", extract_auxiliary_features(h))
    assert "caso más parecido" in r2["improvement_areas"] and r2["star_situation"] <= 1
