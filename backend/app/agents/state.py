from typing import Any, Dict, List, Optional, TypedDict


class InterviewGraphState(TypedDict):
    session_id: str
    career_code: str
    target_role: str
    seniority_level: str
    anonymized_cv_text: str
    job_description_text: str
    current_question_index: int
    total_questions: int
    current_question_text: str
    candidate_response: str
    auxiliary_features: Dict[str, Any]
    allow_followups: bool
    is_followup_turn: bool
    evaluation_result: Dict[str, Any]
    session_state: str  # 'pasar_a_siguiente_tema' | 'profundizar_pregunta' | 'finalizar_entrevista'
    next_question_bank_text: Optional[str]
    next_interviewer_message: str
    evaluation_latency_ms: int
    json_format_valid: bool
