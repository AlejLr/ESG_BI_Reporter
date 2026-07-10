from pathlib import Path

import pandas as pd

_ROOT = Path(__file__).resolve().parent.parent.parent


def export(data: dict, company: str, label: str) -> Path:
    out_dir = _ROOT / "data" / "exports" / company
    out_dir.mkdir(parents=True, exist_ok=True)

    for key, value in data.items():
        if isinstance(value, pd.DataFrame) and not value.empty:
            path = out_dir / f"{label}_{key}.csv"
            save_index = not isinstance(value.index, pd.RangeIndex)
            value.to_csv(path, index=save_index)
            print(f"  saved: {path.relative_to(_ROOT)}")

    return out_dir
