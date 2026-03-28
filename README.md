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
[任务路由] ──┬── Tool A: 正文切片检索（具体细节、条款、段落）
             ├── Tool B: 章节摘要检索（业务概览、风险因素、MD&A）
             ├── Tool C: 财务指标检索（收入、利润率、增长率等数字）
             └── Tool D: 基于已有上下文直接回答
  │
  ▼
[重新规划] 根据已收集信息更新剩余计划
  │
  ├─ 信息充足 → [生成最终答案] → 输出
  └─ 信息不足 → 回到 [细化计划] 继续检索
```

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
| 向量数据库 | FAISS | Facebook 开源的近似最近邻搜索 |
| LLM 编排 | LangChain 0.1.20 | Prompt + Chain + Output Parser |
| 前端 | Streamlit 1.32 + PyVis | 实时 Agent 流程可视化 |
| 评估 | Ragas 0.1.7 | 自动化 RAG 质量评估 |

## 快速开始

### 环境要求

- Python 3.10+
- 阿里云 DashScope API Key（[获取地址](https://dashscope.console.aliyun.com/)）

### 安装

```bash
git clone https://github.com/YOUR_USERNAME/Agentic-10K-Copilot.git
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
├── chunks_vector_store/               # FAISS 向量库：正文切片
├── chapter_summaries_vector_store/    # FAISS 向量库：章节摘要
└── book_quotes_vectorstore/           # FAISS 向量库：财务指标句子
```

## 评估指标

使用 Ragas 框架进行自动化评估：

| 指标 | 含义 |
|------|------|
| **Faithfulness** | 答案是否忠实于检索到的文档（防幻觉核心指标） |
| **Answer Relevancy** | 答案是否切题 |
| **Context Precision** | 检索的文档中相关的比例 |
| **Context Recall** | 回答所需的信息是否都被检索到了 |
| **Answer Correctness** | 答案与标准答案的匹配程度 |

## 设计思路与技术亮点

1. **问题匿名化**：将命名实体替换为变量后再规划，强制 LLM 依赖检索结果而非预训练知识。灵感来源于 Controllable RAG 的核心思想。

2. **多粒度向量库**：针对财报场景设计三个不同粒度的向量库——正文切片捕获细节，章节摘要提供概览，财务指标句子提供精确数字。Task Handler 根据任务类型智能路由。

3. **双重 Grounding Check**：借鉴 [Self-RAG](https://arxiv.org/abs/2310.11511) 论文思想，在检索精炼和答案生成两个阶段都进行事实性验证，确保输出严格基于原始文档。

4. **动态重规划**：借鉴 [Plan-and-Solve Prompting](https://arxiv.org/abs/2305.04091) 思想，Agent 在每次检索/回答后评估已有信息是否充足，不足则更新计划继续执行。

5. **DashScope 适配**：自定义 `DashScopeEmbeddings` 类解决 API 兼容性问题，`robust_parse_plan` 函数处理 LLM 输出的 JSON 格式不稳定问题。

## 致谢

- 原始项目：[NirDiamant/Controllable-RAG-Agent](https://github.com/NirDiamant/Controllable-RAG-Agent)
- LLM：[通义千问 qwen-max](https://dashscope.aliyun.com/) by 阿里云
- Agent 框架：[LangGraph](https://github.com/langchain-ai/langgraph) by LangChain

## License

[Apache-2.0](LICENSE)
