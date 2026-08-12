import streamlit as st
from utils.styling import inject_base_css, banner, note, footer, chip
from utils.db import init_db, seed_demo_borrowers

st.set_page_config(page_title="KhataSetu Finance", page_icon="🪙", layout="wide")
init_db()
seed_demo_borrowers(25)   # change to 1000 to load the full dataset
inject_base_css()

st.markdown(
    '<div style="color:#1F6B4A;font-weight:600;">SME LENDING &nbsp;|&nbsp; SEED ROUND &nbsp;|&nbsp; PROTOTYPE</div>',
    unsafe_allow_html=True,
)
st.title("KhataSetu Finance")
st.subheader("Turning the village ledger into a formal credit line.")
st.write(
    "A GST + UPI + Account Aggregator underwriting engine for New-to-Credit trader "
    "and micro-manufacturing MSMEs in rural and semi-urban India."
)
st.markdown("---")

note("This is a working prototype of the KhataSetu product experience described in the "
     "investor pitch deck. Choose a persona below to explore the app.")

col1, col2 = st.columns(2)
with col1:
    st.markdown("### 👤 I'm a Borrower")
    st.write("Walk through the borrower journey: language selection → data consent → "
             "e-KYC → credit offer → e-sign & disbursement → repayment dashboard.")
    if st.button("Start Borrower Journey →", type="primary", use_container_width=True):
        st.switch_page("pages/1_Language_Onboarding.py")
with col2:
    st.markdown("### 🏦 I'm the Lender / Ops Team")
    st.write("View the portfolio: collections & NPA early-warning dashboard, and "
             "investor-facing business metrics (AUM build, unit economics).")
    b1, b2 = st.columns(2)
    with b1:
        if st.button("Ops Dashboard →", use_container_width=True):
            st.switch_page("pages/7_Lender_Ops_Dashboard.py")
    with b2:
        if st.button("Investor Metrics →", use_container_width=True):
            st.switch_page("pages/8_Investor_Metrics.py")

st.markdown("---")
chip("GST"); chip("UPI"); chip("Account Aggregator"); chip("e-Way Bill"); chip("Co-Lending"); chip("RBI Compliant")
footer()
