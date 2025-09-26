import json
from pathlib import Path
from collections import Counter, OrderedDict
from typing import List

# ==============================
# Configuration
# ==============================
ROOT_DIR = Path(__file__).resolve().parent


def classify_result(output_result: str, faulty_result: str) -> str:
    """Classify test results based on output_result and faulty_result."""
    if output_result == "success" and faulty_result == "assertion_failed":
        return "pass"
    elif output_result == "assertion_failed":
        return "assertion_misjudgment"
    elif output_result == "success" and faulty_result == "success":
        return "assertion_invalid"
    elif output_result == "success" and faulty_result in {"runtime_error", "assertion_not_executable"}:
        return "format_error"
    else:
        return "generation_failed"


def fmt_pct(x: float) -> str:
    """Format float 0..1 as a percentage string with 2 decimals."""
    return f"{x * 100:.2f}%"


def safe_mean(xs: List[float]) -> float:
    """Safe mean: return 0.0 if list is empty."""
    return (sum(xs) / len(xs)) if xs else 0.0


def compute_pass_metrics(pass_cnt: int, total: int, success_gen: int):
    """
    Compute per-task pass@1 and pass@5 under two denominators.
    Note: pass@5 here uses the standard independent-trials approximation:
          p5 = 1 - (1 - p1)**5  (applied per task)
    """
    p1_total = (pass_cnt / total) if total > 0 else 0.0
    p5_total = 1.0 - (1.0 - p1_total) ** 5 if total > 0 else 0.0
    p1_succ = (pass_cnt / success_gen) if success_gen > 0 else 0.0
    p5_succ = 1.0 - (1.0 - p1_succ) ** 5 if success_gen > 0 else 0.0

    return {
        "_p1_total": p1_total,
        "_p5_total": p5_total,
        "_p1_succ": p1_succ,
        "_p5_succ": p5_succ,
        "pass@1_total": fmt_pct(p1_total),
        "pass@5_total": fmt_pct(p5_total),
        "pass@1_success": fmt_pct(p1_succ),
        "pass@5_success": fmt_pct(p5_succ),
    }


def label_success_level(p1_succ: float) -> str:
    """Classify tasks into High/Medium/Low levels by pass@1 success rate."""
    if p1_succ > 0.7:
        return "High"
    elif p1_succ >= 0.2:
        return "Medium"
    else:
        return "Low"


def process_model_folder(model_dir: Path):
    """Process one model folder and return its aggregated summary for global report."""
    summary_counter = Counter()
    task_stats = {}

    # Lists for per-task averaging across tasks (macro-average)
    p1_succ_vals: List[float] = []
    p5_succ_vals: List[float] = []

    # Iterate over all task-level JSON files (skip model-level summary JSON)
    for json_file in model_dir.glob("*_test_result.json"):
        if json_file.name.startswith(model_dir.name):
            continue  # skip model-level JSON

        try:
            data = json.loads(json_file.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"[!] Failed to read {json_file}: {e}")
            continue

        if not isinstance(data, list) or not data:
            continue

        task_id = data[0].get("task_id", json_file.stem.split("_")[0])
        counter = Counter()

        for item in data:
            if not isinstance(item, dict):
                continue
            output_result = item.get("output_result", "")
            faulty_result = item.get("faulty_result", "")
            category = classify_result(output_result, faulty_result)
            counter[category] += 1
            summary_counter[category] += 1
            summary_counter["total"] += 1

        total = sum(counter.values())
        pass_cnt = counter.get("pass", 0)
        success_generated = total - counter.get("format_error", 0) - counter.get("generation_failed", 0)

        counter["total"] = total
        counter["success_generated"] = success_generated

        # Store raw values and formatted strings separately
        pass_metrics = compute_pass_metrics(pass_cnt, total, success_generated)
        counter["_p1_total"] = pass_metrics["_p1_total"]
        counter["_p5_total"] = pass_metrics["_p5_total"]
        counter["_p1_succ"] = pass_metrics["_p1_succ"]
        counter["_p5_succ"] = pass_metrics["_p5_succ"]
        counter["pass@1_total"] = pass_metrics["pass@1_total"]
        counter["pass@5_total"] = pass_metrics["pass@5_total"]
        counter["pass@1_success"] = pass_metrics["pass@1_success"]
        counter["pass@5_success"] = pass_metrics["pass@5_success"]

        counter["pass@1_success_level"] = label_success_level(pass_metrics["_p1_succ"])
        task_stats[task_id] = counter

        # Collect per-task values for macro-averaging
        p1_succ_vals.append(pass_metrics["_p1_succ"])
        p5_succ_vals.append(pass_metrics["_p5_succ"])

    # Compute model-level summary with macro-averages across tasks
    pass_counts = [stats.get("pass", 0) for stats in task_stats.values()] or [0]
    max_pass_count = max(pass_counts)
    min_pass_count = min(pass_counts)

    # Macro-average over tasks (correct for heterogeneous task difficulty)
    avg_p1_succ = safe_mean(p1_succ_vals)
    avg_p5_succ = safe_mean(p5_succ_vals)  # FIX: average per-task pass@5 directly

    high_count = sum(1 for v in p1_succ_vals if v > 0.7)
    mid_count = sum(1 for v in p1_succ_vals if 0.2 <= v <= 0.7)
    low_count = sum(1 for v in p1_succ_vals if v < 0.2)

    # Model-level "ALL" summary
    summary_entry = {
        "task_id": "ALL",
        **dict(summary_counter),
        "max_pass_count": max_pass_count,
        "min_pass_count": min_pass_count,
        "avg_pass@1_success": fmt_pct(avg_p1_succ),
        "avg_pass@5_success": fmt_pct(avg_p5_succ),
        "high_pass_tasks": high_count,
        "medium_pass_tasks": mid_count,
        "low_pass_tasks": low_count,
    }

    results = [summary_entry]
    for task_id, counter in task_stats.items():
        results.append({"task_id": task_id, **dict(counter)})

    # Save model-level JSON
    out_file = model_dir / f"{model_dir.name}_test_result.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"[✓] Saved {out_file}")

    # Return model-level summary for EXperiment_result.json
    overall = dict(summary_counter)
    success_generated_all = (
        overall.get("total", 0)
        - overall.get("generation_failed", 0)
        - overall.get("format_error", 0)
    )

    return OrderedDict({
        "model": model_dir.name,
        "task_id": "ALL",
        "pass": overall.get("pass", 0),
        "assertion_misjudgment": overall.get("assertion_misjudgment", 0),
        "assertion_invalid": overall.get("assertion_invalid", 0),
        "success_generated": success_generated_all,
        "format_error": overall.get("format_error", 0),
        "total": overall.get("total", 0),
        "high_pass_tasks": high_count,
        "medium_pass_tasks": mid_count,
        "low_pass_tasks": low_count,
        "generation_error": overall.get("generation_failed", 0),
        # Percentages
        "Correct Assertion": fmt_pct(overall.get("pass", 0) / overall["total"]) if overall.get("total", 0) else "0.00%",
        "Incorrect Assertion": fmt_pct(
            (overall.get("assertion_misjudgment", 0) + overall.get("assertion_invalid", 0)) / overall["total"]
        ) if overall.get("total", 0) else "0.00%",
        "Failed Generation": fmt_pct(
            (overall.get("generation_failed", 0) + overall.get("format_error", 0)) / overall["total"]
        ) if overall.get("total", 0) else "0.00%",
        "avg_pass@1_success": fmt_pct(avg_p1_succ),
        "avg_pass@5_success": fmt_pct(avg_p5_succ),
    })


def main():
    global_results = []
    for model_dir in ROOT_DIR.iterdir():
        if not model_dir.is_dir():
            continue
        if model_dir.name == "test_report":
            continue
        summary = process_model_folder(model_dir)
        if summary:
            global_results.append(summary)

    # Save global summary
    out_file = ROOT_DIR / "Experiment_result.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(global_results, f, indent=2, ensure_ascii=False)

    print(f"[✓] Saved global summary → {out_file}")


if __name__ == "__main__":
    main()
