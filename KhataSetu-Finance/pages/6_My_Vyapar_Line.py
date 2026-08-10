import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from utils.styling import inject_base_css, banner, footer
from utils.db import get_borrower, get_repayments, add_repayment, update_borrower, get_all_borrowers

st.set_page_config(page_title="KhataSetu | My Vyapar Line", page_icon="📊", layout="centered")
inject_base_css()

banner("MY VYAPAR LINE — Repayment Dashboard")

if "borrower_id" not in st.session_state:
    all_b = get_all_borrowers()
    if not all_b:
        st.info("No borrowers yet. Complete the borrower journey first, or come back after seeding demo data.")
        st.stop()
    options = {f'{b["business_name"]} (ID {b["id"]})': b["id"] for b in all_b if b["disbursed"]}
    if not options:
        st.info("No disbursed borrowers yet.")
        st.stop()
    picked = st.selectbox("View dashboard for:", list(options.keys()))
    st.session_state["borrower_id"] = options[picked]

borrower = get_borrower(st.session_state["borrower_id"])
if not borrower or not borrower["disbursed"]:
    st.warning("This borrower hasn't been disbursed yet.")
    st.stop()

st.markdown(f"### {borrower['business_name']}")
st.caption(f"{borrower['cluster']} · {borrower['sector']} · Risk band: {borrower['risk_band']}")

available = borrower["available_limit"]
sanctioned = borrower["sanctioned_limit"]
st.progress(min(available / sanctioned, 1.0), text=f"Available Limit: ₹{available:,.0f} of ₹{sanctioned:,.0f}")

c1, c2, c3 = st.columns(3)
c1.metric("Next EMI", f"₹{borrower['next_emi']:,.0f}")
c2.metric("Due", borrower["next_emi_due"] or "—")
c3.metric("Autopay", "UPI Autopay ON" if borrower["autopay"] else "OFF")

st.markdown("---")
st.markdown("#### Repayment History")
reps = get_repayments(borrower["id"])
if reps:
    df = pd.DataFrame(reps)[["cycle_no", "amount", "status", "paid_on"]]
    df.columns = ["Cycle", "Amount (₹)", "Status", "Date"]
    st.bar_chart(df.set_index("Cycle")["Amount (₹)"])
    st.dataframe(df, use_container_width=True, hide_index=True)
else:
    st.info("No repayment cycles yet.")

st.caption(
    "A visible repayment-history bar chart reinforces the credit-ladder story: on-time cycles "
    "unlock a higher limit at a lower rate. This dashboard doubles as the early-warning surface — "
    "a missed bar here is the same signal that triggers the collections workflow."
)

st.markdown("---")
col1, col2 = st.columns(2)
with col1:
    if st.button("💳 Repay Now", type="primary", use_container_width=True):
        add_repayment(borrower["id"], len(reps) + 1, borrower["next_emi"], "Paid on time",
                      datetime.now().strftime("%d %b %Y"))
        update_borrower(borrower["id"], {
            "available_limit": min(sanctioned, available + borrower["next_emi"] * 0.6),
            "next_emi_due": (datetime.now() + timedelta(days=30)).strftime("%d %b %Y"),
            "dpd": 0,
        })
        st.success("Payment recorded. Your available limit has been updated.")
        st.rerun()
with col2:
    if st.button("⬆️ Raise Limit", use_container_width=True):
        on_time = sum(1 for r in reps if r["status"] == "Paid on time")
        if reps and on_time / len(reps) >= 0.7:
            new_limit = round(sanctioned * 1.15, -3)
            update_borrower(borrower["id"], {
                "sanctioned_limit": new_limit,
                "available_limit": available + (new_limit - sanctioned),
                "interest_rate": max(16.0, borrower["interest_rate"] - 0.5),
            })
            st.success(f"Great repayment history! Limit raised to ₹{new_limit:,.0f} and rate improved — "
                       "the credit ladder in action.")
            st.rerun()
        else:
            st.warning("Limit increases unlock after a consistent on-time repayment history.")

footer()
