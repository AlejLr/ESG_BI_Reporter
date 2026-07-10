import argparse
import json
import sys
from pathlib import Path


def load_config(company: str) -> dict:
    path = Path(__file__).parent.parent / "configs" / "companies" / f"{company}.json"
    if not path.exists():
        print(f"No config found for '{company}'. Add configs/companies/{company}.json first.")
        sys.exit(1)
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def run(company: str, stage: str) -> None:
    config = load_config(company)
    print(f"[pipeline] company={config['name']}  stage={stage}")

    if stage in ("financial", "all"):
        from src.collectors.financial import collect as collect_financial
        from src.transformers.financial import transform as transform_financial
        from src.exporters.csv_exporter import export
        raw = collect_financial(company, config)
        processed = transform_financial(raw, config)
        out = export(processed, company, "financial")
        print(f"[financial] complete -> {out}")

    if stage in ("esg", "all"):
        if stage == "esg":
            raise NotImplementedError("ESG stage not yet implemented (Phase 3)")
        print("[esg] skipping (not yet implemented)")

    if stage in ("sentiment", "all"):
        if stage == "sentiment":
            raise NotImplementedError("Sentiment stage not yet implemented (Phase 3)")
        print("[sentiment] skipping (not yet implemented)")


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="ESG Integrated Value Analyzer")
    parser.add_argument(
        "--company",
        required=True,
        help="Company slug matching configs/companies/<slug>.json (e.g. orsted)"
    )
    parser.add_argument(
        "--stage",
        choices=["financial", "esg", "sentiment", "all"],
        default="financial",
        help="Pipeline stage to run (default: financial)"
    )
    args = parser.parse_args()
    run(args.company, args.stage)


if __name__ == "__main__":
    main()
