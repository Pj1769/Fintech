"""SQLite helpers for KhataSetu Finance."""

import sqlite3
import json
import os

DB_PATH = "data/khatasetu.db"


def get_connection():
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS borrowers (
            borrower_id INTEGER PRIMARY KEY AUTOINCREMENT,
            business_name TEXT NOT NULL,
            gstin TEXT,
            sector TEXT,
            cluster TEXT,
            turnover_band TEXT,
            language TEXT,
            base_monthly_turnover REAL,
            cash_flow_score REAL,
            risk_band TEXT,
            sanctioned_limit REAL,
            interest_rate_pct REAL,
            processing_fee_pct REAL,
            apr_pct REAL,
            raw_data_json TEXT,
            sub_scores_json TEXT,
            kyc_status TEXT DEFAULT 'pending',
            consent_given INTEGER DEFAULT 0,
            preferred_language TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS credit_offers (
            offer_id INTEGER PRIMARY KEY AUTOINCREMENT,
            borrower_id INTEGER NOT NULL,
            offered_limit REAL,
            interest_rate_pct REAL,
            processing_fee_pct REAL,
            apr_pct REAL,
            status TEXT DEFAULT 'offered',
            offered_at TEXT DEFAULT (datetime('now')),
            responded_at TEXT,
            FOREIGN KEY (borrower_id) REFERENCES borrowers(borrower_id)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS disbursements (
            disbursement_id INTEGER PRIMARY KEY AUTOINCREMENT,
            offer_id INTEGER NOT NULL,
            borrower_id INTEGER NOT NULL,
            disbursed_amount REAL,
            esign_status TEXT DEFAULT 'pending',
            disbursed_at TEXT,
            FOREIGN KEY (offer_id) REFERENCES credit_offers(offer_id),
            FOREIGN KEY (borrower_id) REFERENCES borrowers(borrower_id)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS repayments (
            repayment_id INTEGER PRIMARY KEY AUTOINCREMENT,
            disbursement_id INTEGER NOT NULL,
            borrower_id INTEGER NOT NULL,
            emi_amount REAL,
            due_date TEXT,
            paid_date TEXT,
            status TEXT DEFAULT 'due',
            FOREIGN KEY (disbursement_id) REFERENCES disbursements(disbursement_id),
            FOREIGN KEY (borrower_id) REFERENCES borrowers(borrower_id)
        )
    """)

    conn.commit()
    conn.close()


def insert_borrower(flat_row: dict, raw_data: dict, sub_scores: dict) -> int:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO borrowers (
            business_name, gstin, sector, cluster, turnover_band, language,
            base_monthly_turnover, cash_flow_score, risk_band, sanctioned_limit,
            interest_rate_pct, processing_fee_pct, apr_pct,
            raw_data_json, sub_scores_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        flat_row.get("business_name"), flat_row.get("gstin"), flat_row.get("sector"),
        flat_row.get("cluster"), flat_row.get("turnover_band"), flat_row.get("language"),
        flat_row.get("base_monthly_turnover"), flat_row.get("cash_flow_score"),
        flat_row.get("risk_band"), flat_row.get("sanctioned_limit"),
        flat_row.get("interest_rate_pct"), flat_row.get("processing_fee_pct"),
        flat_row.get("apr_pct"), json.dumps(raw_data), json.dumps(sub_scores),
    ))
    conn.commit()
    borrower_id = cur.lastrowid
    conn.close()
    return borrower_id


def insert_borrowers_bulk(rows: list) -> list:
    """rows: list of (flat_row_dict, raw_data_dict, sub_scores_dict) tuples.
    Uses ONE connection for all inserts — fast."""
    conn = get_connection()
    cur = conn.cursor()
    inserted_ids = []

    for flat_row, raw_data, sub_scores in rows:
        cur.execute("""
            INSERT INTO borrowers (
                business_name, gstin, sector, cluster, turnover_band, language,
                base_monthly_turnover, cash_flow_score, risk_band, sanctioned_limit,
                interest_rate_pct, processing_fee_pct, apr_pct,
                raw_data_json, sub_scores_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            flat_row.get("business_name"), flat_row.get("gstin"), flat_row.get("sector"),
            flat_row.get("cluster"), flat_row.get("turnover_band"), flat_row.get("language"),
            flat_row.get("base_monthly_turnover"), flat_row.get("cash_flow_score"),
            flat_row.get("risk_band"), flat_row.get("sanctioned_limit"),
            flat_row.get("interest_rate_pct"), flat_row.get("processing_fee_pct"),
            flat_row.get("apr_pct"), json.dumps(raw_data), json.dumps(sub_scores),
        ))
        inserted_ids.append(cur.lastrowid)

    conn.commit()
    conn.close()
    return inserted_ids


def get_borrower(borrower_id: int) -> dict:
    conn = get_connection()
    row = conn.execute("SELECT * FROM borrowers WHERE borrower_id = ?", (borrower_id,)).fetchone()
    conn.close()
    if row is None:
        return None
    result = dict(row)
    result["raw_data"] = json.loads(result.pop("raw_data_json") or "{}")
    result["sub_scores"] = json.loads(result.pop("sub_scores_json") or "{}")
    return result


def get_all_borrowers(as_dataframe=False):
    conn = get_connection()
    rows = conn.execute("""
        SELECT borrower_id, business_name, gstin, sector, cluster, turnover_band,
               language, base_monthly_turnover, cash_flow_score, risk_band,
               sanctioned_limit, interest_rate_pct, processing_fee_pct, apr_pct,
               kyc_status, consent_given, created_at
        FROM borrowers
    """).fetchall()
    conn.close()
    result = [dict(r) for r in rows]
    if as_dataframe:
        import pandas as pd
        return pd.DataFrame(result)
    return result


def update_kyc_status(borrower_id: int, status: str):
    conn = get_connection()
    conn.execute("UPDATE borrowers SET kyc_status = ? WHERE borrower_id = ?", (status, borrower_id))
    conn.commit()
    conn.close()


def update_consent(borrower_id: int, given: bool):
    conn = get_connection()
    conn.execute("UPDATE borrowers SET consent_given = ? WHERE borrower_id = ?", (1 if given else 0, borrower_id))
    conn.commit()
    conn.close()


def create_offer(borrower_id: int, limit: float, rate: float, fee: float, apr: float) -> int:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO credit_offers (borrower_id, offered_limit, interest_rate_pct, processing_fee_pct, apr_pct)
        VALUES (?, ?, ?, ?, ?)
    """, (borrower_id, limit, rate, fee, apr))
    conn.commit()
    offer_id = cur.lastrowid
    conn.close()
    return offer_id


def respond_to_offer(offer_id: int, status: str):
    conn = get_connection()
    conn.execute("UPDATE credit_offers SET status = ?, responded_at = datetime('now') WHERE offer_id = ?", (status, offer_id))
    conn.commit()
    conn.close()


def get_offers_for_borrower(borrower_id: int):
    conn = get_connection()
    rows = conn.execute("SELECT * FROM credit_offers WHERE borrower_id = ? ORDER BY offered_at DESC", (borrower_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def create_disbursement(offer_id: int, borrower_id: int, amount: float) -> int:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO disbursements (offer_id, borrower_id, disbursed_amount) VALUES (?, ?, ?)", (offer_id, borrower_id, amount))
    conn.commit()
    disbursement_id = cur.lastrowid
    conn.close()
    return disbursement_id


def mark_esigned(disbursement_id: int):
    conn = get_connection()
    conn.execute("UPDATE disbursements SET esign_status = 'signed', disbursed_at = datetime('now') WHERE disbursement_id = ?", (disbursement_id,))
    conn.commit()
    conn.close()


def create_repayment_schedule(disbursement_id: int, borrower_id: int, emi_amount: float, due_dates: list):
    conn = get_connection()
    cur = conn.cursor()
    for due_date in due_dates:
        cur.execute("INSERT INTO repayments (disbursement_id, borrower_id, emi_amount, due_date) VALUES (?, ?, ?, ?)", (disbursement_id, borrower_id, emi_amount, due_date))
    conn.commit()
    conn.close()


def get_repayments_for_borrower(borrower_id: int):
    conn = get_connection()
    rows = conn.execute("SELECT * FROM repayments WHERE borrower_id = ? ORDER BY due_date", (borrower_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def mark_repayment_paid(repayment_id: int):
    conn = get_connection()
    conn.execute("UPDATE repayments SET status = 'paid', paid_date = datetime('now') WHERE repayment_id = ?", (repayment_id,))
    conn.commit()
    conn.close()


def get_portfolio_summary() -> dict:
    conn = get_connection()
    total_borrowers = conn.execute("SELECT COUNT(*) FROM borrowers").fetchone()[0]
    total_sanctioned = conn.execute("SELECT SUM(sanctioned_limit) FROM borrowers").fetchone()[0] or 0
    total_disbursed = conn.execute("SELECT SUM(disbursed_amount) FROM disbursements").fetchone()[0] or 0
    npa_count = conn.execute("SELECT COUNT(*) FROM repayments WHERE status = 'npa'").fetchone()[0]
    band_counts = conn.execute("SELECT risk_band, COUNT(*) as count FROM borrowers GROUP BY risk_band").fetchall()
    conn.close()
    return {
        "total_borrowers": total_borrowers,
        "total_sanctioned": total_sanctioned,
        "total_disbursed": total_disbursed,
        "npa_count": npa_count,
        "band_distribution": {r["risk_band"]: r["count"] for r in band_counts},
    }
