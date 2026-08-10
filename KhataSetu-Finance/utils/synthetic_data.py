"""Generates synthetic GST / UPI / e-way bill / Account Aggregator data."""

import os
import random
import pandas as pd
from datetime import datetime, timedelta


def generate_borrower_data(seed=None):
    if seed is not None:
        random.seed(seed)

    base_monthly_turnover = random.randint(150000, 3500000)

    gst_returns = []
    for m in range(12):
        month_turnover = int(base_monthly_turnover * random.uniform(0.75, 1.25))
        filed_on_time = random.random() > 0.12
        gst_returns.append({
            "month": (datetime.now() - timedelta(days=30 * (11 - m))).strftime("%b %Y"),
            "declared_turnover": month_turnover,
            "filed_on_time": filed_on_time,
            "delay_days": 0 if filed_on_time else random.randint(1, 20),
        })

    upi_history = []
    for m in range(6):
        daily_inflow = int(base_monthly_turnover / 28 * random.uniform(0.7, 1.3))
        upi_history.append({
            "month": (datetime.now() - timedelta(days=30 * (5 - m))).strftime("%b %Y"),
            "monthly_upi_inflow": daily_inflow * 28,
            "txn_count": random.randint(150, 1200),
        })

    eway_bills = []
    for m in range(6):
        eway_bills.append({
            "month": (datetime.now() - timedelta(days=30 * (5 - m))).strftime("%b %Y"),
            "dispatch_count": random.randint(20, 300),
            "dispatch_value": int(base_monthly_turnover * random.uniform(0.5, 0.9)),
        })

    aa_data = {
        "avg_monthly_bank_credit": int(base_monthly_turnover * random.uniform(0.6, 1.0)),
        "avg_monthly_bank_debit": int(base_monthly_turnover * random.uniform(0.5, 0.95)),
        "avg_closing_balance": int(base_monthly_turnover * random.uniform(0.1, 0.4)),
        "bounce_count_6m": random.choices([0, 1, 2, 3], weights=[70, 15, 10, 5])[0],
    }

    bureau = {
        "has_bureau_file": random.random() > 0.55,
        "bureau_score": random.randint(650, 800) if random.random() > 0.55 else None,
    }

    return {
        "base_monthly_turnover": base_monthly_turnover,
        "gst_returns": gst_returns,
        "upi_history": upi_history,
        "eway_bills": eway_bills,
        "aa_data": aa_data,
        "bureau": bureau,
    }


CLUSTERS = ["UP - Moradabad", "Rajasthan - Bhilwara", "Gujarat - Morbi"]
SECTORS = ["Trading", "Micro-Manufacturing"]
TURNOVER_BANDS = ["< Rs 40L", "Rs 40L-1Cr", "Rs 1-3Cr", "Rs 3-5Cr", "> Rs 5Cr"]
LANGUAGES = ["Hindi", "English", "Gujarati", "Marwari"]

BUSINESS_PREFIXES = [
    "Sharma", "Gupta", "Patel", "Verma", "Singh", "Jain", "Yadav", "Mehta",
    "Chaudhary", "Reddy", "Bansal", "Malhotra", "Rathi", "Nair", "Iyer",
    "Agarwal", "Kapoor", "Shah", "Desai", "Pillai",
]
BUSINESS_SUFFIXES = [
    "Hardware Store", "Textiles", "Agri Traders", "Auto Parts", "Kirana Wholesale",
    "Food Processing", "Steel Traders", "Cloth House", "Fertilizer Depot",
    "Light Engineering", "Electricals", "Grains", "Ceramics", "Timber Traders",
    "Spice Traders", "Plastics", "Packaging Co", "Metal Works",
]


def _flatten_borrower_row(idx: int, raw: dict) -> dict:
    gst = raw["gst_returns"]
    upi = raw["upi_history"]
    eway = raw["eway_bills"]
    aa = raw["aa_data"]
    bureau = raw["bureau"]

    gst_turnovers = [r["declared_turnover"] for r in gst]
    gst_on_time_pct = round(100 * sum(1 for r in gst if r["filed_on_time"]) / len(gst), 1)
    gst_avg_delay_days = round(sum(r["delay_days"] for r in gst) / len(gst), 1)

    upi_inflows = [m["monthly_upi_inflow"] for m in upi]
    upi_trend_pct = round(100 * (upi_inflows[-1] - upi_inflows[0]) / (upi_inflows[0] + 1), 1)

    eway_counts = [m["dispatch_count"] for m in eway]
    eway_momentum_pct = round(100 * (eway_counts[-1] - eway_counts[0]) / (eway_counts[0] + 1), 1)

    return {
        "borrower_id": idx,
        "business_name": f"{random.choice(BUSINESS_PREFIXES)} {random.choice(BUSINESS_SUFFIXES)} #{idx}",
        "gstin": f"07ABCDE{1000+idx}F1Z{idx % 9}",
        "sector": random.choice(SECTORS),
        "cluster": random.choice(CLUSTERS),
        "turnover_band": random.choice(TURNOVER_BANDS),
        "language": random.choice(LANGUAGES),
        "base_monthly_turnover": raw["base_monthly_turnover"],
        "gst_filed_on_time_pct": gst_on_time_pct,
        "gst_avg_declared_turnover": round(sum(gst_turnovers) / len(gst_turnovers)),
        "gst_max_declared_turnover": max(gst_turnovers),
        "gst_min_declared_turnover": min(gst_turnovers),
        "gst_avg_delay_days": gst_avg_delay_days,
        "upi_avg_monthly_inflow": round(sum(upi_inflows) / len(upi_inflows)),
        "upi_inflow_trend_pct": upi_trend_pct,
        "upi_avg_txn_count": round(sum(m["txn_count"] for m in upi) / len(upi)),
        "eway_avg_dispatch_count": round(sum(eway_counts) / len(eway_counts), 1),
        "eway_dispatch_momentum_pct": eway_momentum_pct,
        "eway_avg_dispatch_value": round(sum(m["dispatch_value"] for m in eway) / len(eway)),
        "aa_avg_monthly_credit": aa["avg_monthly_bank_credit"],
        "aa_avg_monthly_debit": aa["avg_monthly_bank_debit"],
        "aa_avg_closing_balance": aa["avg_closing_balance"],
        "aa_net_monthly_flow": aa["avg_monthly_bank_credit"] - aa["avg_monthly_bank_debit"],
        "aa_bounce_count_6m": aa["bounce_count_6m"],
        "bureau_has_file": bureau["has_bureau_file"],
        "bureau_score": bureau["bureau_score"] if bureau["bureau_score"] else "",
    }


def generate_dataset(n: int = 1000, seed: int = 42, score: bool = True) -> pd.DataFrame:
    from utils.scoring_engine import score_borrower
    random.seed(seed)
    rows = []
    scored_rows = []

    for i in range(1, n + 1):
        raw = generate_borrower_data()
        flat = _flatten_borrower_row(i, raw)
        rows.append(flat)

        if score:
            result = score_borrower(raw)
            scored_rows.append({
                "cash_flow_score": result["score"],
                "risk_band": result["risk_band"],
                "sanctioned_limit": result["sanctioned_limit"],
                "interest_rate_pct": result["interest_rate"],
                "processing_fee_pct": result["processing_fee_pct"],
                "apr_pct": result["apr"],
            })

    df = pd.DataFrame(rows)
    if score:
        df = pd.concat([df, pd.DataFrame(scored_rows)], axis=1)
    return df


def save_dataset_csv(path: str = "data/khatasetu_synthetic_dataset.csv", n: int = 1000, seed: int = 42):
    os.makedirs("data", exist_ok=True)
    df = generate_dataset(n=n, seed=seed)
    df.to_csv(path, index=False)
    return path


def load_dataset_to_db(n: int = 1000, seed: int = 42):
    """Fast bulk loader: builds all rows in memory, inserts with ONE connection."""
    from utils.scoring_engine import score_borrower
    from utils.db import init_db, insert_borrowers_bulk

    init_db()
    random.seed(seed)
    rows = []

    for i in range(1, n + 1):
        raw = generate_borrower_data()
        flat = _flatten_borrower_row(i, raw)
        result = score_borrower(raw)

        flat_row = {
            "business_name": flat["business_name"],
            "gstin": flat["gstin"],
            "sector": flat["sector"],
            "cluster": flat["cluster"],
            "turnover_band": flat["turnover_band"],
            "language": flat["language"],
            "base_monthly_turnover": flat["base_monthly_turnover"],
            "cash_flow_score": result["score"],
            "risk_band": result["risk_band"],
            "sanctioned_limit": result["sanctioned_limit"],
            "interest_rate_pct": result["interest_rate"],
            "processing_fee_pct": result["processing_fee_pct"],
            "apr_pct": result["apr"],
        }
        rows.append((flat_row, raw, result["sub_scores"]))

    return insert_borrowers_bulk(rows)


def reset_borrowers_table():
    """Wipes all borrower rows and resets the autoincrement counter."""
    from utils.db import get_connection
    conn = get_connection()
    conn.execute("DELETE FROM borrowers")
    conn.execute("DELETE FROM sqlite_sequence WHERE name='borrowers'")
    conn.commit()
    conn.close()
