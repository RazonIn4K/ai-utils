"""Cost dashboard example for ai-utils.

Reads a CSV file with historical prompts and models, estimates per-request
spend, and prints per-model / per-month totals. When no CSV is provided, the
script generates synthetic data so you can demo the workflow immediately.

Expected CSV columns:
    date (YYYY-MM-DD), model (e.g., gpt-4o), prompt (text), optional expected_response_tokens
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
from collections import defaultdict
from pathlib import Path
from typing import Iterable

from ai_utils import estimate_llm_cost

Record = dict[str, str]


def load_records(csv_path: Path | None) -> list[Record]:
    if csv_path is None or not csv_path.exists():
        return _generate_synthetic_records()

    records: list[Record] = []
    with csv_path.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            if not row.get("prompt") or not row.get("model"):
                continue
            records.append(row)
    return records


def _generate_synthetic_records() -> list[Record]:
    today = dt.date.today()
    records: list[Record] = []
    models = ["gpt-4o", "gpt-3.5-turbo", "claude-3-sonnet"]
    for month_offset in range(3):
        base_date = today - dt.timedelta(days=30 * month_offset)
        for model in models:
            for i in range(50):
                prompt = f"Synthetic prompt #{i} for {model} in {base_date:%Y-%m}"
                records.append(
                    {
                        "date": base_date.strftime("%Y-%m-%d"),
                        "model": model,
                        "prompt": prompt,
                        "expected_response_tokens": "150",
                    }
                )
    return records


def aggregate_costs(records: Iterable[Record]) -> tuple[dict[str, float], dict[str, float], float]:
    per_model: defaultdict[str, float] = defaultdict(float)
    per_month: defaultdict[str, float] = defaultdict(float)

    for record in records:
        prompt = record["prompt"]
        model = record["model"]
        expected = record.get("expected_response_tokens")
        expected_tokens = int(expected) if expected else None
        cost = estimate_llm_cost(prompt, model=model, expected_response_tokens=expected_tokens)
        per_model[model] += cost

        date = dt.datetime.strptime(record["date"], "%Y-%m-%d").date()
        month_key = date.strftime("%Y-%m")
        per_month[month_key] += cost

    grand_total = sum(per_model.values())
    return dict(per_model), dict(per_month), grand_total


def print_text_summary(per_model: dict[str, float], per_month: dict[str, float], grand_total: float) -> None:
    print("Cost dashboard summary")
    print("======================")
    print("Per-model spend:")
    for model, total in sorted(per_model.items()):
        print(f"  {model:20s} ${total:,.2f}")

    print("\nPer-month spend:")
    for month, total in sorted(per_month.items()):
        print(f"  {month} ${total:,.2f}")

    print(f"\nGrand total (all records): ${grand_total:,.2f}")


def emit_structured_summary(
    per_model: dict[str, float],
    per_month: dict[str, float],
    grand_total: float,
    fmt: str,
    output_path: Path | None,
) -> None:
    if fmt == "text":
        print_text_summary(per_model, per_month, grand_total)
        return

    if fmt == "json":
        payload = {
            "per_model": per_model,
            "per_month": per_month,
            "grand_total": grand_total,
        }
        text = json.dumps(payload, indent=2)
    elif fmt == "csv":
        rows = [("per_model", label, total) for label, total in per_model.items()]
        rows += [("per_month", label, total) for label, total in per_month.items()]
        rows.append(("grand_total", "all", grand_total))
        output = []
        output.append("category,label,total_usd")
        for category, label, total in rows:
            output.append(f"{category},{label},{total:.4f}")
        text = "\n".join(output)
    else:
        raise ValueError(f"Unsupported format: {fmt}")

    if output_path:
        output_path.write_text(text + ("\n" if fmt == "csv" else ""), encoding="utf-8")
    else:
        print(text)


def main() -> None:
    parser = argparse.ArgumentParser(description="ai-utils cost dashboard example")
    parser.add_argument("csv", nargs="?", help="Path to CSV containing historical prompts")
    parser.add_argument(
        "--output-format",
        choices=["text", "json", "csv"],
        default="text",
        help="Format for the summary output",
    )
    parser.add_argument(
        "--output-path",
        help="Optional file path for structured summaries (defaults to stdout)",
    )
    args = parser.parse_args()

    csv_path = Path(args.csv).expanduser() if args.csv else None
    records = load_records(csv_path)
    per_model, per_month, grand_total = aggregate_costs(records)
    output_path = Path(args.output_path).expanduser() if args.output_path else None
    emit_structured_summary(per_model, per_month, grand_total, args.output_format, output_path)


if __name__ == "__main__":
    main()
