import json
import os
import streamlit as st
import requests

API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(page_title="dLoan — Dashboard", layout="wide")

def _fetch_summary():
    return requests.get(f"{API_URL}/audit/summary", timeout=10).json()

def _fetch_recent(limit: int = 15):
    return requests.get(f"{API_URL}/audit?limit={limit}&offset=0", timeout=10).json()

st.title("Screening Dashboard")

try:
    summary = _fetch_summary()
except Exception:
    st.warning("Dashboard unavailable (API not running)")
    st.stop()

# ── Row 1: Metric cards ──
c1, c2, c3 = st.columns(3)
with c1:
    st.metric("Total Screenings", summary["total"])
with c2:
    st.metric("Officer Agreement", f'{summary["agreement_pct"]}%')
with c3:
    st.metric("Overrides", summary.get("overrides_count", 0))

# ── Row 2: Charts ──
col_left, col_right = st.columns(2)
with col_left:
    st.subheader("By Outcome")
    st.bar_chart(summary["by_outcome"], use_container_width=True)
with col_right:
    st.subheader("Top Risk Flags")
    flags = summary.get("top_risk_flags", [])
    if flags:
        for flag, count in flags:
            st.write(f"`{count}x` {flag}")
    else:
        st.caption("No risk flags recorded yet.")

st.divider()

# ── Row 3: Tables ──
col_left, col_right = st.columns(2)
with col_left:
    st.subheader("Recent Screenings")
    try:
        recent = _fetch_recent(15)
    except Exception:
        st.info("Could not load recent screenings")
        recent = []

    if not recent:
        st.caption("No screenings yet.")
    else:
        for sr in recent:
            rd = sr.get("result_data", {})
            if isinstance(rd, str):
                try:
                    rd = json.loads(rd)
                except Exception:
                    rd = {}
            rec = rd.get("recommendation", "?")
            st.caption(f"{sr['created_at'][:16]}  `{sr['applicant_id']}` {rec}")

with col_right:
    st.subheader("Recent Overrides")
    overrides = summary.get("recent_overrides", [])
    if not overrides:
        st.caption("All screenings marked correct so far.")
    else:
        for ov in overrides:
            st.write(f"`{ov['applicant_id']}` AI: {ov['ai_rec']} → Officer: {ov['override']}")
            if ov["comment"]:
                st.caption(f"_{ov['comment']}_")
            st.caption(f"{ov['created_at'][:16]}")
