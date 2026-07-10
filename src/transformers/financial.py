import pandas as pd

_REVENUE_COLS = ["total_revenue", "revenue"]
_OPINCOME_COLS = ["operating_income", "ebit", "operating_profit"]
_NETINCOME_COLS = ["net_income"]


def transform(raw: dict, config: dict) -> dict:
    prices_daily = _clean_prices(raw["prices"])
    financials_annual = _clean_financials(raw["financials"])
    summary_annual = _build_summary(prices_daily, financials_annual, config)
    return {
        "prices_daily": prices_daily,
        "financials_annual": financials_annual,
        "summary_annual": summary_annual,
    }


def _clean_prices(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [c.lower().replace(" ", "_") for c in df.columns]
    df.index.name = "date"
    keep = [c for c in ["open", "high", "low", "close", "volume"] if c in df.columns]
    df.index = df.index.normalize()
    df = df[keep].dropna(subset=["close"])
    df["ma_30d"] = df["close"].rolling(30).mean().round(4)
    df["pct_change_daily"] = (df["close"].pct_change() * 100).round(4)
    return df


def _clean_financials(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    df = df.copy()
    if df.index.tz is not None:
        df.index = df.index.tz_convert(None)
    df.index = pd.to_datetime(df.index)
    df.index.name = "fiscal_year_end"
    df.columns = [str(c).lower().replace(" ", "_") for c in df.columns]
    return df


def _build_summary(prices: pd.DataFrame, financials: pd.DataFrame, config: dict) -> pd.DataFrame:
    # Yahoo Finance only exposes the most recent 4 fiscal years; the oldest price year will always have NaN fundamentals.
    # Fiscal year-end dates are mapped to calendar year by their year value, which assumes a December year-end.
    # Companies with non-December fiscal years (e.g. ending March or June) will show a one-year misalignment.
    annual = prices["close"].resample("YE").agg(
        price_start="first",
        price_end="last",
        price_avg="mean",
        price_min="min",
        price_max="max",
    ).round(4)
    annual["price_return_pct"] = (
        (annual["price_end"] - annual["price_start"]) / annual["price_start"] * 100
    ).round(2)
    annual.index = annual.index.year
    annual.index.name = "year"
    annual["currency"] = config.get("currency", "")

    if not financials.empty:
        fin = financials.copy()
        fin.index = fin.index.year
        fin.index.name = "year"

        rev_col = _find_col(fin, _REVENUE_COLS)
        op_col = _find_col(fin, _OPINCOME_COLS)
        net_col = _find_col(fin, _NETINCOME_COLS)

        if rev_col:
            annual["total_revenue"] = fin[rev_col]
            annual["revenue_growth_pct"] = (fin[rev_col].pct_change() * 100).round(2)
        if op_col:
            annual["operating_income"] = fin[op_col]
        if rev_col and op_col:
            annual["operating_margin_pct"] = (fin[op_col] / fin[rev_col] * 100).round(2)
        if net_col:
            annual["net_income"] = fin[net_col]

    return annual.reset_index()


def _find_col(df: pd.DataFrame, candidates: list) -> str | None:
    for c in candidates:
        if c in df.columns:
            return c
    return None
