import streamlit as st
import pandas as pd
from utils.styling import inject_base_css, banner, footer
from utils.synthetic_data import generate_borrower_data
from utils.scoring_engine import score_borrower
from utils.db import insert_borrower
import json
from datetime import datetime

st.set_page_config(page_title="KhataSetu | Credit Offer", page_icon="💰", layout="centered")
inject_base_css()

if "ekyc" not in st.session_state:
    st.warning("Please complete e-KYC first.")
    if st.button("← Back to e-KYC"):
        st.switch_page("pages/3_eKYC_Verification.py")
    st.stop()

banner("TECH & PRODUCT — Alt-Data Underwriting Engine & Credit Offer")
st.markdown("### Your Offer")
st.progress(3 / 4, text="Step 3 of 4")

if "synthetic_data" not in st.session_state:
    with st.spinner("Pulling GST, UPI, e-way bill & AA data... provisional offer in under 15 minutes"):
        st.session_state["synthetic_data"] = generate_borrower_data()

synth = st.session_state["synthetic_data"]
result = score_borrower(synth)
st.session_state["offer_result"] = result

st.markdown("#### Cash-Flow Scorecard")
comp = result["sub_scores"]
df = pd.DataFrame({
    "Signal": ["GST Filing Consistency", "UPI Inflow Trend", "E-Way Bill Momentum",
               "AA Bank Cash-Flow", "Bureau (if any)"],
    "Score (0-100)": [comp["gst"], comp["upi"], comp["eway"], comp["aa"], comp["bureau"]],
})
st.bar_chart(df.set_index("Signal"))
st.caption(f"Composite Cash-Flow Score: **{result['score']}/100** — {result['risk_band']}")

st.markdown("---")

if result["sanctioned_limit"] <= 0:
    st.error("Based on current cash-flow signals, this application needs manual credit review. "
              "No automated offer can be extended at this time.")
    footer()
    st.stop()

c1, c2, c3 = st.columns(3)
c1.metric("Sanctioned Limit", f"₹{result['sanctioned_limit']:,.0f}")
c2.metric("Interest rate (blended)", f"{result['interest_rate']}% p.a.")
c3.metric("APR (all-in)", f"{result['apr']}%")

c4, c5 = st.columns(2)
c4.metric("Processing fee", f"{result['processing_fee_pct']}%")
c5.metric("Tenure", "12 months, revolving")

st.markdown("#### Key Facts Statement (KFS)")
kfs_df = pd.DataFrame({
    "Field": ["Sanctioned Limit", "Interest Rate (blended)", "Processing Fee", "Tenure", "APR (all-in)",
              "Security", "Lenders behind this loan"],
    "Value": [f"₹{result['sanctioned_limit']:,.0f}", f"{result['interest_rate']}% p.a.",
              f"{result['processing_fee_pct']}% of sanctioned limit", "12 months, revolving",
              f"{result['apr']}%", "Hypothecation of stock/receivables + UPI Autopay mandate",
              "Bank partner (90%) + KhataSetu NBFC-LSP (10%) — single blended rate shown"],
})
st.table(kfs_df.set_index("Field"))
st.caption("Shown in full, in plain language, as mandated by RBI's Digital Lending Directions, 2025. "
           "A cooling-off window applies per KhataSetu's board-approved policy.")

if st.button("✅ Accept Offer", type="primary"):
    borrower_data = {
        "business_name": st.session_state["onboarding"]["business_name"],
        "gstin": st.session_state["onboarding"]["gstin"],
        "sector": st.session_state["onboarding"]["sector"],
        "turnover_band": st.session_state["onboarding"]["turnover_band"],
        "cluster": st.session_state["onboarding"]["cluster"],
        "language": st.session_state["onboarding"]["language"],
        "aadhaar_masked": st.session_state["ekyc"]["aadhaar_masked"],
        "pan": st.session_state["ekyc"]["pan"],
        "kyc_verified": 1,
        "consent_json": json.dumps(st.session_state["consent"]),
        "synthetic_data_json": json.dumps(synth),
        "score": result["score"],
        "risk_band": result["risk_band"],
        "sanctioned_limit": result["sanctioned_limit"],
        "available_limit": result["sanctioned_limit"],
        "interest_rate": result["interest_rate"],
        "processing_fee_pct": result["processing_fee_pct"],
        "apr": result["apr"],
        "offer_accepted": 1,
        "disbursed": 0,
        "disbursed_amount": 0,
        "next_emi": 0,
        "next_emi_due": "",
        "autopay": 1,
        "npa_flag": 0,
        "dpd": 0,
        "created_at": datetime.now().isoformat(),
    }
    borrower_id = insert_borrower(borrower_data)
    st.session_state["borrower_id"] = borrower_id
    st.success("Offer accepted!")
    st.switch_page("pages/5_eSign_Disbursement.py")

with st.expander("Why this screen matters"):
    st.write(
        "- The Key Facts Statement is shown in full, in plain language, exactly as mandated by "
        "RBI's Digital Lending Directions — APR, fees and tenure upfront, no fine print.\n"
        "- One blended rate is shown even though two lenders (bank + KhataSetu) sit behind the "
        "loan, as required under the Co-Lending Directions, 2025.\n"
        "- A visible cooling-off window lets the borrower exit penalty-free within the "
        "RE's board-approved period."
    )

footer()
