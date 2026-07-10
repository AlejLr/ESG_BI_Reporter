import json
from datetime import datetime
from pathlib import Path

import pandas as pd
import yfinance as yf

_ROOT = Path(__file__).resolve().parent.parent.parent


def collect(company: str, config: dict) -> dict:
    fin_cfg = config.get("financial") or {}
    ticker_sym = config["ticker"]
    start = fin_cfg.get("start_date", "2021-01-01")
    end = fin_cfg.get("end_date", datetime.today().strftime("%Y-%m-%d"))

    tkr = yf.Ticker(ticker_sym)

    prices = tkr.history(start=start, end=end, interval="1d")
    if prices.empty:
        raise ValueError(f"No price data for '{ticker_sym}'. Verify the ticker symbol.")

    if prices.index.tz is not None:
        prices.index = prices.index.tz_convert(None)

    try:
        financials = tkr.financials.T.sort_index()
    except Exception:
        financials = pd.DataFrame()

    try:
        info = tkr.info
    except Exception:
        info = {}

    _persist_raw(company, prices, financials, info)

    return {"prices": prices, "financials": financials, "info": info}


def _persist_raw(company: str, prices: pd.DataFrame, financials: pd.DataFrame, info: dict) -> None:
    raw_dir = _ROOT / "data" / "raw" / company
    raw_dir.mkdir(parents=True, exist_ok=True)
    prices.to_csv(raw_dir / "prices_raw.csv")
    if not financials.empty:
        financials.to_csv(raw_dir / "financials_raw.csv")
    if info:
        with open(raw_dir / "info.json", "w", encoding="utf-8") as f:
            json.dump(info, f, indent=2, default=str)
