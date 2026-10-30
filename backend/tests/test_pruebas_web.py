"""Conjunto de prueba con respuestas publicadas en internet, carga a golden_dataset y métrica AUC."""
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WEB = ROOT / "backend" / "app" / "data" / "pruebas_web_star.json"


def test_conjunto_web_es_consistente():
    data = json.loads(WEB.read_text(encoding="utf-8"))
    items = data["items"]
    assert len(items) >= 20
    assert len({i["id"] for i in items}) == len(items)
    labels = {i["etiqueta"] for i in items}
    assert labels == {"fuerte", "debil"}
    for it in items:
        assert it["fuente"] in data["fuentes"] and data["fuentes"][it["fuente"]]["url"].startswith("https://")
        assert len(it["respuesta"]) > 40 and it["pregunta"] and it["motivo_de_la_fuente"]


def test_golden_dataset_se_llena_una_sola_vez(client):
    from app.database import SessionLocal
    from app.models import GoldenDataset
    from app.services.question_seed import seed_golden_dataset

    with SessionLocal() as db:
        seed_golden_dataset(db)
        total = db.query(GoldenDataset).count()
        assert seed_golden_dataset(db) == 0
        assert db.query(GoldenDataset).count() == total
        web = db.query(GoldenDataset).filter(GoldenDataset.reviewer_notes.like("[web-%")).count()
        assert web == len(json.loads(WEB.read_text(encoding="utf-8"))["items"])


def test_auc_del_arnes():
    spec = importlib.util.spec_from_file_location("evaluar_evaluador", ROOT / "scripts" / "evaluar_evaluador.py")
    argv, sys.argv = sys.argv, ["evaluar_evaluador.py"]
    try:
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
    finally:
        sys.argv = argv
    assert mod.auc([4, 5], [1, 2]) == 1.0
    assert mod.auc([1], [4]) == 0.0
    assert mod.auc([3], [3]) == 0.5
