"""Cash-flow based credit scorecard for KhataSetu Finance."""


def _score_gst(gst_returns: list) -> float:
    on_time_pct = sum(1 for r in gst_returns if r["filed_on_time"]) / len(gst_returns)
    avg_delay = sum(r["delay_days"] for r in gst_returns) / len(gst_returns)

    turnovers = [r["declared_turnover"] for r in gst_returns]
    avg_turnover = sum(turnovers) / len(turnovers)
    variance = sum((t - avg_turnover) ** 2 for t in turnovers) / len(turnovers)
    cv = (variance ** 0.5) / avg_turnover if avg_turnover else 1

    punctuality_score = on_time_pct * 100
    delay_penalty = min(avg_delay * 2, 30)
    stability_score = max(0, 100 - cv * 150)

    return max(0, min(100, 0.5 * punctuality_score - delay_penalty + 0.5 * stability_score))


def _score_upi(upi_history: list) -> float:
    inflows = [m["monthly_upi_inflow"] for m in upi_history]
    txn_counts = [m["txn_count"] for m in upi_history]

    trend_pct = (inflows[-1] - inflows[0]) / (inflows[0] + 1) * 100
    trend_score = max(0, min(100, 50 + trend_pct))

    avg_txn = sum(txn_counts) / len(txn_counts)
    depth_score = min(100, avg_txn / 8)

    return max(0, min(100, 0.6 * trend_score + 0.4 * depth_score))


def _score_eway(eway_bills: list) -> float:
    counts = [m["dispatch_count"] for m in eway_bills]
    momentum_pct = (counts[-1] - counts[0]) / (counts[0] + 1) * 100
    momentum_score = max(0, min(100, 50 + momentum_pct))

    avg_count = sum(counts) / len(counts)
    activity_score = min(100, avg_count / 2)

    return max(0, min(100, 0.5 * momentum_score + 0.5 * activity_score))


def _score_aa(aa_data: dict) -> float:
    credit = aa_data["avg_monthly_bank_credit"]
    debit = aa_data["avg_monthly_bank_debit"]
    balance = aa_data["avg_closing_balance"]
    bounces = aa_data["bounce_count_6m"]

    net_flow_ratio = (credit - debit) / credit if credit else 0
    net_flow_score = max(0, min(100, 50 + net_flow_ratio * 200))

    balance_ratio = balance / credit if credit else 0
    balance_score = min(100, balance_ratio * 300)

    bounce_penalty = bounces * 15

    return max(0, min(100, 0.5 * net_flow_score + 0.3 * balance_score - bounce_penalty + 20))


def _score_bureau(bureau: dict) -> float:
    if not bureau.get("has_bureau_file") or not bureau.get("bureau_score"):
        return 60
    return max(0, min(100, (bureau["bureau_score"] - 650) / 150 * 100))


def score_borrower(raw: dict) -> dict:
    gst_score = _score_gst(raw["gst_returns"])
    upi_score = _score_upi(raw["upi_history"])
    eway_score = _score_eway(raw["eway_bills"])
    aa_score = _score_aa(raw["aa_data"])
    bureau_score = _score_bureau(raw["bureau"])

    composite = round(
        0.30 * gst_score + 0.30 * upi_score + 0.15 * eway_score +
        0.20 * aa_score + 0.05 * bureau_score, 1
    )

    turnover = raw["base_monthly_turnover"]

    if composite >= 80:
        risk_band, limit_multiple, interest_rate, processing_fee_pct = "A", 3.0, 14.0, 1.0
    elif composite >= 65:
        risk_band, limit_multiple, interest_rate, processing_fee_pct = "B", 2.0, 18.0, 1.5
    elif composite >= 50:
        risk_band, limit_multiple, interest_rate, processing_fee_pct = "C", 1.0, 24.0, 2.0
    else:
        risk_band, limit_multiple, interest_rate, processing_fee_pct = "D", 0.4, 30.0, 2.5

    sanctioned_limit = round(turnover * limit_multiple, -3)
    apr = round(interest_rate + processing_fee_pct, 1)

    return {
        "score": composite,
        "risk_band": risk_band,
        "sanctioned_limit": sanctioned_limit,
        "interest_rate": interest_rate,
        "processing_fee_pct": processing_fee_pct,
        "apr": apr,
        "sub_scores": {
            "gst": round(gst_score, 1),
            "upi": round(upi_score, 1),
            "eway": round(eway_score, 1),
            "aa": round(aa_score, 1),
            "bureau": round(bureau_score, 1),
        },
    }
