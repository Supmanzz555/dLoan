from typing import TypedDict, Literal, Callable
from langgraph.graph import StateGraph, START, END

from agents.intake_agent import run as run_intake
from agents.document_agent import run as run_document
from agents.eligibility_agent import run as run_eligibility
from agents.risk_agent import run as run_risk
from agents.recommendation_agent import run as run_recommendation
from agents.explanation_agent import run as run_explanation
from models.schemas import ApplicantInput, ScreeningResult
from utils.rules import validate_applicant


class AgentState(TypedDict):
    applicant: dict
    intake_result: dict | None
    document_result: dict | None
    eligibility_result: dict | None
    risk_result: dict | None
    recommendation_result: dict | None
    explanation_result: dict | None
    should_stop: bool
    stop_reason: str


def intake_node(state: AgentState) -> dict:
    result = run_intake(state["applicant"])
    updates = {"intake_result": result, "should_stop": False, "stop_reason": ""}
    if not result["valid"]:
        updates["should_stop"] = True
        updates["stop_reason"] = "Need More Info"
    return updates


def document_node(state: AgentState) -> dict:
    result = run_document(state["applicant"])
    updates = {"document_result": result}
    if not result["valid"]:
        updates["should_stop"] = True
        updates["stop_reason"] = "Need More Info"
    return updates


def eligibility_node(state: AgentState) -> dict:
    result = run_eligibility(state["applicant"])
    return {"eligibility_result": result}


def risk_node(state: AgentState) -> dict:
    prior = {
        "intake": state["intake_result"],
        "document": state["document_result"],
        "eligibility": state["eligibility_result"],
    }
    result = run_risk(state["applicant"], prior)
    return {"risk_result": result}


def recommendation_node(state: AgentState) -> dict:
    prior = {
        "intake": state["intake_result"],
        "document": state["document_result"],
        "eligibility": state["eligibility_result"],
        "risk": state["risk_result"],
    }
    result = run_recommendation(state["applicant"], prior)
    return {"recommendation_result": result}


def explanation_node(state: AgentState) -> dict:
    prior = {
        "intake": state["intake_result"],
        "document": state["document_result"],
        "eligibility": state["eligibility_result"],
        "risk": state["risk_result"],
        "recommendation": state["recommendation_result"],
    }
    result = run_explanation(state["applicant"], prior)
    return {"explanation_result": result}


def route_after_intake(state: AgentState) -> Literal["document", END]:
    if state["should_stop"]:
        return END
    return "document"


def route_after_document(state: AgentState) -> Literal["eligibility", END]:
    if state["should_stop"]:
        return END
    return "eligibility"


def build_graph() -> StateGraph:
    graph = StateGraph(AgentState)

    graph.add_node("intake", intake_node)
    graph.add_node("document", document_node)
    graph.add_node("eligibility", eligibility_node)
    graph.add_node("risk", risk_node)
    graph.add_node("recommendation", recommendation_node)
    graph.add_node("explanation", explanation_node)

    graph.add_edge(START, "intake")
    graph.add_conditional_edges("intake", route_after_intake)
    graph.add_conditional_edges("document", route_after_document)
    graph.add_edge("eligibility", "risk")
    graph.add_edge("risk", "recommendation")
    graph.add_edge("recommendation", "explanation")
    graph.add_edge("explanation", END)

    return graph.compile()


def _build_risk_flags(risk: dict, rule_check: dict, applicant: dict) -> tuple[list, bool]:
    dti_rule = rule_check["dti_ratio"]
    monthly_income = applicant.get("monthly_income", 0)
    loan_amount = applicant.get("requested_loan_amount", 0)
    final_risk_flags = []
    llm_flags = list(risk.get("risk_flags", []))

    for flag in llm_flags:
        if "debt-to-income" in flag.lower() or "dti" in flag.lower():
            if dti_rule is None or dti_rule <= 0.6:
                continue
        if "loan amount" in flag.lower() and "income" in flag.lower():
            if monthly_income > 0 and loan_amount / monthly_income <= 12:
                continue
        final_risk_flags.append(flag)

    if dti_rule is not None and dti_rule > 0.6:
        flag = "Debt-to-income ratio exceeds preferred threshold"
        if flag not in final_risk_flags:
            final_risk_flags.append(flag)

    if "severe" in rule_check.get("credit_note", "") or "default" in rule_check.get("credit_note", ""):
        flag = "Credit history shows recent default"
        if flag not in final_risk_flags:
            final_risk_flags.append(flag)

    if monthly_income > 0 and loan_amount / monthly_income > 12:
        flag = "Requested loan amount is high compared with monthly income"
        if flag not in final_risk_flags:
            final_risk_flags.append(flag)

    return final_risk_flags, len(final_risk_flags) > 0


def _override_recommendation(rec: dict, rule_check: dict, hard_rule_failed: bool, has_risk_flags: bool) -> str:
    rec_llm = rec.get("recommendation", "Proceed")
    if hard_rule_failed and rec_llm in ("Proceed", "High Risk Review", "Need More Info"):
        return "Reject / Not Eligible"
    if not hard_rule_failed and rule_check["dti_ratio"] is not None and rule_check["dti_ratio"] > 0.6:
        return "High Risk Review"
    if not hard_rule_failed and has_risk_flags:
        return "High Risk Review"
    if not hard_rule_failed and rule_check["dti_ratio"] is not None and rule_check["dti_ratio"] <= 0.6 and "default" not in rule_check["credit_note"] and not rule_check["missing_docs"]:
        return "Proceed"
    if not hard_rule_failed and not has_risk_flags and rec_llm == "Reject / Not Eligible":
        return "Proceed"
    return rec_llm


def _finalize_explanation(rec: dict, expl: dict, rule_check: dict, applicant: dict, rec_llm: str, final_risk_flags: list) -> tuple[str, str]:
    explanation = expl.get("explanation", "")
    next_action = expl.get("next_action", "")
    rec_original_llm = rec.get("recommendation", "")

    if rec_original_llm == rec_llm:
        return explanation, next_action

    name = applicant.get("name", "Applicant")
    if rec_llm == "Reject / Not Eligible":
        issues = "; ".join(rule_check["issues"]) if rule_check["issues"] else "fails eligibility criteria"
        return f"{name} fails hard eligibility rules: {issues}.", "Notify applicant that eligibility requirements are not met."
    if rec_llm == "Proceed":
        return f"{name} meets all eligibility criteria with no significant risk flags.", "Proceed to manual review by credit officer."
    flags = final_risk_flags or rule_check["issues"]
    flags_text = "; ".join(flags) if flags else "risk signals detected"
    return f"{name} has risk signals requiring careful manual review: {flags_text}.", "Assign to senior credit officer for manual review."


def screen_applicant(applicant: dict, progress_callback: Callable[[str], None] | None = None) -> tuple[ScreeningResult, dict]:
    graph = build_graph()
    initial = {
        "applicant": applicant,
        "intake_result": None,
        "document_result": None,
        "eligibility_result": None,
        "risk_result": None,
        "recommendation_result": None,
        "explanation_result": None,
        "should_stop": False,
        "stop_reason": "",
    }

    state = initial.copy()
    for event in graph.stream(initial):
        for node_name, node_output in event.items():
            state.update(node_output)
            if progress_callback:
                progress_callback(node_name)

    agent_states = {
        "intake": state.get("intake_result"),
        "document": state.get("document_result"),
        "eligibility": state.get("eligibility_result"),
        "risk": state.get("risk_result"),
        "recommendation": state.get("recommendation_result"),
        "explanation": state.get("explanation_result"),
        "should_stop": state.get("should_stop"),
        "stop_reason": state.get("stop_reason", ""),
    }

    if state.get("should_stop"):
        document = state.get("document_result", {}) or {}
        missing_docs = document.get("missing_documents", [])
        reason = state.get("stop_reason", "Need More Info")

        return ScreeningResult(
            applicant_id=applicant["applicant_id"],
            recommendation=reason,
            confidence="High",
            eligibility_status="Incomplete application",
            risk_flags=[],
            missing_documents=missing_docs,
            explanation="Application is incomplete. Required information or documents are missing.",
            next_action="Contact applicant to provide missing information.",
        ), agent_states

    rec = state.get("recommendation_result", {}) or {}
    risk = state.get("risk_result", {}) or {}
    elig = state.get("eligibility_result", {}) or {}
    expl = state.get("explanation_result", {}) or {}

    rule_check = validate_applicant(ApplicantInput(**applicant))
    hard_rule_failed = len([i for i in rule_check["issues"] if "DTI" not in i and "credit" not in i]) > 0

    final_risk_flags, has_risk_flags = _build_risk_flags(risk, rule_check, applicant)

    llm_says_ineligible = elig.get("eligible") is False
    if hard_rule_failed and not llm_says_ineligible:
        elig = {"eligible": False, "issues": rule_check["issues"], "eligibility_status": "Ineligible per rules"}
    elif not hard_rule_failed and llm_says_ineligible:
        elig = {"eligible": True, "issues": [], "eligibility_status": "Passes all rules"}

    rec_llm = _override_recommendation(rec, rule_check, hard_rule_failed, has_risk_flags)

    dti_label = elig.get("dti_percentage", "")
    if not dti_label and rule_check["dti_ratio"] is not None:
        dti_label = f"{rule_check['dti_ratio'] * 100:.0f}%"

    explanation, next_action = _finalize_explanation(rec, expl, rule_check, applicant, rec_llm, final_risk_flags)

    disclaimer = "Requires human review: This screening is AI-generated and must be verified by a credit officer before any decision."
    if disclaimer not in explanation:
        explanation += f"\n\n{disclaimer}"

    return ScreeningResult(
        applicant_id=applicant["applicant_id"],
        recommendation=rec_llm,
        confidence=rec.get("confidence", "Medium"),
        eligibility_status=elig.get("eligibility_status", ""),
        debt_to_income_ratio=dti_label,
        risk_flags=final_risk_flags,
        missing_documents=[],
        explanation=explanation,
        next_action=next_action,
    ), agent_states


if __name__ == "__main__":
    from data.applicants import APP001, APP004, APP005, APP007, APP008, APP013

    for app in [APP001, APP004, APP005, APP007, APP008, APP013]:
        result, _ = screen_applicant(app)
        print(f"\n{result.applicant_id} — {result.recommendation} ({result.confidence})")
        print(f"  Status: {result.eligibility_status}")
        if result.risk_flags:
            print(f"  Flags: {result.risk_flags}")
        if result.missing_documents:
            print(f"  Missing: {result.missing_documents}")
        print(f"  Action: {result.next_action}")
