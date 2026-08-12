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


def format_masked_aadhaar(raw: str) -> str:
    """Take raw digits typed so far, mask first 8, keep last 4 visible,
    format as xxxx xxxx 5458."""
    digits = "".join(c for c in raw if c.isdigit())[:12]
    if not digits:
        return ""
    masked_chars = []
    for i, ch in enumerate(digits):
        masked_chars.append(ch if i >= 8 else "x")
    grouped = " ".join(
        "".join(masked_chars[i:i + 4]) for i in range(0, len(masked_chars), 4)
    )
    return grouped


aadhaar_raw = st.text_input(
    "Aadhaar Number",
    placeholder="xxxx xxxx 4821",
    max_chars=14,
)

masked_preview = format_masked_aadhaar(aadhaar_raw)
if masked_preview:
    st.caption(f"Masked: **{masked_preview}**")

pan = st.text_input("PAN (auto-fetched)", value="ABCDE1234F", disabled=True)
st.caption("✅ PAN verified")

st.write("")
st.markdown("**Live selfie**")
selfie = st.camera_input("Tap to capture live selfie")
st.write("")

if st.button("✅ Verify & Continue", type="primary"):
    digits = "".join(c for c in aadhaar_raw if c.isdigit())
    if len(digits) < 12:
        st.error("Please enter a valid 12-digit Aadhaar number.")
    else:
        st.session_state["ekyc"] = {
            "aadhaar_masked": format_masked_aadhaar(aadhaar_raw),
            "pan": pan,
            "selfie_captured": selfie is not None,
        }
        st.success("Identity verified.")
        st.switch_page("pages/4_Credit_Offer.py")

footer()
