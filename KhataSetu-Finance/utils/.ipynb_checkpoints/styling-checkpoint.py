"""Shared styling helpers so every page matches the KhataSetu pitch-deck look:
deep-green banner strips, white cards, consistent footer."""

import streamlit as st

GREEN = "#1F6B4A"
GREEN_DARK = "#154A33"
CREAM = "#FDF6E3"
GOLD = "#C9A227"


def inject_base_css():
    st.markdown(
        f"""
        <style>
        .block-container {{ padding-top: 2rem; padding-bottom: 3rem; }}

        .ks-banner {{
            background-color: {GREEN};
            color: white;
            padding: 10px 18px;
            border-radius: 4px;
            font-weight: 700;
            font-size: 1.05rem;
            margin: 18px 0 12px 0;
            letter-spacing: 0.3px;
        }}
        .ks-subbanner {{
            background-color: {GREEN_DARK};
            color: white;
            padding: 6px 14px;
            border-radius: 4px;
            font-weight: 600;
            font-size: 0.85rem;
            margin-bottom: 10px;
        }}
        .ks-card {{
            background-color: #FFFFFF;
            border: 1px solid #E3E8E5;
            border-radius: 10px;
            padding: 16px 18px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
            margin-bottom: 12px;
        }}
        .ks-note {{
            background-color: {CREAM};
            border-left: 4px solid {GOLD};
            padding: 10px 14px;
            border-radius: 4px;
            font-size: 0.9rem;
            margin-bottom: 14px;
        }}
        .ks-metric-big {{
            font-size: 1.9rem;
            font-weight: 800;
            color: {GREEN_DARK};
        }}
        .ks-footer {{
            text-align: center;
            color: #8A8A8A;
            font-size: 0.72rem;
            letter-spacing: 1px;
            margin-top: 40px;
            border-top: 1px solid #eee;
            padding-top: 10px;
        }}
        .ks-chip {{
            display: inline-block;
            background-color: #E8F1EC;
            color: {GREEN_DARK};
            padding: 3px 10px;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 600;
            margin-right: 6px;
        }}
        .ks-whatsapp-btn {{
            background-color: #25D366;
            color: white;
            padding: 10px 16px;
            border-radius: 8px;
            text-align: center;
            font-weight: 700;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def banner(text: str):
    st.markdown(f'<div class="ks-banner">{text}</div>', unsafe_allow_html=True)


def subbanner(text: str):
    st.markdown(f'<div class="ks-subbanner">{text}</div>', unsafe_allow_html=True)


def note(text: str):
    st.markdown(f'<div class="ks-note"><b>Note:</b> {text}</div>', unsafe_allow_html=True)


def footer():
    st.markdown(
        '<div class="ks-footer">KHATASETU FINANCE  |  SEED PITCH PROTOTYPE  |  CONFIDENTIAL</div>',
        unsafe_allow_html=True,
    )


def chip(text: str):
    st.markdown(f'<span class="ks-chip">{text}</span>', unsafe_allow_html=True)