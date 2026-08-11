import streamlit as st
from datetime import datetime, timedelta
from utils.styling import inject_base_css, banner, footer
from utils.db import update_borrower, add_repayment

st.set_page_config(page_title="KhataSetu | e-Sign", page_icon="✍️", layout="centered")
inject_base_css()

if "borrower_id" not in st.session_state:
    st.warning("Please accept your offer first.")
    if st.button("← Back to Offer"):
        st.switch_page("pages/4_Credit_Offer.py")
    st.stop()

banner("TECH & PRODUCT — e-Sign & Disbursement")
st.markdown("### Almost Done")
st.progress(4 / 4, text="Step 4 of 4")

result = st.session_state["offer_result"]
sanctioned = result["sanctioned_limit"]

st.markdown("#### Loan Agreement")
st.write("Aadhaar e-Sign | OTP verification")
otp = st.text_input("Enter OTP sent to your registered mobile", max_chars=6, placeholder="123456")

if "esigned" not in st.session_state:
    st.session_state["esigned"] = False

if not st.session_state["esigned"]:
    if st.button("Verify OTP & e-Sign", type="primary"):
        if otp and len(otp) >= 4:
            st.session_state["esigned"] = True
            st.rerun()
        else:
            st.error("Please enter a valid OTP.")
else:
    st.success("✅ e-signature captured")
    draw_amount = st.slider(
        "How much would you like to draw now from your sanctioned limit?",
        min_value=int(sanctioned * 0.2), max_value=int(sanctioned), value=int(sanctioned * 0.5), step=1000,
    )
    if st.button("💸 Disburse Funds", type="primary"):
        next_emi = round(draw_amount / 9 * (1 + result["interest_rate"] / 100 / 12 * 6), -2)
        next_due = (datetime.now() + timedelta(days=30)).strftime("%d %b %Y")
        update_borrower(st.session_state["borrower_id"], {
            "offer_accepted": 1,
            "disbursed": 1,
            "disbursed_amount": draw_amount,
            "available_limit": sanctioned - draw_amount,
            "next_emi": next_emi,
            "next_emi_due": next_due,
        })
        add_repayment(st.session_state["borrower_id"], 1, next_emi, "Upcoming", next_due)
        st.session_state["disbursed_amount"] = draw_amount
        st.session_state["masked_account"] = "XX" + st.session_state["ekyc"]["aadhaar_masked"][-4:]
        st.balloons()
        st.markdown(
            f'<div class="ks-card">✅ <b>Funds Credited</b><br>'
            f'₹{draw_amount:,.0f} credited to A/c {st.session_state["masked_account"]} via escrow</div>',
            unsafe_allow_html=True,
        )
        if st.button("View Repayment Schedule →", type="primary"):
            st.switch_page("pages/6_My_Vyapar_Line.py")

with st.expander("Why this screen matters"):
    st.write(
        "- Aadhaar e-Sign closes the loop without a single physical signature or branch visit — "
        "core to the sub-48-hour promise.\n"
        "- Disbursal moves through an escrow account straight to the borrower's own bank account, "
        "never to a third party, per RBI's digital lending disbursal rule.\n"
        "- A clear confirmation moment builds trust for a first-time formal borrower and sets up "
        "the repayment relationship that follows."
    )

footer()
