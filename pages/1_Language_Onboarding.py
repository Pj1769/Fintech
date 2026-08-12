import streamlit as st
from utils.styling import inject_base_css, banner, footer

st.set_page_config(page_title="KhataSetu | Onboarding", page_icon="🌐", layout="centered")
inject_base_css()

banner("TECH & PRODUCT — Onboarding & Language Selection")

st.markdown("### KhataSetu")
st.markdown("#### Apna Vyapar, Apni Bhasha")
st.caption("Choose your language / भाषा चुनें")

languages = ["Hindi / हिंदी", "English", "Gujarati / ગુજરાતી", "Marwari / मारवाड़ी"]
choice = st.radio(" ", languages, index=0, label_visibility="collapsed")

st.markdown(
    f'<div class="ks-whatsapp-btn">💬 Continue on WhatsApp ({choice.split(" / ")[0]})</div>',
    unsafe_allow_html=True,
)


st.markdown("---")
st.markdown("##### Tell us about your business")
col1, col2 = st.columns(2)
with col1:
    business_name = st.text_input("Business name", placeholder="e.g. Sharma Hardware Store")
    sector = st.selectbox("Sector", ["Trading", "Micro-Manufacturing"])
with col2:
    gstin = st.text_input("GSTIN", placeholder="07ABCDE1234F1Z5", max_chars=15)
    cluster = st.selectbox("Cluster / Location", ["UP - Moradabad", "Rajasthan - Bhilwara", "Gujarat - Morbi"])

turnover_band = st.select_slider(
    "Approximate annual turnover",
    options=["< Rs 40L", "Rs 40L-1Cr", "Rs 1-3Cr", "Rs 3-5Cr", "> Rs 5Cr"],
    value="Rs 1-3Cr",
)

if st.button("Continue →", type="primary"):
    if not business_name or not gstin:
        st.error("Please enter your business name and GSTIN to continue.")
    else:
        st.session_state["onboarding"] = {
            "language": choice.split(" / ")[0],
            "business_name": business_name,
            "gstin": gstin,
            "sector": sector,
            "cluster": cluster,
            "turnover_band": turnover_band,
        }
        st.switch_page("pages/2_Data_Consent.py")

footer()
