import re
from typing import Dict, Iterable, List, Optional

# Expresiones regulares para anonimización de datos personales (PII) en currículums
EMAIL_REGEX = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
PHONE_REGEX = re.compile(
    r"(?<![\d.,])(?:\+?\d{1,3}[\s.-]?)?\(?\d{2,3}\)?[\s.-]?\d{3,4}[\s.-]?\d{4}(?![\d%])"
)
CURP_RFC_ID_REGEX = re.compile(
    r"\b[A-Z]{4}\d{6}[HM][A-Z]{5}[A-Z0-9]\d\b|\b[A-Z&Ñ]{3,4}\d{6}[A-Z0-9]{3}\b|\bA0\d{7}\b"
)
URL_PERSONAL_REGEX = re.compile(
    r"(?:https?://)?(?:www\.)?(?:linkedin\.com/in/|github\.com/|instagram\.com/|facebook\.com/|x\.com/|twitter\.com/)[^\s,)>;]*[^\s,)>;.]",
    re.IGNORECASE,
)

# Expresiones regulares para detectar métricas cuantitativas en respuestas STAR (Dimensión Resultado)
QUANTITATIVE_METRICS_REGEX = re.compile(
    r"\b\d+(?:[.,]\d+)?\s*(?:%|por\s*ciento|ms|milisegundos|segundos|s|minutos|min|horas|h|días|semanas|meses|x|veces|usuarios|clientes|solicitudes|req/s|rpm|fps|mb|gb|tb|usd|mxn|\$|pesos|dólares|puntos|k|m|ppm|oee)\b"
    r"|\$\s*\d+(?:[.,]\d+)?"
    r"|\b(?:reduj\w+|increment\w+|aument\w+|mejor\w+|ahorr\w+|baj\w+|sub\w+|optimiz\w+)\s+(?:en\s+)?(?:un\s+)?\d+(?:[.,]\d+)?\s*%?",
    re.IGNORECASE,
)


def anonymize_pii(text: str, extra_names: Optional[Iterable[str]] = None) -> str:
    """
    Reemplaza correos electrónicos, teléfonos, matrículas/CURP/RFC, enlaces personales y
    (si se conocen) el nombre y apellidos del usuario antes de guardar el texto o
    enviarlo a un proveedor de IA.
    """
    if not text:
        return ""
    cleaned = EMAIL_REGEX.sub("[EMAIL_ANONIMIZADO]", text)
    for name in extra_names or []:
        for part in {p for p in re.split(r"\s+", name or "") if len(p) >= 3}:
            cleaned = re.sub(rf"(?<!\w){re.escape(part)}(?!\w)", "[NOMBRE]", cleaned, flags=re.IGNORECASE)
    cleaned = CURP_RFC_ID_REGEX.sub("[ID_ANONIMIZADO]", cleaned)
    cleaned = URL_PERSONAL_REGEX.sub("[PERFIL_ANONIMIZADO]", cleaned)
    cleaned = PHONE_REGEX.sub("[TELEFONO_ANONIMIZADO]", cleaned)
    return cleaned.strip()


def extract_auxiliary_features(response_text: str) -> Dict[str, object]:
    """
    Extrae longitud de respuesta y detecta mediante Regex la presencia y lista de métricas
    cuantitativas para respaldar la calificación de la dimensión Resultado en el método STAR.
    """
    if not response_text:
        return {
            "response_length_chars": 0,
            "response_word_count": 0,
            "has_quantitative_metrics": False,
            "quantitative_metrics_count": 0,
            "detected_metrics_list": [],
        }

    words = response_text.strip().split()
    matches: List[str] = [m.group(0).strip() for m in QUANTITATIVE_METRICS_REGEX.finditer(response_text)]

    return {
        "response_length_chars": len(response_text.strip()),
        "response_word_count": len(words),
        "has_quantitative_metrics": len(matches) > 0,
        "quantitative_metrics_count": len(matches),
        "detected_metrics_list": matches[:15],
    }
