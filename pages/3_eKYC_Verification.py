import streamlit as st
from utils.styling import inject_base_css, banner, footer

st.set_page_config(page_title="KhataSetu | e-KYC", page_icon="🪪", layout="centered")
inject_base_css()

if "consent" not in st.session_state:
    st.warning("Please complete the consent step first.")
    if st.button("← Back to Consent"):
        st.switch_page("pages/2_Data_Consent.py")
    st.stop()

banner("TECH & PRODUCT — Document Upload & e-KYC")
st.markdown("### Verify Identity")
st.progress(2 / 4, text="Step 2 of 4")

aadhaar = st.text_input("Aadhaar Number", placeholder="XXXX XXXX 4821", max_chars=14)
pan = st.text_input("PAN (auto-fetched)", value="ABCDE1234F", disabled=True)
st.caption("✅ PAN verified")

st.write("")
st.markdown("**Live selfie**")
selfie = st.camera_input("Tap to capture live selfie")

st.write("")
if st.button("✅ Verify & Continue", type="primary"):
    if not aadhaar or len(aadhaar.replace(" ", "")) < 4:
        st.error("Please enter a valid Aadhaar number.")
    else:
        st.session_state["ekyc"] = {
            "aadhaar_masked": "XXXX XXXX " + aadhaar.replace(" ", "")[-4:],
            "pan": pan,
            "selfie_captured": selfie is not None,
        }
        st.success("Identity verified.")
        st.switch_page("pages/4_Credit_Offer.py")

footer()
