import os
import time
import streamlit as st
import requests

from data.applicants import ALL_APPLICANTS, APPLICANT_MAP

API_URL = os.getenv("API_URL", "http://localhost:8000")

I18N = {
    "en": {
        "title": "dLoan — Applicant Screening",
        "load_sample": "Load sample applicant",
        "applicant_id": "Applicant ID",
        "name": "Name",
        "age": "Age",
        "employment_type": "Employment Type",
        "monthly_income": "Monthly Income (THB)",
        "monthly_debt": "Monthly Debt (THB)",
        "loan_amount": "Requested Loan Amount (THB)",
        "credit_history": "Credit History",
        "uploaded_docs": "Uploaded Documents",
        "notes": "Notes",
        "screen_btn": "Screen Applicant",
        "recommendation": "Recommendation",
        "confidence": "Confidence",
        "eligibility_status": "Eligibility Status",
        "debt_to_income": "Debt-to-Income Ratio",
        "risk_flags": "Risk Flags",
        "missing_docs": "Missing Documents",
        "explanation": "Explanation",
        "next_action": "Next Action",
        "feedback": "Feedback",
        "feedback_thanks": "Thank you for your feedback!",
        "feedback_override_label": "Correct recommendation should be:",
        "feedback_comments": "Comments (optional)",
        "feedback_submit": "Submit Feedback",
        "feedback_yes": "👍 Yes, correct",
        "feedback_no": "👎 No, needs correction",
        "complete": "Complete!",
        "queued": "Queued",
        "running": "Running",
        "resp_lang": "💬 Response Language",
        "lang_en": "English",
        "lang_th": "Thai",
    },
}

EMPLOYMENT_LABELS = {
    "employee": "Employee",
    "self-employed": "Self-employed",
    "business_owner": "Business Owner",
    "unemployed": "Unemployed",
}

CREDIT_LABELS = {
    "normal": "Normal",
    "good": "Good",
    "fair": "Fair",
    "default": "Default",
    "severe_default": "Severe Default",
    "bad": "Bad",
}

DOC_LABELS = {
    "id_card": "ID Card",
    "salary_slip": "Salary Slip",
    "bank_statement": "Bank Statement",
}

REC_LABELS = {
    "Proceed": "Proceed",
    "Need More Info": "Need More Info",
    "Reject / Not Eligible": "Reject / Not Eligible",
    "High Risk Review": "High Risk Review",
}

AGENT_LABELS = {
    "intake": "Intake",
    "document": "Document",
    "eligibility": "Eligibility",
    "risk": "Risk",
    "recommendation": "Recommendation",
    "explanation": "Explanation",
}


def _t(key: str) -> str:
    return I18N["en"].get(key, key)


def _opt(mapping: dict, value: str) -> str:
    return mapping.get(value, value)


st.set_page_config(page_title="dLoan — Applicant Screening", layout="wide")
st.title(_t("title"))

if "result" not in st.session_state:
    st.session_state.result = None
if "agent_states" not in st.session_state:
    st.session_state.agent_states = None
if "error" not in st.session_state:
    st.session_state.error = None
if "feedback_submitted" not in st.session_state:
    st.session_state.feedback_submitted = False
if "show_override_form" not in st.session_state:
    st.session_state.show_override_form = False
if "screening_job_id" not in st.session_state:
    st.session_state.screening_job_id = None
if "resp_lang" not in st.session_state:
    st.session_state.resp_lang = "en"
if "form_applicant_id" not in st.session_state:
    st.session_state.form_applicant_id = ""
if "form_name" not in st.session_state:
    st.session_state.form_name = ""
if "form_age" not in st.session_state:
    st.session_state.form_age = 25
if "form_employment_type" not in st.session_state:
    st.session_state.form_employment_type = "employee"
if "form_monthly_income" not in st.session_state:
    st.session_state.form_monthly_income = 0.0
if "form_monthly_debt" not in st.session_state:
    st.session_state.form_monthly_debt = 0.0
if "form_loan_amount" not in st.session_state:
    st.session_state.form_loan_amount = 0.0
if "form_credit_history" not in st.session_state:
    st.session_state.form_credit_history = "normal"
if "form_uploaded_docs" not in st.session_state:
    st.session_state.form_uploaded_docs = []
if "form_notes" not in st.session_state:
    st.session_state.form_notes = ""

st.selectbox(
    _t("resp_lang"),
    ["en", "th"],
    format_func=lambda x: I18N["en"].get("lang_" + x, x),
    key="resp_lang",
)

sample_id = st.selectbox(
    _t("load_sample"),
    [""] + [a["applicant_id"] for a in ALL_APPLICANTS],
    key="sample_selector",
)

current_sample = st.session_state.get("_active_sample")
if sample_id and sample_id != current_sample:
    sample = APPLICANT_MAP[sample_id]
    st.session_state.form_applicant_id = sample["applicant_id"]
    st.session_state.form_name = sample["name"]
    st.session_state.form_age = sample["age"]
    st.session_state.form_employment_type = sample["employment_type"]
    st.session_state.form_monthly_income = float(sample.get("monthly_income", 0))
    st.session_state.form_monthly_debt = float(sample.get("monthly_debt", 0))
    st.session_state.form_loan_amount = float(sample.get("requested_loan_amount", 0))
    st.session_state.form_credit_history = sample["credit_history"]
    st.session_state.form_uploaded_docs = list(sample.get("uploaded_documents", []))
    st.session_state.form_notes = sample.get("notes", "")
    st.session_state._active_sample = sample_id
elif not sample_id and current_sample:
    st.session_state.form_applicant_id = ""
    st.session_state.form_name = ""
    st.session_state.form_age = 25
    st.session_state.form_employment_type = "employee"
    st.session_state.form_monthly_income = 0.0
    st.session_state.form_monthly_debt = 0.0
    st.session_state.form_loan_amount = 0.0
    st.session_state.form_credit_history = "normal"
    st.session_state.form_uploaded_docs = []
    st.session_state.form_notes = ""
    st.session_state._active_sample = ""

with st.form("applicant_form"):
    col1, col2 = st.columns(2)
    with col1:
        applicant_id = st.text_input(_t("applicant_id"), key="form_applicant_id")
        name = st.text_input(_t("name"), key="form_name")
        age = st.number_input(_t("age"), min_value=0, max_value=150, key="form_age")
        employment_type = st.selectbox(
            _t("employment_type"),
            ["employee", "self-employed", "business_owner", "unemployed"],
            format_func=lambda x: EMPLOYMENT_LABELS.get(x, x),
            key="form_employment_type",
        )
        monthly_income = st.number_input(_t("monthly_income"), min_value=0.0, key="form_monthly_income")
        monthly_debt = st.number_input(_t("monthly_debt"), min_value=0.0, key="form_monthly_debt")
    with col2:
        requested_amount = st.number_input(_t("loan_amount"), min_value=0.0, key="form_loan_amount")
        credit_history = st.selectbox(
            _t("credit_history"),
            ["normal", "good", "fair", "default", "severe_default", "bad"],
            format_func=lambda x: CREDIT_LABELS.get(x, x),
            key="form_credit_history",
        )
        uploaded_docs = st.multiselect(
            _t("uploaded_docs"),
            ["id_card", "salary_slip", "bank_statement"],
            format_func=lambda x: DOC_LABELS.get(x, x),
            key="form_uploaded_docs",
        )
        notes = st.text_area(_t("notes"), key="form_notes")

    submitted = st.form_submit_button(_t("screen_btn"), type="primary")

if submitted:
    st.session_state.feedback_submitted = False
    st.session_state.show_override_form = False
    st.session_state.result = None
    st.session_state.agent_states = None
    st.session_state.error = None
    applicant = {
        "applicant_id": st.session_state.form_applicant_id,
        "name": st.session_state.form_name,
        "age": st.session_state.form_age,
        "employment_type": st.session_state.form_employment_type,
        "monthly_income": st.session_state.form_monthly_income,
        "monthly_debt": st.session_state.form_monthly_debt,
        "requested_loan_amount": st.session_state.form_loan_amount,
        "credit_history": st.session_state.form_credit_history,
        "uploaded_documents": st.session_state.form_uploaded_docs,
        "notes": st.session_state.form_notes or None,
        "response_lang": st.session_state.resp_lang,
    }

    try:
        resp = requests.post(f"{API_URL}/screen", json=applicant, timeout=10)
        if resp.status_code == 200:
            st.session_state.screening_job_id = resp.json()["job_id"]
            st.rerun()
        elif resp.status_code == 429:
            st.session_state.error = "API rate limit exceeded. Please wait a moment and try again."
        else:
            st.session_state.error = f"Error: {resp.json().get('detail', 'Unknown error')}"
    except requests.exceptions.ConnectionError:
        st.session_state.error = f"Could not connect to API at {API_URL}. Make sure the API server is running."

if st.session_state.screening_job_id:
    job_id = st.session_state.screening_job_id
    status_resp = requests.get(f"{API_URL}/screen/{job_id}/status", timeout=10)
    if status_resp.status_code == 200:
        data = status_resp.json()
        agent_names = ["intake", "document", "eligibility", "risk", "recommendation", "explanation"]
        done = len(data.get("progress", []))
        progress = done / len(agent_names)

        if data["status"] == "done":
            st.session_state.result = data["result"]
            st.session_state.agent_states = data.get("agent_states", {})
            st.session_state.screening_job_id = None
            st.progress(1.0, text=_t("complete"))
            st.rerun()
        elif data["status"] == "error":
            st.session_state.error = data.get("error", "Screening failed")
            st.session_state.screening_job_id = None
            st.rerun()
        else:
            name = agent_names[done - 1] if done > 0 else "queued"
            label = _opt(AGENT_LABELS, name) if name != "queued" else _t("queued")
            st.progress(progress, text=f"{label}...")
            time.sleep(1.5)
            st.rerun()
    else:
        st.session_state.error = "Failed to get screening status"
        st.session_state.screening_job_id = None
        st.rerun()

if st.session_state.error:
    st.error(st.session_state.error)

if st.session_state.result:
    result = st.session_state.result

    score = {"Proceed": "🟢", "Need More Info": "🟡", "Reject / Not Eligible": "🔴", "High Risk Review": "🟠"}
    icon = score.get(result["recommendation"], "⚪")
    rec_display = _opt(REC_LABELS, result["recommendation"])

    st.divider()
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(_t("recommendation"), f"{icon} {rec_display}")
    with col2:
        st.metric(_t("confidence"), result["confidence"])
    with col3:
        st.metric(_t("eligibility_status"), result.get("eligibility_status", "N/A"))

    if result.get("debt_to_income_ratio"):
        st.metric(_t("debt_to_income"), result["debt_to_income_ratio"])

    if result.get("risk_flags"):
        st.subheader(_t("risk_flags"))
        for flag in result["risk_flags"]:
            st.warning(f"⚠️ {flag}")

    if result.get("missing_documents"):
        st.subheader(_t("missing_docs"))
        for doc in result["missing_documents"]:
            st.info(f"📄 {doc}")

    st.subheader(_t("explanation"))
    st.write(result["explanation"])

    st.subheader(_t("next_action"))
    st.info(result["next_action"])

    st.divider()
    st.subheader(_t("feedback"))

    if st.session_state.feedback_submitted:
        st.success(_t("feedback_thanks"))

    elif st.session_state.show_override_form:
        with st.form("feedback_form"):
            override = st.selectbox(
                _t("feedback_override_label"),
                ["Proceed", "Need More Info", "Reject / Not Eligible", "High Risk Review"],
                format_func=lambda x: REC_LABELS.get(x, x),
            )
            comment = st.text_area(_t("feedback_comments"))
            if st.form_submit_button(_t("feedback_submit"), type="primary"):
                resp = requests.post(f"{API_URL}/feedback", json={
                    "screening_id": result["screening_id"],
                    "correct": False,
                    "override_recommendation": override,
                    "comment": comment or None,
                }, timeout=10)
                if resp.status_code == 200:
                    st.session_state.feedback_submitted = True
                    st.session_state.show_override_form = False
                    st.rerun()

    else:
        col1, col2 = st.columns(2)
        with col1:
            if st.button(_t("feedback_yes"), use_container_width=True):
                resp = requests.post(f"{API_URL}/feedback", json={
                    "screening_id": result["screening_id"],
                    "correct": True,
                }, timeout=10)
                if resp.status_code == 200:
                    st.session_state.feedback_submitted = True
                    st.rerun()
        with col2:
            if st.button(_t("feedback_no"), use_container_width=True):
                st.session_state.show_override_form = True
                st.rerun()

    agent_states = st.session_state.get("agent_states", {})
    if agent_states:
        st.divider()
        st.subheader("Agent Chain")
        saw_skip = False
        agents = [
            ("intake", "Intake Agent", ["valid", "missing_fields"]),
            ("document", "Document Agent", ["valid", "missing_documents"]),
            ("eligibility", "Eligibility Agent", ["eligible", "eligibility_status", "dti_percentage"]),
            ("risk", "Risk Agent", ["risk_level", "risk_flags", "risk_summary"]),
            ("recommendation", "Recommendation Agent", ["recommendation", "confidence", "reasoning"]),
            ("explanation", "Explanation Agent", ["explanation", "next_action"]),
        ]
        for key, label, fields in agents:
            data = agent_states.get(key) or {}
            if not data:
                with st.expander(f"⏭️ {label} — Skipped", expanded=False):
                    st.caption("Pipeline stopped before this agent.")
                saw_skip = True
                continue
            status_icon = "✅"
            if key == "risk" and data.get("risk_flags"):
                status_icon = "⚠️"
            elif key in ("intake", "document") and not data.get("valid", True):
                status_icon = "❌"
            elif key == "eligibility" and not data.get("eligible", True):
                status_icon = "❌"

            with st.expander(f"{status_icon} {label}", expanded=False):
                for f in fields:
                    val = data.get(f)
                    if val is not None:
                        if isinstance(val, list):
                            val = ", ".join(str(v) for v in val) if val else "none"
                        st.caption(f"**{f}:** {val}")
