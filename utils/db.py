"""Lightweight SQLite persistence so borrower state survives across the
multi-page Streamlit journey and the lender/ops dashboard can read it back.

seed_demo_borrowers() loads from khatasetu_synthetic_dataset.csv when
present, so the app's dashboards reflect the exact dataset you generated
with synthetic_data.generate_dataset(). Falls back to generating fresh
synthetic data if the CSV isn't found.
"""

import sqlite3
import json
import os
from datetime import datetime, timedelta
import random
import pandas as pd

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "khatasetu.db")
CSV_PATH = os.path.join(os.path.dirname(__file__), "..", "khatasetu_synthetic_dataset.csv")


def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS borrowers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            business_name TEXT,
            gstin TEXT,
            sector TEXT,
            turnover_band TEXT,
            cluster TEXT,
            language TEXT,
            aadhaar_masked TEXT,
            pan TEXT,
            kyc_verified INTEGER DEFAULT 0,
            consent_json TEXT,
            synthetic_data_json TEXT,
            score REAL,
            risk_band TEXT,
            sanctioned_limit REAL,
            available_limit REAL,
            interest_rate REAL,
            processing_fee_pct REAL,
            apr REAL,
            offer_accepted INTEGER DEFAULT 0,
            disbursed INTEGER DEFAULT 0,
            disbursed_amount REAL,
            next_emi REAL,
            next_emi_due TEXT,
            autopay INTEGER DEFAULT 1,
            npa_flag INTEGER DEFAULT 0,
            dpd INTEGER DEFAULT 0,
            created_at TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS repayments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            borrower_id INTEGER,
            cycle_no INTEGER,
            amount REAL,
            status TEXT,
            paid_on TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            borrower_id INTEGER,
            alert_type TEXT,
            detail TEXT,
            stage TEXT,
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()


def insert_borrower(data: dict) -> int:
    conn = get_conn()
    c = conn.cursor()
    cols = ", ".join(data.keys())
    placeholders = ", ".join(["?"] * len(data))
    c.execute(f"INSERT INTO borrowers ({cols}) VALUES ({placeholders})", list(data.values()))
    conn.commit()
    new_id = c.lastrowid
    conn.close()
    return new_id


def update_borrower(borrower_id: int, data: dict):
    conn = get_conn()
    c = conn.cursor()
    set_clause = ", ".join([f"{k} = ?" for k in data.keys()])
    c.execute(f"UPDATE borrowers SET {set_clause} WHERE id = ?", list(data.values()) + [borrower_id])
    conn.commit()
    conn.close()


def get_borrower(borrower_id: int):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM borrowers WHERE id = ?", (borrower_id,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None


def get_all_borrowers():
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM borrowers ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def add_repayment(borrower_id, cycle_no, amount, status, paid_on):
    conn = get_conn()
    c = conn.cursor()
    c.execute(
        "INSERT INTO repayments (borrower_id, cycle_no, amount, status, paid_on) VALUES (?,?,?,?,?)",
        (borrower_id, cycle_no, amount, status, paid_on),
    )
    conn.commit()
    conn.close()


def get_repayments(borrower_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM repayments WHERE borrower_id = ? ORDER BY cycle_no", (borrower_id,))
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def add_alert(borrower_id, alert_type, detail, stage):
    conn = get_conn()
    c = conn.cursor()
    c.execute(
        "INSERT INTO alerts (borrower_id, alert_type, detail, stage, created_at) VALUES (?,?,?,?,?)",
        (borrower_id, alert_type, detail, stage, datetime.now().isoformat()),
    )
    conn.commit()
    conn.close()


def get_alerts():
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM alerts ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def _seed_from_csv(n):
    """Load borrowers from khatasetu_synthetic_dataset.csv (capped at n rows)."""
    df = pd.read_csv(CSV_PATH)
    if n:
        df = df.head(n)

    for _, row in df.iterrows():
        disbursed = random.random() < 0.85
        dpd = random.choices([0, 5, 12, 22, 35], weights=[70, 12, 8, 6, 4])[0]
        npa_flag = 1 if dpd >= 90 else 0
        sanctioned_limit = float(row["sanctioned_limit"])
        disbursed_amount = round(sanctioned_limit * random.uniform(0.4, 0.9), 0) if disbursed else 0
        next_emi = round(sanctioned_limit * 0.045, -2) if disbursed else 0

        bureau_score = row.get("bureau_score", "")
        bureau_has_file = bool(row.get("bureau_has_file", False))

        synth_stub = {
            "base_monthly_turnover": int(row["base_monthly_turnover"]),
            "gst_returns": [{"filed_on_time": True, "declared_turnover": int(row["gst_avg_declared_turnover"]), "delay_days": 0}] * 12,
            "upi_history": [{"monthly_upi_inflow": int(row["upi_avg_monthly_inflow"]), "txn_count": int(row["upi_avg_txn_count"])}] * 6,
            "eway_bills": [{"dispatch_count": int(row["eway_avg_dispatch_count"]), "dispatch_value": int(row["eway_avg_dispatch_value"])}] * 6,
            "aa_data": {
                "avg_monthly_bank_credit": int(row["aa_avg_monthly_credit"]),
                "avg_monthly_bank_debit": int(row["aa_avg_monthly_debit"]),
                "avg_closing_balance": int(row["aa_avg_closing_balance"]),
                "bounce_count_6m": int(row["aa_bounce_count_6m"]),
            },
            "bureau": {"has_bureau_file": bureau_has_file, "bureau_score": (int(bureau_score) if bureau_score not in ("", None) and not pd.isna(bureau_score) else None)},
        }

        data = {
            "business_name": row["business_name"],
            "gstin": row["gstin"],
            "sector": row["sector"],
            "turnover_band": row["turnover_band"],
            "cluster": row["cluster"],
            "language": row["language"],
            "aadhaar_masked": "XXXX XXXX " + str(1000 + int(row["borrower_id"])),
            "pan": f"ABCDE{1000+int(row['borrower_id'])}F",
            "kyc_verified": 1,
            "consent_json": json.dumps({"gst": True, "aa": True, "upi": True, "eway": True}),
            "synthetic_data_json": json.dumps(synth_stub),
            "score": float(row["cash_flow_score"]),
            "risk_band": row["risk_band"],
            "sanctioned_limit": sanctioned_limit,
            "available_limit": sanctioned_limit - disbursed_amount if disbursed else sanctioned_limit,
            "interest_rate": float(row["interest_rate_pct"]),
            "processing_fee_pct": float(row["processing_fee_pct"]),
            "apr": float(row["apr_pct"]),
            "offer_accepted": 1 if disbursed else 0,
            "disbursed": 1 if disbursed else 0,
            "disbursed_amount": disbursed_amount,
            "next_emi": next_emi,
            "next_emi_due": (datetime.now() + timedelta(days=random.randint(1, 30))).strftime("%d %b %Y"),
            "autopay": 1,
            "npa_flag": npa_flag,
            "dpd": dpd,
            "created_at": (datetime.now() - timedelta(days=random.randint(1, 300))).isoformat(),
        }
        bid = insert_borrower(data)

        n_cycles = random.randint(2, 8)
        for cyc in range(1, n_cycles + 1):
            status = random.choices(["Paid on time", "Paid late", "Missed"], weights=[80, 15, 5])[0]
            add_repayment(bid, cyc, next_emi or 5000, status,
                          (datetime.now() - timedelta(days=(n_cycles - cyc) * 30)).strftime("%d %b %Y"))

        if dpd >= 8:
            add_alert(bid, "UPI Inflow Decline", "UPI inflow down >20% over trailing 30 days", "Day 3-7: Cluster manager call")
        if dpd >= 22:
            add_alert(bid, "GST Filing Delay", "GST return filing delayed beyond due date", "Day 8-15: On-ground field visit")
        if dpd >= 35:
            add_alert(bid, "Autopay Bounce", "First UPI Autopay bounce on scheduled EMI", "Day 16-30: Restructuring / OTS offer")


def _seed_random(n):
    """Fallback: generate fresh synthetic borrowers if the CSV isn't found."""
    from utils.synthetic_data import generate_borrower_data
    from utils.scoring_engine import score_borrower

    clusters = ["UP - Moradabad", "Rajasthan - Bhilwara", "Gujarat - Morbi"]
    sectors = ["Trading", "Micro-Manufacturing"]
    names = ["Sharma Hardware Store", "Gupta Textiles", "Patel Agri Traders", "Verma Auto Parts",
             "Singh Kirana Wholesale", "Jain Food Processing", "Yadav Steel Traders", "Mehta Cloth House"]

    for i in range(n):
        name = random.choice(names) + f" #{i+1}"
        synth = generate_borrower_data()
        result = score_borrower(synth)
        disbursed = random.random() < 0.85
        dpd = random.choices([0, 5, 12, 22, 35], weights=[70, 12, 8, 6, 4])[0]

        data = {
            "business_name": name, "gstin": f"07ABCDE{1000+i}F1Z{i%9}",
            "sector": random.choice(sectors), "turnover_band": "Rs 1-3Cr",
            "cluster": random.choice(clusters), "language": "Hindi",
            "aadhaar_masked": "XXXX XXXX " + str(1000 + i), "pan": f"ABCDE{1000+i}F",
            "kyc_verified": 1, "consent_json": json.dumps({"gst": True, "aa": True, "upi": True, "eway": True}),
            "synthetic_data_json": json.dumps(synth), "score": result["score"], "risk_band": result["risk_band"],
            "sanctioned_limit": result["sanctioned_limit"],
            "available_limit": result["sanctioned_limit"] * random.uniform(0.4, 1.0) if disbursed else result["sanctioned_limit"],
            "interest_rate": result["interest_rate"], "processing_fee_pct": result["processing_fee_pct"],
            "apr": result["apr"], "offer_accepted": 1 if disbursed else 0, "disbursed": 1 if disbursed else 0,
            "disbursed_amount": result["sanctioned_limit"] * random.uniform(0.4, 0.9) if disbursed else 0,
            "next_emi": round(result["sanctioned_limit"] * 0.045, -2) if disbursed else 0,
            "next_emi_due": (datetime.now() + timedelta(days=random.randint(1, 30))).strftime("%d %b %Y"),
            "autopay": 1, "npa_flag": 1 if dpd >= 90 else 0, "dpd": dpd,
            "created_at": (datetime.now() - timedelta(days=random.randint(1, 300))).isoformat(),
        }
        insert_borrower(data)


def seed_demo_borrowers(n=25):
    """Populate the DB so the lender dashboard and investor metrics pages
    have data. Uses khatasetu_synthetic_dataset.csv if present (capped at
    n rows), otherwise generates fresh random borrowers."""
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) as n FROM borrowers")
    existing = c.fetchone()["n"]
    conn.close()
    if existing >= n:
        return

    if os.path.exists(CSV_PATH):
        _seed_from_csv(n)
    else:
        _seed_random(n)
