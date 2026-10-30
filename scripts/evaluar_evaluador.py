#!/usr/bin/env python3
"""
Arnés de evaluación del Agente Evaluador ("entrenamiento" por calibración).

Compara las calificaciones del evaluador contra calificaciones de referencia y
reporta, por dimensión STAR:
  - Kappa ponderado cuadrático (QWK): acuerdo para escalas ordinales 0-5. Meta >= 0.75 (RN-07).
  - Error absoluto medio (MAE). Meta <= 0.5.
  - % dentro de ±1 punto. Meta >= 90 %.

Uso:
  # Línea base del analizador local (sin IA, sin costo):
  python scripts/evaluar_evaluador.py --modo local

  # Agente de IA real con tus llaves del .env (≈ 24 llamadas, centavos de dólar):
  python scripts/evaluar_evaluador.py --modo llm --rubrica indicadores
  python scripts/evaluar_evaluador.py --modo llm --rubrica holistico    # comparar contra el prompt anterior

  # Con calificaciones HUMANAS (plantilla en datos/golden/plantilla_calificacion_humana.csv):
  python scripts/evaluar_evaluador.py --modo llm --golden datos/golden/mis_calificaciones.csv

Por defecto usa backend/app/data/calibracion_star.jsonl (sintético, NO validado por humanos):
sirve para detectar fallas grandes, no para afirmar que el modelo califica como una persona.
"""
import argparse
import csv
import json
import os
import statistics
import sys
import time
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

DIMS = ["star_situation", "star_task", "star_action", "star_result", "technical_clarity", "relevance"]
SHORT = {"star_situation": "S", "star_task": "T", "star_action": "A", "star_result": "R",
         "technical_clarity": "C", "relevance": "P"}


def qwk(a, b, k=6):
    """Kappa ponderado cuadrático entre dos listas de enteros 0..k-1."""
    if not a:
        return float("nan")
    o = [[0] * k for _ in range(k)]
    for x, y in zip(a, b):
        o[x][y] += 1
    n = len(a)
    ha = [sum(o[i]) for i in range(k)]
    hb = [sum(o[i][j] for i in range(k)) for j in range(k)]
    num = den = 0.0
    for i in range(k):
        for j in range(k):
            w = ((i - j) ** 2) / ((k - 1) ** 2)
            num += w * o[i][j]
            den += w * ha[i] * hb[j] / n
    return 1.0 - num / den if den else 1.0


def load_reference(args):
    items = []
    if args.golden:
        by_id = defaultdict(list)
        meta = {}
        with open(args.golden, encoding="utf-8") as f:
            for row in csv.DictReader(f):
                if not row.get("S", "").strip():
                    continue
                by_id[row["id"]].append({SHORT_INV[c]: int(row[c]) for c in "STARCP"})
                meta[row["id"]] = row
        for iid, raters in by_id.items():
            m = meta[iid]
            items.append({
                "id": iid, "career_code": m["carrera"], "pregunta": m["pregunta"],
                "vacante": m.get("vacante", ""), "respuesta": m["respuesta"], "nivel": "humano",
                "esperado": {d: int(round(statistics.median(r[d] for r in raters))) for d in DIMS},
                "calificadores": raters,
            })
    else:
        path = ROOT / "backend" / "app" / "data" / "calibracion_star.jsonl"
        items = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    return items


SHORT_INV = {v: k for k, v in SHORT.items()}


def report_human_agreement(items):
    """Acuerdo entre calificadores humanos (QWK por pares), si hay 2 o más por respuesta."""
    multi = [it for it in items if len(it.get("calificadores", [])) >= 2]
    if not multi:
        return
    print("Acuerdo entre humanos (primeros dos calificadores de cada respuesta):")
    for d in DIMS:
        a = [it["calificadores"][0][d] for it in multi]
        b = [it["calificadores"][1][d] for it in multi]
        print(f"  {d:20s} QWK {qwk(a, b):.2f}")
    print()


def evaluate(item, mode):
    if mode == "llm":
        os.environ["EVALUATOR_RUBRIC_MODE"] = ARGS.rubrica
    from app.agents import evaluator
    from app.services.anonymizer import extract_auxiliary_features

    state = {
        "career_code": item["career_code"], "target_role": "Puesto de la vacante",
        "seniority_level": "Junior / Intern", "job_description_text": item.get("vacante", ""),
        "current_question_text": item["pregunta"], "candidate_response": item["respuesta"],
        "auxiliary_features": extract_auxiliary_features(item["respuesta"]),
    }
    if mode == "local":
        res = evaluator._critical_star_analyzer(
            question_text=item["pregunta"], vacancy_context=item.get("vacante", ""),
            response_text=item["respuesta"], career_code=item["career_code"],
            target_role="Puesto", aux=state["auxiliary_features"])
        return {d: res[d] for d in DIMS}, "local"
    out = evaluator.evaluate_candidate_turn_node(state)
    ev = out["evaluation_result"]
    return {d: ev[d] for d in DIMS}, ev.get("evaluator_source", "?")


def main():
    items = load_reference(ARGS)
    if ARGS.modo == "llm":
        from app.config import settings
        if not (settings.gemini_ready or settings.openai_ready):
            sys.exit("No hay llaves válidas en .env (corre scripts/check_apis.py).")
    report_human_agreement(items)
    preds, refs, rows, sources = defaultdict(list), defaultdict(list), [], defaultdict(int)
    t0 = time.time()
    for it in items:
        got, src = evaluate(it, ARGS.modo)
        sources[src.split(":")[0]] += 1
        for d in DIMS:
            preds[d].append(int(got[d]))
            refs[d].append(int(it["esperado"][d]))
        rows.append({"id": it["id"], "nivel": it.get("nivel"), "esperado": it["esperado"], "obtenido": got,
                     "fuente": src})
        sys.stdout.write(".")
        sys.stdout.flush()
    print(f"\n{len(items)} respuestas en {time.time() - t0:.1f} s · fuentes: {dict(sources)}\n")

    summary = {}
    print(f"{'Dimensión':20s} {'QWK':>6s} {'MAE':>6s} {'±1':>6s} {'exacto':>7s}")
    for d in DIMS:
        a, b = refs[d], preds[d]
        mae = statistics.mean(abs(x - y) for x, y in zip(a, b))
        w1 = 100 * sum(abs(x - y) <= 1 for x, y in zip(a, b)) / len(a)
        ex = 100 * sum(x == y for x, y in zip(a, b)) / len(a)
        k = qwk(a, b)
        summary[d] = {"qwk": round(k, 3), "mae": round(mae, 2), "dentro_1_%": round(w1, 1), "exacto_%": round(ex, 1)}
        print(f"{d:20s} {k:6.2f} {mae:6.2f} {w1:5.0f}% {ex:6.0f}%")
    avg_ref = [statistics.mean(r["esperado"][d] for d in DIMS) for r in rows]
    avg_got = [statistics.mean(r["obtenido"][d] for d in DIMS) for r in rows]
    mae_avg = statistics.mean(abs(x - y) for x, y in zip(avg_ref, avg_got))
    corr = statistics.correlation(avg_ref, avg_got) if len(rows) > 2 else float("nan")
    print(f"\nPromedio del turno: MAE {mae_avg:.2f} · correlación {corr:.2f}")
    qwks = [summary[d]["qwk"] for d in DIMS]
    ok = min(qwks) >= 0.75 and mae_avg <= 0.5
    print("Meta RN-07 (QWK ≥ 0.75 en todas las dimensiones y MAE del promedio ≤ 0.5):", "CUMPLE" if ok else "NO CUMPLE")

    print("\nMayores diferencias (para revisar a mano):")
    worst = sorted(rows, key=lambda r: -abs(statistics.mean(r["esperado"].values()) - statistics.mean(r["obtenido"].values())))
    for r in worst[:6]:
        e = statistics.mean(r["esperado"].values())
        g = statistics.mean(r["obtenido"].values())
        print(f"  {r['id']} ({r['nivel']}): esperado {e:.2f} · obtenido {g:.2f}")

    out = ROOT / f"resultados_evaluador_{ARGS.modo}_{ARGS.rubrica}.json"
    out.write_text(json.dumps({"modo": ARGS.modo, "rubrica": ARGS.rubrica, "resumen": summary,
                               "mae_promedio": round(mae_avg, 3), "correlacion": round(corr, 3),
                               "cumple_rn07": ok, "detalle": rows}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nDetalle en {out.name}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--modo", choices=["local", "llm"], default="local")
    ap.add_argument("--rubrica", choices=["indicadores", "holistico"], default="indicadores")
    ap.add_argument("--golden", help="CSV con calificaciones humanas (ver datos/golden/)")
    ARGS = ap.parse_args()
    main()
