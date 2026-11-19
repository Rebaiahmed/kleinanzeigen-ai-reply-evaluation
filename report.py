#!/usr/bin/env python3
"""Report reviewed AI-reply evaluations without persisting replies or conversations."""
import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path


class InputError(ValueError):
    pass


def read_jsonl(path):
    rows = []
    with Path(path).open(encoding="utf-8") as stream:
        for number, line in enumerate(stream, 1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise InputError(f"Invalid JSON on line {number} in {path}") from exc
            if not isinstance(row, dict):
                raise InputError(f"Expected an object on line {number} in {path}")
            rows.append(row)
    return rows


def nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def create_report(cases, judgments, metadata):
    if not cases:
        raise InputError("Dataset is empty")
    if not all(nonempty(metadata.get(key)) for key in ("dataset_version", "candidate", "model")):
        raise InputError("dataset_version, candidate and model are required")
    by_id = {}
    for case in cases:
        case_id = case.get("id")
        if not nonempty(case_id) or case_id in by_id:
            raise InputError("Cases must have unique, nonempty IDs")
        if not nonempty(case.get("category")):
            raise InputError(f"Missing category: {case_id}")
        if case.get("source_type") not in ("synthetic", "real_permissioned"):
            raise InputError(f"Invalid source_type: {case_id}")
        if case.get("split") not in ("dev", "validation", "test"):
            raise InputError(f"Invalid split: {case_id}")
        criteria = case.get("criteria")
        if not isinstance(criteria, list) or not criteria:
            raise InputError(f"Missing criteria: {case_id}")
        ids = [item.get("id") if isinstance(item, dict) else None for item in criteria]
        if any(not nonempty(value) for value in ids) or len(set(ids)) != len(ids):
            raise InputError(f"Invalid or duplicate criterion IDs: {case_id}")
        if any(not nonempty(item.get("description")) for item in criteria):
            raise InputError(f"Missing criterion description: {case_id}")
        by_id[case_id] = case

    reviewed = {}
    for judgment in judgments:
        case_id = judgment.get("case_id")
        if case_id not in by_id or case_id in reviewed:
            raise InputError("Judgments must refer to unique, known case IDs")
        if judgment.get("reviewer_type") not in ("human", "model"):
            raise InputError(f"Invalid reviewer_type: {case_id}")
        if judgment.get("generation_status") not in ("ok", "error", "refused"):
            raise InputError(f"Invalid generation_status: {case_id}")
        verdicts = judgment.get("verdicts")
        allowed = {item["id"] for item in by_id[case_id]["criteria"]}
        if not isinstance(verdicts, dict) or not set(verdicts).issubset(allowed):
            raise InputError(f"Unknown or invalid verdicts: {case_id}")
        if any(value not in ("pass", "fail", "unclear") for value in verdicts.values()):
            raise InputError(f"Invalid verdict: {case_id}")
        reviewed[case_id] = judgment

    results = Counter()
    categories = defaultdict(Counter)
    sources = Counter()
    reviewers = Counter()
    splits = Counter()
    for case_id, case in by_id.items():
        judgment = reviewed.get(case_id)
        if judgment is None:
            outcome = "missing"
        elif judgment["generation_status"] != "ok":
            outcome = judgment["generation_status"]
        else:
            verdicts = judgment["verdicts"]
            expected = {item["id"] for item in case["criteria"]}
            if "fail" in verdicts.values():
                outcome = "fail"
            elif set(verdicts) != expected or "unclear" in verdicts.values():
                outcome = "unclear"
            else:
                outcome = "pass"
        results[outcome] += 1
        categories[case["category"]][outcome] += 1
        sources[case["source_type"]] += 1
        splits[case["split"]] += 1
        if judgment:
            reviewers[judgment["reviewer_type"]] += 1
    outcomes = ("pass", "fail", "unclear", "missing", "error", "refused")
    return {
        "schema_version": 1,
        "metadata": metadata,
        "total": len(cases),
        "outcomes": {key: results[key] for key in outcomes},
        "categories": {key: {status: count[status] for status in outcomes} for key, count in sorted(categories.items())},
        "source_types": dict(sorted(sources.items())),
        "splits": dict(sorted(splits.items())),
        "reviewer_types": dict(sorted(reviewers.items())),
        "complete_pass": results["pass"] == len(cases),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases", required=True)
    parser.add_argument("--judgments", required=True)
    parser.add_argument("--dataset-version", required=True)
    parser.add_argument("--candidate", required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    try:
        report = create_report(read_jsonl(args.cases), read_jsonl(args.judgments), {
            "dataset_version": args.dataset_version, "candidate": args.candidate, "model": args.model,
        })
        Path(args.out).write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(json.dumps({"total": report["total"], "outcomes": report["outcomes"], "complete_pass": report["complete_pass"]}))
        return 0 if report["complete_pass"] else 1
    except (InputError, OSError) as exc:
        print(f"Evaluation input error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
