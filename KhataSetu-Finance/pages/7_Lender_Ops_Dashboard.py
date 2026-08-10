import streamlit as st
import pandas as pd
from utils.styling import inject_base_css, banner, subbanner, footer
from utils.db import get_all_borrowers, get_alerts

st.set_page_config(page_title="KhataSetu | Ops Dashboard", page_icon="🏦", layout="wide")
inject_base_css()

banner("LENDER / OPS DASHBOARD — Portfolio, Collections & NPA Management")

borrowers = get_all_borrowers()
if not borrowers:
    st.info("No borrowers yet. Visit the Home page to seed demo data.")
    st.stop()

df = pd.DataFrame(borrowers)
disbursed_df = df[df["disbursed"] == 1]

total_aum = disbursed_df["disbursed_amount"].sum()
active_borrowers = len(disbursed_df)
npa_count = disbursed_df["npa_flag"].sum()
npa_rate = (npa_count / active_borrowers * 100) if active_borrowers else 0

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total AUM", f"₹{total_aum:,.0f}")
c2.metric("Active Borrowers", f"{active_borrowers:,}")
c3.metric("NPA Rate", f"{npa_rate:.1f}%", delta=f"{npa_rate - 4:.1f} pts vs 4% target",
          delta_color="inverse")
c4.metric("Avg Sanctioned Limit", f"₹{df['sanctioned_limit'].mean():,.0f}")

st.markdown("---")

col_a, col_b = st.columns([1.3, 1])
with col_a:
    subbanner("Cluster-wise Portfolio")
    cluster_summary = disbursed_df.groupby("cluster").agg(
        borrowers=("id", "count"), aum=("disbursed_amount", "sum")
    ).reset_index()
    st.bar_chart(cluster_summary.set_index("cluster")["aum"])
    st.dataframe(cluster_summary.rename(columns={"cluster": "Cluster", "borrowers": "Borrowers", "aum": "AUM (₹)"}),
                 hide_index=True, use_container_width=True)

with col_b:
    subbanner("Co-Lending Split (90 / 10)")
    bank_share = total_aum * 0.9
    khatasetu_share = total_aum * 0.1
    split_df = pd.DataFrame({"Partner": ["Bank / SFB (90%)", "KhataSetu NBFC-LSP (10%)"],
                              "Amount": [bank_share, khatasetu_share]})
    st.bar_chart(split_df.set_index("Partner"))
    st.caption(f"Bank @ ~9.5% cost of funds: ₹{bank_share:,.0f}  ·  "
               f"KhataSetu @ ~13%: ₹{khatasetu_share:,.0f}")

st.markdown("---")
subbanner("Risk Band Distribution")
risk_summary = df["risk_band"].value_counts().reset_index()
risk_summary.columns = ["Risk Band", "Count"]
st.bar_chart(risk_summary.set_index("Risk Band"))

st.markdown("---")
banner("Early Warning Signals — Leading Indicators")
st.write(
    "🔻 UPI inflow decline >20% (30d)  ·  📅 GST filing delayed  ·  🚚 E-way bill volume drop  ·  "
    "🔁 First UPI Autopay bounce"
)

alerts = get_alerts()
if alerts:
    alerts_df = pd.DataFrame(alerts)
    borrower_lookup = {b["id"]: b["business_name"] for b in borrowers}
    alerts_df["business_name"] = alerts_df["borrower_id"].map(borrower_lookup)
    alerts_df = alerts_df[["business_name", "alert_type", "detail", "stage", "created_at"]]
    alerts_df.columns = ["Borrower", "Alert Type", "Detail", "Escalation Stage", "Flagged At"]
    st.dataframe(alerts_df, hide_index=True, use_container_width=True)
else:
    st.success("No active early-warning alerts.")

st.markdown("---")
subbanner("Escalation Ladder")
ladder = pd.DataFrame({
    "Stage": ["Day 0-2", "Day 3-7", "Day 8-15", "Day 16-30", "30+ DPD"],
    "Action": ["Automated SMS/WhatsApp nudge", "Cluster manager call", "On-ground field visit",
               "Restructuring / OTS offer", "Bureau reporting; joint asset classification"],
    "Borrowers at this stage": [
        len(disbursed_df[(disbursed_df["dpd"] > 0) & (disbursed_df["dpd"] <= 2)]),
        len(disbursed_df[(disbursed_df["dpd"] > 2) & (disbursed_df["dpd"] <= 7)]),
        len(disbursed_df[(disbursed_df["dpd"] > 7) & (disbursed_df["dpd"] <= 15)]),
        len(disbursed_df[(disbursed_df["dpd"] > 15) & (disbursed_df["dpd"] <= 30)]),
        len(disbursed_df[disbursed_df["dpd"] > 30]),
    ],
})
st.table(ladder.set_index("Stage"))

st.markdown("---")
subbanner("Borrower Register")
show_cols = ["id", "business_name", "cluster", "sector", "risk_band", "sanctioned_limit",
             "disbursed_amount", "dpd", "npa_flag"]
reg = df[show_cols].rename(columns={
    "id": "ID", "business_name": "Business", "cluster": "Cluster", "sector": "Sector",
    "risk_band": "Risk Band", "sanctioned_limit": "Sanctioned (₹)",
    "disbursed_amount": "Disbursed (₹)", "dpd": "DPD", "npa_flag": "NPA",
})
st.dataframe(reg, hide_index=True, use_container_width=True)

footer()
