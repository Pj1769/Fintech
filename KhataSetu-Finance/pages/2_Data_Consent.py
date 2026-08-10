import streamlit as st
from utils.styling import inject_base_css, banner, footer

st.set_page_config(page_title="KhataSetu | Consent", page_icon="🔐", layout="centered")
inject_base_css()

if "onboarding" not in st.session_state:
    st.warning("Please start from the onboarding step.")
    if st.button("← Back to Onboarding"):
        st.switch_page("pages/1_Language_Onboarding.py")
    st.stop()

banner("TECH & PRODUCT — GST, UPI & Account Aggregator Consent")
st.markdown("### Data Consent")
st.caption(f"Business: {st.session_state['onboarding']['business_name']}")

c1, c2 = st.columns(2)
with c1:
    gst_consent = st.checkbox("📄 GST Returns — Last 12 months", value=True)
    aa_consent = st.checkbox("🏦 Bank Account (AA) — via Finvu / OneMoney", value=True)
with c2:
    upi_consent = st.checkbox("💳 UPI Settlement History — 6 months", value=True)
    eway_consent = st.checkbox("🚚 E-Way Bill Trail — Dispatch data", value=True)

st.write("")
all_granted = gst_consent and aa_consent and upi_consent and eway_consent
if st.button("🔒 Grant Secure Consent", type="primary", disabled=not all_granted):
    st.session_state["consent"] = {
        "gst": gst_consent, "aa": aa_consent, "upi": upi_consent, "eway": eway_consent,
    }
    st.success("Consent granted. Pulling your data securely...")
    st.switch_page("pages/3_eKYC_Verification.py")

if not all_granted:
    st.info("All four consents are needed to build your cash-flow score.")

with st.expander("Why this screen matters"):
    st.write(
        "- Purpose-limited, granular consent per RBI's Account Aggregator and Digital Lending "
        "Directions — the borrower sees exactly what is pulled and why.\n"
        "- GSTN's status as a live AA Financial Information Provider lets us pull GST data "
        "through the same consent flow as bank data — one screen, one OTP.\n"
        "- This is the single most important screen in the funnel: it converts a manual "
        "PDF-upload nightmare into a sub-5-minute, revocable, bank-grade consent."
    )

footer()
