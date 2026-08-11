import streamlit as st
import pandas as pd
from utils.styling import inject_base_css, banner, subbanner, footer
from utils.db import get_all_borrowers

st.set_page_config(page_title="KhataSetu | Investor Metrics", page_icon="📈", layout="wide")
inject_base_css()

banner("BUSINESS PLAN — 3-Year AUM Build & Unit Economics")

borrowers = get_all_borrowers()
df = pd.DataFrame(borrowers) if borrowers else pd.DataFrame()

st.markdown("#### 3-Year AUM Build & Path to EBITDA Positive")
plan_df = pd.DataFrame({
    "Year": ["Year 1", "Year 2", "Year 3"],
    "Borrowers": [2500, 9000, 22000],
    "AUM (₹ Cr)": [40, 180, 550],
    "Clusters": [3, 8, 15],
})
c1, c2 = st.columns([1.4, 1])
with c1:
    st.bar_chart(plan_df.set_index("Year")["AUM (₹ Cr)"])
with c2:
    st.table(plan_df.set_index("Year"))
st.caption("EBITDA turns positive around Month 30-32 (Q2 of Year 3) as NIM and fee income "
           "outpace cluster opex.")

st.markdown("---")
subbanner("Unit Economics")
u1, u2, u3, u4 = st.columns(4)
u1.metric("CAC", "₹3,200 - ₹4,000", help="Phygital: cluster manager + digital sourcing")
u2.metric("3-Yr LTV", "~₹28,000", help="Multi-cycle revolving relationship")
u3.metric("LTV : CAC", "~7-8x", help="After 2 renewal cycles")
u4.metric("Gross NPA Target", "< 4.0%", help="vs 5-7% industry typical")

st.markdown("---")
subbanner("Revenue Model — Four Streams, Anchored on Spread")
rev_df = pd.DataFrame({
    "Stream": ["Net Interest Margin", "Processing Fee", "Co-Lending Servicing Spread", "Cross-Sell (Yr 2+)"],
    "Detail": [
        "~5.5-6.0% on 10% own-book share (~17% blended rate less ~11% cost of funds)",
        "1.0-1.5% of sanctioned limit, on origination and renewal",
        "Sourcing/underwriting/collections fee on bank partner's 90% share",
        "Embedded GST-filing SaaS, invoice financing, credit-linked insurance",
    ],
})
st.table(rev_df.set_index("Stream"))

st.markdown("---")
subbanner("Live Prototype Snapshot (from seeded/demo data)")
if not df.empty:
    disbursed_df = df[df["disbursed"] == 1]
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Prototype AUM", f"₹{disbursed_df['disbursed_amount'].sum():,.0f}")
    m2.metric("Prototype Borrowers", f"{len(disbursed_df)}")
    m3.metric("Avg Score", f"{df['score'].mean():.1f}/100")
    m4.metric("Avg Interest Rate", f"{df['interest_rate'].mean():.1f}%")
else:
    st.info("No demo data yet.")

footer()
