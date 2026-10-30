# Golden dataset humano: cómo calificar

Este es el paso que vuelve **válida** la medición de los agentes. Las respuestas de
`backend/app/data/calibracion_star.jsonl` fueron calificadas con la rúbrica, pero **no por
personas independientes**; sirven para detectar fallas grandes, no para afirmar que la IA
califica como un reclutador.

## Pasos

1. Copia `plantilla_calificacion_humana.csv` una vez por persona calificadora
   (por ejemplo `calificaciones_profe_ana.csv`). Ábrela en Excel o Google Sheets.
2. Cada persona califica **sin ver la calificación de la IA ni la de las demás**, usando la
   rúbrica de `backend/app/data/rubrica_star.json`: en cada dimensión cuenta cuántos de los 5
   indicadores se cumplen (0 a 5). Escribe su nombre en `calificador`.
   - S = Situación, T = Tarea, A = Acción, R = Resultado, C = Claridad técnica, P = Pertinencia.
3. Junta todos los archivos en uno solo (mismas columnas, una fila por persona y respuesta).
4. Agrega respuestas reales de compañeros (anonimizadas y con su permiso) con un `id` nuevo.
   Meta: 150–200 respuestas, 2–3 calificadores.
5. Mide:

```bash
python scripts/evaluar_evaluador.py --modo llm --golden datos/golden/mis_calificaciones.csv
```

El script reporta primero **cuánto coinciden los humanos entre sí** (si no coinciden, hay que
aclarar la rúbrica antes de culpar a la IA) y luego **cuánto coincide la IA con la mediana
humana**. Meta del SRS (RN-07): kappa ponderado ≥ 0.75.
