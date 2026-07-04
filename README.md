# ESG Integrated Value Analyzer

An automated data pipeline and analytical framework that answers a single question: **is a company's sustainability commitment genuine, performative, or somewhere in between?**

Combines ESG scores, financial performance, public sentiment, and regulatory context into a unified "Integrated Value" framework

---

## What This Project Does

Most ESG tools report data in silos. This project cross-references four layers to surface what isolated scores miss:

| Layer | What It Measures | Source |
|---|---|---|
| ESG Performance | Carbon emissions, energy use, governance scores, science-based targets | Open ESG API, company sustainability reports, CDP open data |
| Financial Performance | Revenue, margins, stock price trend, market cap over time | yfinance (2021–2026) |
| Public Sentiment | News tone, Reddit discussion, Google News mentions around sustainability topics | NewsAPI free tier, Reddit JSON endpoints, Google News RSS |
| Regulatory Context | EU Taxonomy alignment, CSRD reporting status, SBTi membership, jurisdictional framework | Manual config per company (reviewed annually) |

The intersection of these four layers is where the insight lives.

---

## The Integrated Value Framework

This is the original analytical contribution of the project. Rather than producing a single composite score (which is easy to criticize and hard to defend), the framework produces a **four-dimensional scorecard** visualized as a radar chart.

### Core Signal: ESG–Financial Correlation
Does stronger ESG performance correspond to stronger or more stable financial performance for this company over the same period? This is the primary analytical question.

### Key Insight: The Sentiment Gap
The most compelling output. Compares a company's **public perception** (sentiment from news and social media) against its **actual reported ESG metrics**.

### Greenwashing Detection
Compares marketing signals (press release tone, sustainability report language) against hard metrics (emissions trajectory, energy intensity, target completion rates). A company that talks about sustainability constantly but doesn't improve its numbers gets flagged. A company that underreports its progress gets flagged in the opposite direction.

### Regulatory Modifier
Frames the other three dimensions by asking: what regulatory environment is this company operating in? A company voluntarily adopting EU Taxonomy standards while headquartered outside the EU is making a different commitment than one that is legally required to. This context changes how the ESG scores should be read.

### Supporting Analyses
- **Carbon intensity trend**: emissions per unit of revenue, not absolute emissions. A growing company that increases absolute emissions while improving per-unit efficiency is behaving differently than a company that is simply shrinking.
- **Peer comparison**: each company scored relative to its sector, not in isolation. A company that looks good standalone may be average within its industry.

---

## Output Types

### 1. Portfolio Dashboard
A multi-company Power BI dashboard comparing all target companies across all four framework dimensions. This lives on the portfolio as the full project showcase. Updated periodically as new company data is collected.

### 2. Case Study
A single-company view: one page, three or four key insights highlighted.

---

## Companies Covered

| Company | Sector | Priority | Notes |
|---|---|---|---|
| Ørsted | Energy (offshore wind) | 1: proof of concept | Strongest public ESG data; sector leader; clear before/after story |
| Unilever | FMCG | 2 | Major sustainability commitments; high public visibility |
| Nestlé | Food & Beverage | 3 | Interesting tension between public claims and water/deforestation controversies |
| Tesla | Automotive / Energy | 4 | Unusual ESG profile: high environmental but governance concerns |

**Adding a new company takes hours, not days.** Each company requires a config entry and one-time regulatory scoring. All collection and analysis logic is company-agnostic.

---

## Project Structure

```
ESG_BI_Reporter/
├── data/
│   ├── raw/                    # Raw API responses, scraped content, downloaded PDFs
│   ├── processed/              # Cleaned, structured datasets per company per source
│   └── exports/                # CSV/Excel files ready for Power BI ingestion
├── src/
│   ├── collectors/
│   │   ├── financial.py        # yfinance: stock price, revenue, margins, market cap
│   │   ├── esg.py              # Open ESG API → sustainability report fallback → CDP
│   │   ├── sentiment.py        # NewsAPI + Reddit JSON + Google News RSS collection
│   │   └── regulatory.py       # Loads per-company regulatory config from configs/
│   ├── transformers/
│   │   ├── financial.py        # Normalize, compute derived metrics (carbon intensity etc.)
│   │   ├── esg.py              # Standardize ESG metrics across sources
│   │   └── sentiment.py        # Clean text, deduplicate, prepare for inference
│   ├── analysis/
│   │   ├── inference.py        # HuggingFace sentiment/emotion/toxicity pipeline (reused from SM Analyzer)
│   │   ├── correlation.py      # ESG–financial correlation analysis
│   │   ├── gap_analysis.py     # Sentiment vs ESG gap (greenwashing detection)
│   │   ├── peer_comparison.py  # Sector-relative scoring
│   │   └── integrated_value.py # Assemble final scorecard per company
│   └── exporters/
│       ├── csv_exporter.py     # Write processed data to data/exports/
│       └── case_study.py       # Single-company summary export for outreach
├── configs/
│   └── companies/
│       ├── orsted.json         # Tickers, regulatory scores, sector, data source config
│       ├── unilever.json
│       ├── nestle.json
│       └── tesla.json
├── notebooks/
│   ├── 01_orsted_exploration.ipynb
│   └── 02_framework_prototype.ipynb
├── case_studies/               # Generated per-company outputs (CSV + summary text)
├── requirements.txt
└── README.md
```

---

## Data Sources

### Financial Data (yfinance)
- **What**: stock price history, market cap, revenue, operating margins, P/E ratio
- **Coverage**: 2021–2026 (5-year window; ESG data before 2020 is sparse and inconsistent)
- **Ticker examples**: Ørsted → `ORSTED.CO`, Unilever → `UL`, Nestlé → `NSRGY`, Tesla → `TSLA`
- **Free**: yes, no API key required

### ESG Data (multi-source with fallback chain)
1. **Open ESG API** (openESG.com free tier) — structured ESG scores, attempted first
2. **Company sustainability reports** — annual PDFs; key metrics extracted or entered into structured JSON
3. **CDP open data** — annual public dataset download, used as supplementary source
4. **Manual config** — for MVP, key metrics (total GHG emissions, renewable energy %, water use, etc.) can be entered directly into the company config JSON and updated annually

### Sentiment Data (three free sources)
1. **NewsAPI free tier** — 500 requests/day, headlines and article metadata from major news outlets
2. **Reddit public JSON** — append `.json` to any subreddit URL; no API key required for read-only access. Target: r/investing, r/sustainability, r/environment, company-specific subreddits
3. **Google News RSS** — filtered by company name, returns recent headlines with no rate limit

Twitter/X is excluded — the API is paid-only as of 2023 and doesn't fit the free-tier constraint.

### Sentiment Analysis (HuggingFace Transformers, reused from SM Analyzer)
The inference pipeline from [Social-Media-Emotion-Analysis-Dashboard](https://github.com/AlejLr/Social-Media-Emotion-Analysis-Dashboard) is reused as-is:
- **Sentiment**: positive / negative / neutral classification
- **Emotion**: joy, anger, fear, sadness, surprise, disgust
- **Toxicity**: binary flag for harmful content

Only the data collection layer changes. The Mastodon scraper is replaced by the news/Reddit/RSS collectors above. The model loading and inference pipeline is imported directly.

### Regulatory Context (manual config per company)
Stored in `configs/companies/<company>.json`. Reviewed and updated annually (these change slowly). Fields:
- `eu_taxonomy_aligned`: `"yes"` / `"partial"` / `"no"`
- `csrd_status`: `"reporting"` / `"preparing"` / `"not_applicable"`
- `sbti_member`: `true` / `false`
- `sbti_target_status`: `"committed"` / `"approved"` / `"achieved"` / `"none"`
- `primary_regulatory_framework`: `"EU"` / `"US"` / `"mixed"`
- `voluntary_eu_standards`: `true` / `false` (companies outside EU that adopt EU standards anyway)

---

## Tech Stack

| Component | Tool | Purpose |
|---|---|---|
| Data collection | Python (requests, feedparser, praw) | API calls, RSS parsing, Reddit JSON |
| Financial data | yfinance | Historical stock and financial data |
| Data manipulation | pandas, numpy | Cleaning, transformation, derived metrics |
| NLP inference | HuggingFace transformers | Sentiment, emotion, toxicity classification |
| Analysis | scipy, statsmodels | Correlation analysis, statistical testing |
| Exports | pandas (CSV/Excel writer) | Power BI-ready output files |
| Visualization | Power BI | Dashboard and case study output |
| Config | JSON | Per-company settings and regulatory scores |

---

## Getting Started

### Prerequisites
- Python 3.10+
- Power BI Desktop (for dashboard development)
- NewsAPI key (free tier at newsapi.org)

### Installation

```bash
git clone https://github.com/AlejLr/ESG_BI_Reporter.git
cd ESG_BI_Reporter
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS/Linux
pip install -r requirements.txt
```

### Configuration

Copy the example config and fill in your API keys:

```bash
cp .env.example .env
```

```env
NEWS_API_KEY=your_newsapi_key_here
OPEN_ESG_API_KEY=your_openESG_key_here   # optional, falls back gracefully
```

### Running the Pipeline

```bash
# Full pipeline for a single company
python -m src.pipeline --company orsted

# Individual stages
python -m src.collectors.financial --company orsted
python -m src.collectors.esg --company orsted
python -m src.collectors.sentiment --company orsted

# Generate case study export
python -m src.exporters.case_study --company orsted
```

Outputs land in `data/exports/orsted/` as CSV files ready for Power BI.

---

## Design Principles

**One company in, one case study out.** The pipeline is parameterized by company. Adding Eneco or ING means adding one JSON config file, not touching any analysis code.

**Free tier only.** Every data source used has a free, no-credit-card access path. The pipeline degrades gracefully when an API is unavailable rather than failing entirely.

**Analysis framework over data aggregation.** The raw data alone is not interesting. The ESG–financial correlation, the sentiment gap, and the greenwashing detection are what make the output worth reading.

**Power BI handles visualization.** The Python pipeline's job is to produce clean, well-structured CSV files. Power BI handles all chart design. This keeps responsibilities separated and avoids over-engineering the Python side.

---

## Roadmap

Each phase ends at a concrete, verifiable milestone. A phase is not complete until the milestone is met, not just when the code is written.

---

### Phase 1: Pipeline Foundation

**Milestone:** run the pipeline for Ørsted and get a clean financial CSV that can be visually verified against known data.

- [ ] Full project scaffold (folders, entry point, `.env` handling)
- [ ] Company config schema defined (JSON)
- [ ] Ørsted config created (financial fields)
- [ ] Financial collector (`src/collectors/financial.py`) using yfinance
- [ ] Financial transformer (`src/transformers/financial.py`)
- [ ] Ørsted financial CSV generated and verified

---

### Phase 2: Research and Methodology

**Milestone:** a methodology notes document exists in `notebooks/` that answers the core design questions before any analysis code is written. Time-boxed to 3 days.

- [ ] ESG metrics audit: what does Open ESG return for Ørsted, what is in their sustainability report, what units are used
- [ ] Greenwashing detection logic defined in plain language
- [ ] Sentiment collection parameters defined: subreddits, search terms, Google News queries per company
- [ ] Ørsted ESG metrics entered manually into config JSON from their latest sustainability report
- [ ] HuggingFace inference pipeline ported from SM Analyzer and confirmed running locally on sample text

---

### Phase 3: Complete Data Layer

**Milestone:** all four processed datasets for Ørsted exist in `data/processed/` and pass a sanity check. HuggingFace inference produces output without errors on a batch of 50 headlines.

- [ ] ESG collector (`src/collectors/esg.py`) with Open ESG API and fallback chain
- [ ] Sentiment collector (`src/collectors/sentiment.py`) with NewsAPI, Reddit JSON, Google News RSS
- [ ] Regulatory loader (`src/collectors/regulatory.py`)
- [ ] Ørsted regulatory config populated
- [ ] ESG transformer (`src/transformers/esg.py`)
- [ ] Sentiment transformer (`src/transformers/sentiment.py`)
- [ ] Data validation checkpoint: all four sources reviewed and confirmed correct

---

### Phase 4: Ørsted Case Study (MVP)

**Milestone:** a case study output file for Ørsted that can be attached to a cold outreach email. Numbers are correct, the narrative is defensible.

- [ ] Methodology research checkpoint (2-3 hours: ESG-financial correlation literature, greenwashing detection defensibility)
- [ ] Correlation analysis (`src/analysis/correlation.py`)
- [ ] Sentiment gap and greenwashing detection (`src/analysis/gap_analysis.py`)
- [ ] Carbon intensity calculation (emissions per unit of revenue)
- [ ] Integrated value scorecard (`src/analysis/integrated_value.py`)
- [ ] CSV exporter (`src/exporters/csv_exporter.py`)
- [ ] Case study summary exporter (`src/exporters/case_study.py`)
- [ ] Ørsted case study output generated and reviewed

---

### Phase 5: Modularity Proof and Quality

**Milestone:** Unilever case study generated in under half a day of work starting from only a new JSON config file. One-pager format implemented.

- [ ] Unilever config created and populated
- [ ] Unilever full pipeline run and case study generated
- [ ] Peer comparison module (`src/analysis/peer_comparison.py`)
- [ ] Code quality pass: error handling, logging, graceful API fallbacks
- [ ] Case study one-pager format designed and implemented (structured layout, key metrics highlighted)
- [ ] Ørsted case study reproduced in the new format

---

### Phase 6: Scale and Portfolio

**Milestone:** a portfolio-ready GitHub repo with a working Power BI dashboard and all four companies covered.

- [ ] Nestlé added (config, pipeline run, case study)
- [ ] Tesla added (config, pipeline run, case study)
- [ ] Power BI portfolio dashboard (multi-company comparison)
- [ ] Power BI case study view (single-company)
- [ ] Notebooks cleaned up and documented
- [ ] README finalized with examples
- [ ] Repo ready for public portfolio
