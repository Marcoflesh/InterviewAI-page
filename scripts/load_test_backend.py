#!/usr/bin/env python3
"""
Prueba de carga del BACKEND completo: N usuarios simultáneos que se registran,
inician una entrevista, responden K preguntas y piden su reporte.

    python scripts/load_test_backend.py --base http://localhost:8000 --users 20 --turns 5

Úsalo contra tu Docker local. Con llaves reales consume saldo (≈ users x (turns+3) llamadas).
"""
import argparse
import random
import statistics
import string
import sys
import time
from concurrent.futures import ThreadPoolExecutor

import httpx

ANSWERS = [
    "En mi práctica la API tardaba 900 ms; mi meta era bajarla a 250 ms. Agregué índices en PostgreSQL y caché "
    "con Redis, validé con pruebas de carga y reduje la latencia 72% soportando 3 veces más usuarios.",
    "Hice un script en Python con pandas que bajó un reporte de 2 horas a 5 minutos y ahora se usa cada semana.",
    "No sé.",
    "Trabajé en equipo y siempre doy lo mejor de mí.",
]


def user_flow(base: str, turns: int, timings: dict, errors: list):
    c = httpx.Client(base_url=base, timeout=120)
    tag = "".join(random.choices(string.ascii_lowercase, k=10))
    def timed(name, fn):
        t0 = time.perf_counter()
        r = fn()
        timings.setdefault(name, []).append((time.perf_counter() - t0) * 1000)
        if r.status_code >= 400:
            errors.append(f"{name}:{r.status_code}")
        return r
    r = timed("register", lambda: c.post("/api/auth/register", json={
        "full_name": "Carga Prueba Usuario", "email": f"carga.{tag}@gmail.com",
        "password": "Contrasena123", "university": "Tec"}))
    if r.status_code != 200:
        return
    c.headers["Authorization"] = f"Bearer {r.json()['access_token']}"
    r = timed("start", lambda: c.post("/api/sessions/start", json={
        "career_code": "ITC", "target_role": "Backend Jr",
        "cv_text": "Proyectos con Python, FastAPI, PostgreSQL y Docker.",
        "job_description_text": "Backend Jr para plataforma de pagos con APIs REST, PostgreSQL y Docker."}))
    if r.status_code != 200:
        return
    sid = r.json()["session_id"]
    for _ in range(turns):
        timed("turn", lambda: c.post("/api/sessions/turn", json={"session_id": sid,
                                                                  "candidate_response": random.choice(ANSWERS)}))
    timed("report", lambda: c.get(f"/api/sessions/{sid}/report"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="http://localhost:8000")
    ap.add_argument("--users", type=int, default=20)
    ap.add_argument("--turns", type=int, default=5)
    a = ap.parse_args()
    timings, errors = {}, []
    t0 = time.perf_counter()
    with ThreadPoolExecutor(max_workers=a.users) as pool:
        for _ in range(a.users):
            pool.submit(user_flow, a.base, a.turns, timings, errors)
    wall = time.perf_counter() - t0
    total = sum(len(v) for v in timings.values())
    print(f"{a.users} usuarios simultáneos · {total} peticiones en {wall:.1f} s ({total / wall:.1f} req/s)")
    for name, v in timings.items():
        v.sort()
        p95 = v[int(0.95 * (len(v) - 1))]
        print(f"  {name:9s} n={len(v):4d}  p50={statistics.median(v):7.0f} ms  p95={p95:7.0f} ms  máx={v[-1]:7.0f} ms")
    print(f"  errores: {len(errors)} {sorted(set(errors))[:8]}")
    sys.exit(1 if errors and len(errors) > 0.05 * total else 0)


if __name__ == "__main__":
    main()
