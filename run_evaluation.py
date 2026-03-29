"""
run_evaluation.py
=================
Agentic 10-K Copilot 自动化评估脚本

评估维度:
  1. Ragas 指标: Faithfulness, Answer Relevancy, Context Recall, Answer Correctness, Answer Similarity
  2. 系统指标: 延迟、规划步数、检索次数、成功率
  3. 按题目类别 & 难度分组分析

用法:
    python run_evaluation.py                  # 运行全部 10 题
    python run_evaluation.py --quick          # 只运行前 3 题（快速验证）
    python run_evaluation.py --report-only    # 仅从已有 raw results 生成报告
"""

import json
import os
import sys
import time

# Windows GBK 编码兼容：Agent 输出可能包含 Unicode 字符（如 • ✓ ✗），
# 在中文 Windows 上 stdout 默认使用 GBK 导致 UnicodeEncodeError
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
import argparse
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(override=True)
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
os.environ["OPENAI_BASE_URL"] = os.getenv("OPENAI_BASE_URL",
                                           "https://dashscope.aliyuncs.com/compatible-mode/v1")

# ---------------------------------------------------------------------------
# 1. 运行 Agent 收集结果
# ---------------------------------------------------------------------------

def run_agent_on_question(agent_app, question: str, recursion_limit: int = 80):
    """
    对单个问题运行完整 Agent Pipeline, 收集答案、上下文和执行统计.
    """
    inputs = {"question": question}
    config = {"recursion_limit": recursion_limit}

    start_time = time.time()
    agent_state = None
    step_count = 0
    retrieval_count = 0
    plan_steps_total = 0

    try:
        for plan_output in agent_app.stream(inputs, config=config):
            step_count += 1
            for _, state_value in plan_output.items():
                agent_state = state_value

                # 统计检索次数
                curr = state_value.get("curr_state", "")
                if curr in ("retrieve_chunks", "retrieve_summaries",
                            "retrieve_book_quotes"):
                    retrieval_count += 1

                # 记录计划步数
                plan = state_value.get("plan")
                if plan and isinstance(plan, list):
                    plan_steps_total = max(plan_steps_total, len(plan))

        elapsed = time.time() - start_time
        answer = (agent_state.get("response", "") or "") if agent_state else ""
        # response 可能是 dict（来自 qualitative_answer_workflow）
        if isinstance(answer, dict):
            answer = answer.get("answer", str(answer))

        context = (agent_state.get("aggregated_context", "") or "") if agent_state else ""

        return {
            "answer": answer,
            "contexts": [context] if context else [],
            "latency_seconds": round(elapsed, 1),
            "step_count": step_count,
            "retrieval_count": retrieval_count,
            "plan_steps": plan_steps_total,
            "success": True,
            "error": None,
        }
    except Exception as e:
        elapsed = time.time() - start_time
        return {
            "answer": "",
            "contexts": [],
            "latency_seconds": round(elapsed, 1),
            "step_count": step_count,
            "retrieval_count": retrieval_count,
            "plan_steps": plan_steps_total,
            "success": False,
            "error": str(e),
        }


def collect_results(questions: list, agent_app, output_path: str):
    """对所有问题运行 Agent 并保存原始结果."""
    results = []
    total = len(questions)

    for idx, q in enumerate(questions):
        qid = q["id"]
        print(f"\n{'='*60}")
        print(f"[{idx+1}/{total}] {qid}: {q['question'][:60]}...")
        print(f"{'='*60}")

        result = run_agent_on_question(agent_app, q["question"])
        result["id"] = qid
        result["question"] = q["question"]
        result["ground_truth"] = q["ground_truth"]
        result["category"] = q["category"]
        result["difficulty"] = q["difficulty"]
        results.append(result)

        status = "OK" if result["success"] else f"FAIL: {result['error'][:80]}"
        print(f"  -> {status} | {result['latency_seconds']}s | "
              f"steps={result['step_count']} | retrievals={result['retrieval_count']}")

        # 每题保存一次，防止中途失败丢失数据
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

    return results


# ---------------------------------------------------------------------------
# 2. 计算 Ragas 指标
# ---------------------------------------------------------------------------

def compute_ragas_metrics(results: list) -> dict:
    """使用 Ragas 0.1.7 框架计算 RAG 质量指标."""
    try:
        from datasets import Dataset
        from ragas import evaluate
        from ragas.metrics import (
            faithfulness,
            answer_relevancy,
            context_recall,
            answer_correctness,
            answer_similarity,
        )
        from ragas.llms import LangchainLLMWrapper
        from ragas.embeddings import LangchainEmbeddingsWrapper
        from langchain_openai import ChatOpenAI
        from functions_for_pipeline import DashScopeEmbeddings

        # 只用成功的结果
        valid = [r for r in results if r["success"] and r["answer"]]
        if not valid:
            return {"error": "No valid results to evaluate"}

        # 配置 Ragas 使用 qwen-max 作为评估 LLM + DashScope 兼容 Embedding
        ragas_llm = LangchainLLMWrapper(
            ChatOpenAI(temperature=0, model_name="qwen-max", max_tokens=2000)
        )
        ragas_emb = LangchainEmbeddingsWrapper(
            DashScopeEmbeddings(model="text-embedding-v3")
        )

        # 构建 Dataset
        data = {
            "question": [r["question"] for r in valid],
            "answer": [r["answer"] for r in valid],
            "contexts": [r["contexts"] for r in valid],
            "ground_truth": [r["ground_truth"] for r in valid],
        }
        dataset = Dataset.from_dict(data)

        metrics = [faithfulness, answer_relevancy, context_recall,
                   answer_correctness, answer_similarity]

        print("\n[Ragas] Computing metrics (this may take a while)...")
        result = evaluate(
            dataset,
            metrics=metrics,
            llm=ragas_llm,
            embeddings=ragas_emb,
            raise_exceptions=False,
        )

        return {
            "faithfulness": round(result["faithfulness"], 4),
            "answer_relevancy": round(result["answer_relevancy"], 4),
            "context_recall": round(result["context_recall"], 4),
            "answer_correctness": round(result["answer_correctness"], 4),
            "answer_similarity": round(result["answer_similarity"], 4),
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"[Ragas] Error: {e}")
        return {"error": str(e)}


# ---------------------------------------------------------------------------
# 3. 自定义指标（不依赖 Ragas，确保始终可计算）
# ---------------------------------------------------------------------------

def compute_custom_metrics(results: list) -> dict:
    """计算系统级和业务级自定义指标."""
    total = len(results)
    successful = [r for r in results if r["success"]]
    failed = [r for r in results if not r["success"]]

    # --- 系统指标 ---
    success_rate = len(successful) / total if total else 0
    avg_latency = (sum(r["latency_seconds"] for r in successful) / len(successful)
                   if successful else 0)
    avg_steps = (sum(r["step_count"] for r in successful) / len(successful)
                 if successful else 0)
    avg_retrievals = (sum(r["retrieval_count"] for r in successful) / len(successful)
                      if successful else 0)
    avg_plan_steps = (sum(r["plan_steps"] for r in successful) / len(successful)
                      if successful else 0)

    # --- 答案覆盖度（简单文本匹配）---
    # 检查 ground_truth 中的关键数字是否出现在 answer 中
    import re
    coverage_scores = []
    for r in successful:
        if not r["answer"]:
            coverage_scores.append(0)
            continue
        # 提取 ground_truth 中的数字
        gt_numbers = set(re.findall(r'\$[\d,.]+\s*(?:billion|million|B|M)?', r["ground_truth"]))
        gt_percentages = set(re.findall(r'[\d.]+%', r["ground_truth"]))
        key_figures = gt_numbers | gt_percentages

        if not key_figures:
            coverage_scores.append(1.0)  # 非数字问题，跳过
            continue

        hits = sum(1 for fig in key_figures if fig in r["answer"])
        coverage_scores.append(hits / len(key_figures))

    avg_number_coverage = (sum(coverage_scores) / len(coverage_scores)
                           if coverage_scores else 0)

    # --- 答案长度分布 ---
    answer_lengths = [len(r["answer"]) for r in successful if r["answer"]]
    avg_answer_length = (sum(answer_lengths) / len(answer_lengths)
                         if answer_lengths else 0)

    # --- 上下文长度分布 ---
    context_lengths = [len(c) for r in successful for c in r["contexts"] if c]
    avg_context_length = (sum(context_lengths) / len(context_lengths)
                          if context_lengths else 0)

    # --- 按类别分组 ---
    from collections import defaultdict
    by_category = defaultdict(list)
    by_difficulty = defaultdict(list)
    for r in results:
        by_category[r["category"]].append(r)
        by_difficulty[r["difficulty"]].append(r)

    category_stats = {}
    for cat, items in by_category.items():
        s = [r for r in items if r["success"]]
        category_stats[cat] = {
            "count": len(items),
            "success_rate": len(s) / len(items) if items else 0,
            "avg_latency": round(sum(r["latency_seconds"] for r in s) / len(s), 1) if s else 0,
        }

    difficulty_stats = {}
    for diff, items in by_difficulty.items():
        s = [r for r in items if r["success"]]
        difficulty_stats[diff] = {
            "count": len(items),
            "success_rate": len(s) / len(items) if items else 0,
            "avg_latency": round(sum(r["latency_seconds"] for r in s) / len(s), 1) if s else 0,
        }

    return {
        "total_questions": total,
        "successful": len(successful),
        "failed": len(failed),
        "success_rate": round(success_rate, 4),
        "avg_latency_seconds": round(avg_latency, 1),
        "avg_steps_per_question": round(avg_steps, 1),
        "avg_retrievals_per_question": round(avg_retrievals, 1),
        "avg_plan_steps": round(avg_plan_steps, 1),
        "avg_number_coverage": round(avg_number_coverage, 4),
        "avg_answer_length_chars": round(avg_answer_length),
        "avg_context_length_chars": round(avg_context_length),
        "by_category": category_stats,
        "by_difficulty": difficulty_stats,
    }


# ---------------------------------------------------------------------------
# 4. 生成 Markdown 评估报告
# ---------------------------------------------------------------------------

def generate_report(results: list, ragas_metrics: dict, custom_metrics: dict,
                    output_dir: str):
    """生成 Markdown 格式的评估报告."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    cm = custom_metrics

    lines = []
    lines.append("# Agentic 10-K Copilot — Evaluation Report")
    lines.append(f"\n> Generated: {timestamp}")
    lines.append(f"> Questions: {cm['total_questions']} | "
                 f"Success Rate: {cm['success_rate']*100:.1f}%")
    lines.append("")

    # --- Ragas 指标 ---
    lines.append("## 1. RAG Quality Metrics (Ragas)")
    lines.append("")
    if "error" in ragas_metrics:
        lines.append(f"Ragas evaluation encountered an error: `{ragas_metrics['error']}`")
        lines.append("")
        lines.append("Custom fallback metrics are provided below.")
    else:
        lines.append("| Metric | Score | Description |")
        lines.append("|--------|-------|-------------|")
        descriptions = {
            "faithfulness": "答案是否忠实于检索到的文档（防幻觉核心指标）",
            "answer_relevancy": "答案是否切题、与问题相关",
            "context_recall": "关键信息是否被成功检索到",
            "answer_correctness": "答案与标准答案的匹配程度",
            "answer_similarity": "答案与标准答案的语义相似度",
        }
        for metric, score in ragas_metrics.items():
            if metric != "error":
                desc = descriptions.get(metric, "")
                lines.append(f"| **{metric}** | {score:.4f} | {desc} |")
    lines.append("")

    # --- 系统指标 ---
    lines.append("## 2. System Performance Metrics")
    lines.append("")
    lines.append("| Metric | Value |")
    lines.append("|--------|-------|")
    lines.append(f"| Success Rate | {cm['success_rate']*100:.1f}% ({cm['successful']}/{cm['total_questions']}) |")
    lines.append(f"| Avg Latency | {cm['avg_latency_seconds']}s |")
    lines.append(f"| Avg Steps per Question | {cm['avg_steps_per_question']} |")
    lines.append(f"| Avg Retrieval Calls | {cm['avg_retrievals_per_question']} |")
    lines.append(f"| Avg Plan Steps | {cm['avg_plan_steps']} |")
    lines.append(f"| Avg Answer Length | {cm['avg_answer_length_chars']} chars |")
    lines.append(f"| Avg Context Length | {cm['avg_context_length_chars']} chars |")
    lines.append(f"| Key Number Coverage | {cm['avg_number_coverage']*100:.1f}% |")
    lines.append("")

    # --- 按类别分析 ---
    lines.append("## 3. Performance by Question Category")
    lines.append("")
    lines.append("| Category | Count | Success Rate | Avg Latency |")
    lines.append("|----------|-------|--------------|-------------|")
    for cat, stats in cm["by_category"].items():
        lines.append(f"| {cat} | {stats['count']} | "
                     f"{stats['success_rate']*100:.0f}% | {stats['avg_latency']}s |")
    lines.append("")

    # --- 按难度分析 ---
    lines.append("## 4. Performance by Difficulty")
    lines.append("")
    lines.append("| Difficulty | Count | Success Rate | Avg Latency |")
    lines.append("|------------|-------|--------------|-------------|")
    for diff in ["easy", "medium", "hard"]:
        if diff in cm["by_difficulty"]:
            stats = cm["by_difficulty"][diff]
            lines.append(f"| {diff} | {stats['count']} | "
                         f"{stats['success_rate']*100:.0f}% | {stats['avg_latency']}s |")
    lines.append("")

    # --- 逐题详情 ---
    lines.append("## 5. Per-Question Results")
    lines.append("")
    for r in results:
        status = "PASS" if r["success"] else "FAIL"
        lines.append(f"### {r['id']} [{status}] — {r['category']} / {r['difficulty']}")
        lines.append(f"**Question:** {r['question']}")
        lines.append("")
        if r["success"]:
            answer_preview = r["answer"][:500] + ("..." if len(r["answer"]) > 500 else "")
            lines.append(f"**Agent Answer:** {answer_preview}")
            lines.append("")
            lines.append(f"**Ground Truth:** {r['ground_truth'][:300]}...")
            lines.append("")
            lines.append(f"Latency: {r['latency_seconds']}s | "
                         f"Steps: {r['step_count']} | "
                         f"Retrievals: {r['retrieval_count']}")
        else:
            lines.append(f"**Error:** {r['error']}")
        lines.append("")
        lines.append("---")
        lines.append("")

    # --- 评估方法说明 ---
    lines.append("## 6. Evaluation Methodology")
    lines.append("")
    lines.append("### 6.1 Dataset Design")
    lines.append("- 10 questions covering 6 categories: financial_metrics, segment_analysis, "
                 "profitability, product_performance, risk_factors, capital_allocation, "
                 "operating_expenses, balance_sheet, product_launches")
    lines.append("- 3 difficulty levels: easy (direct lookup), medium (multi-step analysis), "
                 "hard (synthesis across sections)")
    lines.append("- Ground truth answers extracted directly from Apple FY2025 10-K filing")
    lines.append("")
    lines.append("### 6.2 Metrics Explanation")
    lines.append("- **Faithfulness** (Ragas): Measures whether every claim in the answer "
                 "can be traced back to the retrieved context. Core anti-hallucination metric.")
    lines.append("- **Answer Relevancy** (Ragas): Evaluates if the answer addresses "
                 "the question asked, penalizing off-topic content.")
    lines.append("- **Context Recall** (Ragas): Checks if the retrieval system found "
                 "all information needed to answer correctly.")
    lines.append("- **Answer Correctness** (Ragas): Combines factual overlap and semantic "
                 "similarity with ground truth.")
    lines.append("- **Key Number Coverage** (Custom): Percentage of key financial figures "
                 "from ground truth that appear in the agent's answer.")
    lines.append("- **Success Rate** (Custom): Percentage of questions completed without errors.")
    lines.append("")
    lines.append("### 6.3 Anti-Hallucination Design")
    lines.append("This system implements 3-layer hallucination prevention:")
    lines.append("1. **Input Layer**: Question anonymization replaces named entities with variables")
    lines.append("2. **Retrieval Layer**: Distilled content grounding check against original context")
    lines.append("3. **Output Layer**: Final answer grounding check against aggregated context")
    lines.append("")

    report_text = "\n".join(lines)
    report_path = os.path.join(output_dir, "eval_report.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_text)
    print(f"\n[Report] Saved to {report_path}")
    return report_path


# ---------------------------------------------------------------------------
# 5. 主流程
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Evaluate Agentic 10-K Copilot")
    parser.add_argument("--quick", action="store_true",
                        help="Run only first 3 questions for quick validation")
    parser.add_argument("--report-only", action="store_true",
                        help="Generate report from existing raw results without running agent")
    parser.add_argument("--skip-ragas", action="store_true",
                        help="Skip Ragas metrics (faster, only custom metrics)")
    args = parser.parse_args()

    # 创建输出目录
    output_dir = "eval_results"
    os.makedirs(output_dir, exist_ok=True)
    raw_path = os.path.join(output_dir, "eval_raw_results.json")

    # 加载测试题
    with open("eval_questions.json", "r", encoding="utf-8") as f:
        questions = json.load(f)

    if args.quick:
        questions = questions[:3]
        print(f"[Quick mode] Running {len(questions)} questions only")

    # --- 收集结果 ---
    if args.report_only:
        print(f"[Report-only mode] Loading results from {raw_path}")
        with open(raw_path, "r", encoding="utf-8") as f:
            results = json.load(f)
    else:
        print("="*60)
        print("  Agentic 10-K Copilot — Automated Evaluation")
        print("="*60)
        print(f"  Questions: {len(questions)}")
        print(f"  Output: {output_dir}/")
        print("="*60)

        # 导入并创建 Agent
        from functions_for_pipeline import create_agent
        agent_app = create_agent()

        results = collect_results(questions, agent_app, raw_path)

        print(f"\n[Done] Raw results saved to {raw_path}")

    # --- 计算指标 ---
    print("\n[Metrics] Computing custom metrics...")
    custom_metrics = compute_custom_metrics(results)

    ragas_metrics = {"error": "Skipped by user (--skip-ragas)"}
    if not args.skip_ragas:
        ragas_metrics = compute_ragas_metrics(results)

    # 保存指标
    all_metrics = {"ragas": ragas_metrics, "custom": custom_metrics}
    metrics_path = os.path.join(output_dir, "eval_metrics.json")
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(all_metrics, f, ensure_ascii=False, indent=2)
    print(f"[Metrics] Saved to {metrics_path}")

    # --- 生成报告 ---
    generate_report(results, ragas_metrics, custom_metrics, output_dir)

    # --- 终端摘要 ---
    print("\n" + "="*60)
    print("  EVALUATION SUMMARY")
    print("="*60)
    print(f"  Success Rate:     {custom_metrics['success_rate']*100:.1f}%")
    print(f"  Avg Latency:      {custom_metrics['avg_latency_seconds']}s")
    print(f"  Number Coverage:  {custom_metrics['avg_number_coverage']*100:.1f}%")
    if "error" not in ragas_metrics:
        print(f"  Faithfulness:     {ragas_metrics.get('faithfulness', 'N/A')}")
        print(f"  Answer Relevancy: {ragas_metrics.get('answer_relevancy', 'N/A')}")
        print(f"  Answer Correct:   {ragas_metrics.get('answer_correctness', 'N/A')}")
        print(f"  Context Recall:   {ragas_metrics.get('context_recall', 'N/A')}")
    print("="*60)


if __name__ == "__main__":
    main()
