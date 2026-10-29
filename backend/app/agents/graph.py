from langgraph.graph import END, StateGraph
from app.config import settings
from app.agents.state import InterviewGraphState
from app.agents.evaluator import evaluate_candidate_turn_node
from app.agents.interviewer import (
    advance_to_next_topic_node,
    finalize_interview_node,
    generate_followup_question_node,
)


def route_after_evaluation(state: InterviewGraphState) -> str:
    """
    Arista condicional de LangGraph:
    1. Si se alcanzó el número total de preguntas de la sesión -> finalizar_entrevista.
    2. Si allow_followups está habilitado, no estamos ya en una repregunta, y Acción o Resultado < umbral -> profundizar_pregunta.
    3. En cualquier otro caso (por defecto para priorizar preguntas aleatorias sin repreguntas innecesarias) -> pasar_a_siguiente_tema.
    """
    current_idx = state.get("current_question_index", 0)
    total_q = state.get("total_questions", 5)

    eval_res = state.get("evaluation_result", {})
    allow_followups = state.get("allow_followups", settings.ENABLE_FOLLOWUP_QUESTIONS)
    is_followup = state.get("is_followup_turn", False)

    low_star = (
        eval_res.get("star_action", 3) < settings.FOLLOWUP_STAR_THRESHOLD
        or eval_res.get("star_result", 3) < settings.FOLLOWUP_STAR_THRESHOLD
    )

    if allow_followups and not is_followup and low_star:
        return "profundizar_pregunta"

    if current_idx + 1 >= total_q:
        return "finalizar_entrevista"

    return "pasar_a_siguiente_tema"


def build_interview_graph():
    """
    Construye y compila el grafo de estados cíclico/condicional en LangGraph
    que coordina al Agente Evaluador y al Agente Entrevistador.
    """
    workflow = StateGraph(InterviewGraphState)

    workflow.add_node("evaluador", evaluate_candidate_turn_node)
    workflow.add_node("profundizar_pregunta", generate_followup_question_node)
    workflow.add_node("pasar_a_siguiente_tema", advance_to_next_topic_node)
    workflow.add_node("finalizar_entrevista", finalize_interview_node)

    workflow.set_entry_point("evaluador")

    workflow.add_conditional_edges(
        "evaluador",
        route_after_evaluation,
        {
            "profundizar_pregunta": "profundizar_pregunta",
            "pasar_a_siguiente_tema": "pasar_a_siguiente_tema",
            "finalizar_entrevista": "finalizar_entrevista",
        },
    )

    workflow.add_edge("profundizar_pregunta", END)
    workflow.add_edge("pasar_a_siguiente_tema", END)
    workflow.add_edge("finalizar_entrevista", END)

    return workflow.compile()


interview_graph = build_interview_graph()
