"""
ragas_eval.py — RAGAS Scorecard with Edge-case Optimizations
=============================================================
Mục tiêu:
  - Chạy scorecard dùng RAGAS tương tự eval.py
  - Giữ pipeline ổn định khi gặp edge-cases (timeout, thiếu context, câu không có expected source)
  - Có fallback để không làm hỏng toàn bộ lượt chấm
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from rag_answer import rag_answer
from eval import BASELINE_CONFIG, VARIANT_CONFIG, score_context_recall


TEST_QUESTIONS_PATH = Path(__file__).parent / "data" / "test_questions.json"
RESULTS_DIR = Path(__file__).parent / "results"


def _load_questions(test_questions: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
    if test_questions is not None:
        return test_questions
    with open(TEST_QUESTIONS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _is_error_answer(answer: str) -> bool:
    return (not answer) or answer.startswith("ERROR") or answer == "PIPELINE_NOT_IMPLEMENTED"


def _is_abstain_answer(answer: str) -> bool:
    text = (answer or "").lower()
    keys = [
        "không tìm thấy đủ thông tin",
        "khong tim thay du thong tin",
        "không đủ thông tin",
        "insufficient",
        "not enough information",
        "cannot answer from the provided context",
    ]
    return any(k in text for k in keys)


def _build_ragas_sample(row: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    # RAGAS cần question/answer/contexts/ground_truth.
    if _is_error_answer(row["answer"]):
        return None
    if not row["contexts"]:
        return None

    return {
        "id": row["id"],
        "question": row["query"],
        "answer": row["answer"],
        "contexts": row["contexts"],
        "ground_truth": row.get("expected_answer", ""),
    }


def _evaluate_with_ragas(samples: List[Dict[str, Any]]) -> Tuple[Dict[str, Dict[str, Optional[float]]], str]:
    """
    Trả về map id -> metric scores (0-1 từ ragas) và status.
    Có tương thích nhiều version ragas.
    """
    if not samples:
        return {}, "no-valid-samples"

    try:
        from ragas import evaluate
        metrics = []
        try:
            # ragas mới
            from ragas.metrics import Faithfulness, ResponseRelevancy, ContextRecall

            metrics = [Faithfulness(), ResponseRelevancy(), ContextRecall()]
        except Exception:
            # ragas cũ
            from ragas.metrics import faithfulness, answer_relevancy, context_recall

            metrics = [faithfulness, answer_relevancy, context_recall]

        dataset = None
        try:
            from ragas.dataset_schema import RagasDataset

            dataset = RagasDataset.from_list(samples)
        except Exception:
            from datasets import Dataset

            dataset = Dataset.from_list(samples)

        result = evaluate(dataset=dataset, metrics=metrics)
        df = result.to_pandas()

        out: Dict[str, Dict[str, Optional[float]]] = {}
        for _, r in df.iterrows():
            qid = str(r.get("id", ""))
            out[qid] = {
                "faithfulness": r.get("faithfulness"),
                "relevance": r.get("answer_relevancy"),
                "context_recall": r.get("context_recall"),
            }
        return out, "ragas-ok"
    except Exception as e:
        return {}, f"ragas-failed: {e}"


def _score_0_1_to_1_5(value: Optional[float]) -> Optional[int]:
    if value is None:
        return None
    v = max(0.0, min(1.0, float(value)))
    if v >= 0.8:
        return 5
    if v >= 0.6:
        return 4
    if v >= 0.4:
        return 3
    if v >= 0.2:
        return 2
    return 1


def run_ragas_scorecard(
    config: Dict[str, Any],
    test_questions: Optional[List[Dict[str, Any]]] = None,
    verbose: bool = True,
) -> List[Dict[str, Any]]:
    questions = _load_questions(test_questions)
    rows: List[Dict[str, Any]] = []

    if verbose:
        print("=" * 70)
        print(f"RAGAS scorecard: {config.get('label', 'unnamed')}")
        print(f"Config: {config}")
        print("=" * 70)

    for q in questions:
        qid = q["id"]
        query = q["question"]
        expected_answer = q.get("expected_answer", "")
        expected_sources = q.get("expected_sources", [])

        try:
            result = rag_answer(
                query=query,
                retrieval_mode=config.get("retrieval_mode", "dense"),
                top_k_search=config.get("top_k_search", 10),
                top_k_select=config.get("top_k_select", 3),
                use_rerank=config.get("use_rerank", False),
                verbose=False,
            )
            answer = result["answer"]
            chunks_used = result["chunks_used"]
        except Exception as e:
            answer = f"ERROR: {e}"
            chunks_used = []

        contexts = [c.get("text", "") for c in chunks_used if c.get("text")]

        rows.append(
            {
                "id": qid,
                "query": query,
                "answer": answer,
                "expected_answer": expected_answer,
                "expected_sources": expected_sources,
                "chunks_used": chunks_used,
                "contexts": contexts,
                "config_label": config.get("label", "unnamed"),
                "ragas_status": "pending",
                "faithfulness": None,
                "relevance": None,
                "context_recall": None,
                "completeness": None,
                "notes": "",
            }
        )

    valid_samples = [s for s in (_build_ragas_sample(r) for r in rows) if s is not None]
    ragas_scores, ragas_status = _evaluate_with_ragas(valid_samples)

    for row in rows:
        answer = row["answer"]
        expected_sources = row["expected_sources"]

        # recall luôn tính từ retrieval thật để ổn định hơn edge-case.
        recall = score_context_recall(row["chunks_used"], expected_sources)
        row["context_recall"] = recall["score"]

        # Edge-case 1: pipeline lỗi
        if _is_error_answer(answer):
            row["faithfulness"] = 1
            row["relevance"] = 1
            row["completeness"] = 1
            row["ragas_status"] = "error-answer"
            row["notes"] = "Pipeline error -> forced low scores"
            continue

        # Edge-case 2: câu không có expected source (unanswerable/abstain test)
        if not expected_sources:
            if _is_abstain_answer(answer):
                row["faithfulness"] = 5
                row["relevance"] = 5
                row["completeness"] = 5
                row["ragas_status"] = "edge-abstain-pass"
                row["notes"] = "No expected source + proper abstain"
            else:
                row["faithfulness"] = 2
                row["relevance"] = 2
                row["completeness"] = 2
                row["ragas_status"] = "edge-abstain-fail"
                row["notes"] = "No expected source but model did not abstain"
            continue

        # Edge-case 3: không có context retrieve
        if not row["contexts"]:
            row["faithfulness"] = 1
            row["relevance"] = 1
            row["completeness"] = 1
            row["ragas_status"] = "no-context"
            row["notes"] = "No retrieved context"
            continue

        # RAGAS score nếu có
        score_pack = ragas_scores.get(row["id"], {})
        row["faithfulness"] = _score_0_1_to_1_5(score_pack.get("faithfulness"))
        row["relevance"] = _score_0_1_to_1_5(score_pack.get("relevance"))

        # Completeness: ưu tiên relevance/faithfulness làm proxy khi thiếu metric completeness chuẩn của ragas.
        if row["faithfulness"] is not None and row["relevance"] is not None:
            row["completeness"] = round((row["faithfulness"] + row["relevance"]) / 2)
        else:
            row["completeness"] = 3

        row["ragas_status"] = ragas_status
        row["notes"] = f"RAGAS status: {ragas_status}"

    return rows


def save_ragas_results(rows: List[Dict[str, Any]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)


def summarize(rows: List[Dict[str, Any]]) -> Dict[str, Optional[float]]:
    def avg(metric: str) -> Optional[float]:
        vals = [r[metric] for r in rows if r.get(metric) is not None]
        if not vals:
            return None
        return round(sum(vals) / len(vals), 3)

    return {
        "faithfulness": avg("faithfulness"),
        "relevance": avg("relevance"),
        "context_recall": avg("context_recall"),
        "completeness": avg("completeness"),
    }


def run_ab_ragas(verbose: bool = True) -> Dict[str, Any]:
    baseline_rows = run_ragas_scorecard(BASELINE_CONFIG, verbose=verbose)
    variant_rows = run_ragas_scorecard(VARIANT_CONFIG, verbose=verbose)

    baseline_summary = summarize(baseline_rows)
    variant_summary = summarize(variant_rows)

    delta = {}
    for k in baseline_summary:
        b = baseline_summary[k]
        v = variant_summary[k]
        delta[k] = None if (b is None or v is None) else round(v - b, 3)

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    save_ragas_results(baseline_rows, RESULTS_DIR / "ragas_baseline.json")
    save_ragas_results(variant_rows, RESULTS_DIR / "ragas_variant.json")

    report = {
        "baseline": baseline_summary,
        "variant": variant_summary,
        "delta": delta,
    }

    with open(RESULTS_DIR / "ragas_ab_summary.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    return report


if __name__ == "__main__":
    print("=" * 60)
    print("RAGAS Evaluation")
    print("=" * 60)

    report = run_ab_ragas(verbose=True)
    print("\nSummary:")
    print(json.dumps(report, ensure_ascii=False, indent=2))
