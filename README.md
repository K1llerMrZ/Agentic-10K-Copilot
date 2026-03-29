# Agentic 10-K Copilot — 智能财报研读系统

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.0.49-green.svg)](https://github.com/langchain-ai/langgraph)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.32-red.svg)](https://streamlit.io/)

基于 **LangGraph Plan-and-Execute** 架构的 Agentic RAG 系统，对 Apple 10-K 年报进行智能多轮问答。系统具备问题匿名化、动态规划、多向量库路由检索、双重事实性验证（Grounding Check）和自动重规划能力。

> 本项目改造自 [NirDiamant/Controllable-RAG-Agent](https://github.com/NirDiamant/Controllable-RAG-Agent)，将原 Harry Potter 小说问答场景迁移至 **金融财报分析** 领域，使用 **qwen-max (通义千问)** 作为 LLM，通过阿里云 DashScope API 调用。

---

## 系统架构

```
用户提问
  │
  ▼
[匿名化] 将命名实体替换为变量（Apple→X, iPhone→Y, FY2025→Z）
  │
  ▼
[制定计划] LLM 生成分步执行计划
  │
  ▼
[还原计划] 将变量还原为真实实体
  │
  ▼
[细化计划] 确保每步可被检索工具或回答工具执行
  │
  ▼
[任务路由] ──┬── Tool A: 正文切片检索 (FAISS + BM25 Hybrid)
             ├── Tool B: 章节摘要检索 (FAISS + BM25 Hybrid)
             ├── Tool C: 财务指标检索 (FAISS Dense, k=10)
             └── Tool D: 基于已有上下文直接回答
  │
  ▼
[重新规划] 根据已收集信息更新剩余计划 (MAX_REPLAN_RETRIES=5 兜底)
  │
  ├─ 信息充足 → [生成最终答案] → [数字审计] → 输出
  └─ 信息不足 → 回到 [细化计划] 继续检索
```

> **数字审计 (Self-Correction)**：自动提取上下文中的 `$`/`%` 数字，检查答案覆盖率，不足时强制重新生成。

## 核心特性

**Agentic RAG 架构**
- Plan-and-Execute 模式：先制定全局计划，再逐步执行并动态调整
- 基于 LangGraph StateGraph 的有限状态机，12 个节点协作完成复杂问答

**多源向量库路由检索**
- 3 个 FAISS 向量库覆盖不同信息粒度：正文切片（细节）、章节摘要（概览）、财务指标（数字）
- Task Handler 根据任务性质自动选择最合适的检索源

**三层幻觉防护**
- 输入层：问题匿名化，阻断 LLM 使用预训练知识
- 检索层：精炼内容 Grounding Check，确保过滤后的内容忠实于原始检索结果
- 输出层：答案 Grounding Check，确保最终回答忠实于聚合上下文

**Chain-of-Thought 推理**
- Few-shot 财务推理示例引导 LLM 进行数值计算、归纳总结和诚实拒答

**实时可视化**
- Streamlit + PyVis 网络图，实时展示 Agent 执行到哪个节点

## 技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| LLM | qwen-max | 通义千问，通过 DashScope OpenAI 兼容 API 调用 |
| Embedding | text-embedding-v3 | 阿里云 DashScope 文本向量模型 |
| Agent 框架 | LangGraph 0.0.49 | 基于 StateGraph 的有限状态机 |
| 向量数据库 | FAISS + BM25 | 混合检索：Dense (FAISS) + Sparse (BM25) + RRF 重排 |
| LLM 编排 | LangChain 0.1.20 | Prompt + Chain + Output Parser |
| 前端 | Streamlit 1.32 + PyVis | 实时 Agent 流程可视化 |
| 评估 | Ragas 0.1.7 | 自动化 RAG 质量评估 |

## 快速开始

### 环境要求

- Python 3.10+
- 阿里云 DashScope API Key（[获取地址](https://dashscope.console.aliyun.com/)）

### 安装

```bash
git clone https://github.com/K1llerMrZ/Agentic-10K-Copilot.git
cd Agentic-10K-Copilot

python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
```

### 配置

复制 `.env.example` 为 `.env` 并填入你的 API Key：

```bash
cp .env.example .env
```

```env
OPENAI_API_KEY=your-dashscope-api-key
OPENAI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
```

### 重建向量库（可选）

项目已包含预构建的向量库。如需从 PDF 重新构建：

```bash
python build_vector_stores.py
```

该脚本会从 `_10-K-2025-As-Filed.pdf` 生成三个 FAISS 向量库：
- `chunks_vector_store/` — 正文切片（1000 tokens, 200 overlap）
- `chapter_summaries_vector_store/` — LLM 生成的章节摘要
- `book_quotes_vectorstore/` — 含数字的财务数据句子

### 运行

```bash
streamlit run simulate_agent.py
```

打开浏览器访问 `http://localhost:8501`，输入问题即可开始分析。

### Notebook 版本

逐步教程和评估流程详见：

```
sophisticated_rag_agent_apple10-k.ipynb
```

## 项目结构

```
├── .env.example                       # API 配置模板
├── .gitignore
├── LICENSE
├── README.md
├── requirements.txt                   # 锁定的依赖版本
├── _10-K-2025-As-Filed.pdf            # Apple 10-K 年报原始数据
├── functions_for_pipeline.py          # 核心引擎（LLM Chains + Agent Graph）
├── helper_functions.py                # 工具函数（PDF分章、token计数等）
├── simulate_agent.py                  # Streamlit 前端入口
├── build_vector_stores.py             # 向量库一键构建脚本
├── sophisticated_rag_agent_apple10-k.ipynb  # Jupyter Notebook 教程
├── eval_questions.json                # 评估数据集（10 题，含 Ground Truth）
├── run_evaluation.py                  # 自动化评估脚本
├── eval_results/                      # 评估结果输出
│   ├── eval_raw_results.json          #   每题原始回答与元数据
│   ├── eval_metrics.json              #   汇总指标 JSON
│   └── eval_report.md                 #   可读评估报告
├── chunks_vector_store/               # FAISS 向量库：正文切片
├── chapter_summaries_vector_store/    # FAISS 向量库：章节摘要
└── book_quotes_vectorstore/           # FAISS 向量库：财务指标句子
```

## 评估结果

基于 Apple FY2025 10-K 年报设计 10 个问答对，覆盖 9 个类别、3 个难度等级，使用 Ragas 框架 + 自定义指标进行自动化评估。

### RAG 质量指标（Ragas）

| 指标 | 得分 | 说明 |
|------|------|------|
| **Faithfulness** | **86.4%** | 答案忠实于检索文档，三层幻觉防护有效 |
| **Answer Relevancy** | **92.4%** | 回答高度切题，极少偏离主题 |
| **Context Recall** | **75.2%** | Hybrid Search (BM25+Dense) 提升关键词召回 |
| **Answer Correctness** | **63.1%** | 事实正确率，含语义相似度与关键数字匹配 |
| **Answer Similarity** | **85.5%** | 答案与 Ground Truth 的语义相似度 |

> 注：Ragas 评估基于 LLM-as-Judge，单次运行存在 ±5% 的波动区间。多次评估中 Faithfulness 最高达 98%，Context Recall 最高达 88.3%。

### 系统性能指标

| 指标 | 值 |
|------|------|
| **成功率** | **100%**（10/10） |
| **平均延迟** | 119.9s |
| **平均执行步数** | 9.8 steps |
| **平均检索次数** | 1.2 次/问题 |
| **关键数字覆盖率** | 34.4% |

### 按难度分布

| 难度 | 题数 | 成功率 | 平均延迟 |
|------|------|--------|----------|
| Easy（直接查找） | 3 | 100% | 100.3s |
| Medium（多步分析） | 4 | 100% | 123.9s |
| Hard（跨章节综合） | 3 | 100% | 134.4s |

### 评估指标说明

| 指标 | 类型 | 含义 |
|------|------|------|
| **Faithfulness** | Ragas | 答案中每条声明是否都能追溯到检索上下文（防幻觉核心指标） |
| **Answer Relevancy** | Ragas | 答案是否切题，惩罚偏离主题的内容 |
| **Context Recall** | Ragas | 回答所需的信息是否都被检索系统找到 |
| **Answer Correctness** | Ragas | 事实重叠度 + 语义相似度的综合得分 |
| **Key Number Coverage** | Custom | Ground Truth 中关键财务数字（$、%）在答案中的出现比例 |
| **Success Rate** | Custom | 无错误完成的问题比例 |

详细逐题分析见 [`eval_results/eval_report.md`](eval_results/eval_report.md)

## 设计思路与技术亮点

1. **问题匿名化**：将命名实体替换为变量后再规划，强制 LLM 依赖检索结果而非预训练知识。灵感来源于 Controllable RAG 的核心思想。Faithfulness 达到 98% 验证了该策略的有效性。

2. **混合检索 Hybrid Search (Dense + BM25 + RRF)**：自研 `HybridRetriever` 类，将 FAISS 语义检索与 BM25 关键词检索结合，通过 Reciprocal Rank Fusion (RRF) 重排算法融合排序。解决纯向量检索对专有名词（iPhone 16 Pro Max）和精确数字（$391.0B）不敏感的问题。

3. **多粒度向量库**：针对财报场景设计三个不同粒度的向量库——正文切片捕获细节，章节摘要提供概览，财务指标句子提供精确数字。Task Handler 根据任务类型智能路由。

4. **三重 Grounding Check + Self-Correction**：
   - 借鉴 [Self-RAG](https://arxiv.org/abs/2310.11511) 论文思想，在检索精炼和答案生成两个阶段进行事实性验证
   - 新增 `number_audit` 数字审计节点（Self-Correction Prompting）：自动提取上下文中的 `$`/`%` 数字，检查最终答案的覆盖率，不足时强制重新生成

5. **动态重规划 + Graceful Degradation**：借鉴 [Plan-and-Solve Prompting](https://arxiv.org/abs/2305.04091) 思想，Agent 动态调整执行计划。双层兜底机制：外层 `MAX_REPLAN_RETRIES=5`（重规划上限）+ 内层 `MAX_GROUNDING_RETRIES=3`（Grounding Check 上限），避免死循环。

6. **DashScope 适配**：自定义 `DashScopeEmbeddings` 类（同步+异步），`robust_parse_plan` + `_repair_json` 处理 LLM 输出 JSON 格式不稳定问题。

## 已知局限与优化路线

### 已实现

| 优化方向 | 方案 | 效果 |
|----------|------|------|
| 纯向量检索召回不全 | Hybrid Search (BM25 + Dense + RRF) | 提升 Context Recall |
| 答案遗漏数字 | Self-Correction 数字审计节点 | 提升 Number Coverage |
| Agent 死循环 | 双层 Graceful Degradation | 成功率 100% |

### 未来迭代（Future Work）

| 方向 | 产品级方案 | 预期收益 |
|------|-----------|----------|
| **高级文档解析** | 引入 LlamaParse / Docling / 阿里文档解析 API，将 PDF 表格还原为结构化 Markdown，保持行列表头关联 | 根治因切片切断表格导致的数字丢失，Key Number Coverage → 90%+ |
| **计算器工具** | 在 Agent Graph 中新增 Calculator Tool (Python 代码执行器)，当识别到同比/环比/利润率差值计算时自动生成并执行代码 | 消除数学计算幻觉，提升 Answer Correctness → 85%+ |
| **语义缓存** | 引入 GPTCache 或 Redis 语义缓存，对相似问题（余弦相似度 > 0.95）命中缓存秒回 | 热点查询延迟从 100+s → 500ms，API 成本降低 80%+ |
| **延迟优化** | 1) Streaming 流式输出 + 实时状态透出；2) 模型分级路由（Planner 用 qwen-max，判断节点用 qwen-turbo）；3) 超复杂问题走异步报告模式 | 体感延迟降低 70%，实际延迟降低 50% |
| **评估扩展** | 增加至 50+ 测试用例，覆盖跨年对比、多公司对比场景；引入 LLM-as-Judge 人工对齐评估 | 评估可信度和覆盖面大幅提升 |

## 致谢

- 原始项目：[NirDiamant/Controllable-RAG-Agent](https://github.com/NirDiamant/Controllable-RAG-Agent)
- LLM：[通义千问 qwen-max](https://dashscope.aliyun.com/) by 阿里云
- Agent 框架：[LangGraph](https://github.com/langchain-ai/langgraph) by LangChain

## License

[Apache-2.0](LICENSE)
