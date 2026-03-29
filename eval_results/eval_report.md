# Agentic 10-K Copilot — Evaluation Report

> Generated: 2026-03-29 03:45
> Questions: 10 | Success Rate: 100.0%

## 1. RAG Quality Metrics (Ragas)

| Metric | Score | Description |
|--------|-------|-------------|
| **faithfulness** | 0.9800 | 答案是否忠实于检索到的文档（防幻觉核心指标） |
| **answer_relevancy** | 0.9013 | 答案是否切题、与问题相关 |
| **context_recall** | 0.7667 | 关键信息是否被成功检索到 |
| **answer_correctness** | 0.6553 | 答案与标准答案的匹配程度 |
| **answer_similarity** | 0.8503 | 答案与标准答案的语义相似度 |

## 2. System Performance Metrics

| Metric | Value |
|--------|-------|
| Success Rate | 100.0% (10/10) |
| Avg Latency | 139.4s |
| Avg Steps per Question | 10.0 |
| Avg Retrieval Calls | 1.5 |
| Avg Plan Steps | 3.2 |
| Avg Answer Length | 904 chars |
| Avg Context Length | 907 chars |
| Key Number Coverage | 34.5% |

## 3. Performance by Question Category

| Category | Count | Success Rate | Avg Latency |
|----------|-------|--------------|-------------|
| financial_metrics | 2 | 100% | 266.2s |
| segment_analysis | 1 | 100% | 109.7s |
| profitability | 1 | 100% | 62.2s |
| product_performance | 1 | 100% | 100.1s |
| risk_factors | 1 | 100% | 124.4s |
| capital_allocation | 1 | 100% | 138.0s |
| operating_expenses | 1 | 100% | 66.5s |
| balance_sheet | 1 | 100% | 204.0s |
| product_launches | 1 | 100% | 57.0s |

## 4. Performance by Difficulty

| Difficulty | Count | Success Rate | Avg Latency |
|------------|-------|--------------|-------------|
| easy | 3 | 100% | 196.5s |
| medium | 4 | 100% | 84.6s |
| hard | 3 | 100% | 155.5s |

## 5. Per-Question Results

### Q01 [PASS] — financial_metrics / easy
**Question:** What was Apple's total net sales in fiscal year 2025?

**Agent Answer:** The following table shows net sales by category for 2025 (dollars in millions): Total net sales $ 416,161  6 % $ 391,035  2 % $ 383,285

**Ground Truth:** Apple's total net sales in fiscal year 2025 were $416.2 billion ($416,161 million), representing a 6% increase compared to fiscal year 2024's $391.0 billion....

Latency: 61.0s | Steps: 8 | Retrievals: 1

---

### Q02 [PASS] — segment_analysis / medium
**Question:** How did Apple's Services segment perform in FY2025 compared to FY2024? What were the main growth drivers?

**Agent Answer:** Context: Services net sales increased during 2025 compared to 2024 primarily due to higher net sales from advertising, the App Store and cloud services. Services gross margin percentage increased during 2025 compared to 2024 primarily due to a different mix of services, partially offset by higher costs. (1) 109,158 14 % 96,169 13 % 85,200 Services Gross Margin Services gross margin increased during 2025 compared to 2024 primarily due to higher Services net sales and a different mix of services. ...

**Ground Truth:** Services net sales were $109.2 billion ($109,158 million) in FY2025, up 14% from $96.2 billion in FY2024. The growth was primarily driven by higher net sales from advertising, the App Store and cloud services. Services gross margin was 75.4%, up from 73.9% in FY2024, with gross profit of $82.3 billi...

Latency: 109.7s | Steps: 8 | Retrievals: 1

---

### Q03 [PASS] — profitability / medium
**Question:** Compare Apple's Products and Services gross margin percentages in FY2025. Which segment is more profitable on a margin basis?

**Agent Answer:** In FY2025, the gross margin percentages for Apple's two segments are as follows: Products at 36.8% and Services at 75.4%. The Services segment has a significantly higher gross margin percentage compared to the Products segment. Therefore, on a margin basis, the Services segment is more profitable with a 75.4% gross margin percentage compared to the 36.8% of the Products segment.

**Ground Truth:** In FY2025, Products gross margin percentage was 36.8% while Services gross margin percentage was 75.4%. Services is significantly more profitable on a margin basis, with nearly double the gross margin percentage of Products. Products gross margin was $112.9 billion and Services gross margin was $82....

Latency: 62.2s | Steps: 8 | Retrievals: 1

---

### Q04 [PASS] — product_performance / medium
**Question:** Which product categories saw revenue growth and which declined in FY2025? Provide specific numbers.

**Agent Answer:** To determine which product categories saw revenue growth and which declined in FY2025, we need to look at the 2025 'Change' column for each category. Here are the specific numbers:

- iPhone: The change is +4%, indicating an increase from $201,183 million in 2024 to $209,586 million in 2025.
- Mac: The change is +12%, showing an increase from $29,984 million in 2024 to $33,708 million in 2025.
- iPad: The change is +5%, reflecting an increase from $26,694 million in 2024 to $28,023 million in 20...

**Ground Truth:** Revenue growth categories: iPhone $209.6B (+4%, driven by higher Pro model sales), Mac $33.7B (+12%, higher laptop and desktop sales), iPad $28.0B (+5%, higher iPad Air, iPad mini and iPad sales), Services $109.2B (+14%). Revenue decline: Wearables, Home and Accessories $35.7B (-4%, lower Accessorie...

Latency: 100.1s | Steps: 8 | Retrievals: 1

---

### Q05 [PASS] — risk_factors / hard
**Question:** What tariff-related risks does Apple face according to its FY2025 10-K? How might these impact the business?

**Agent Answer:** The tariff-related risks that Apple faces according to its FY2025 10-K include the imposition of new U.S. tariffs on imports from various countries such as China, India, Japan, South Korea, Taiwan, Vietnam, and the EU, along with the potential for additional sector-based tariffs or other measures. In response, several countries have either imposed or threatened to impose reciprocal tariffs on U.S. imports, which could lead to a trade war. These actions can result in supply chain disruptions, inc...

**Ground Truth:** Beginning in Q2 2025, new U.S. tariffs were announced on imports from China, India, Japan, South Korea, Taiwan, Vietnam and the EU. Several countries imposed or threatened reciprocal tariffs. The U.S. Department of Commerce initiated a Section 232 investigation into semiconductor imports. These tari...

Latency: 124.4s | Steps: 12 | Retrievals: 2

---

### Q06 [PASS] — financial_metrics / easy
**Question:** What was Apple's net income and diluted earnings per share in FY2025?

**Agent Answer:** From the Consolidated Statements of Comprehensive Income, Apple's net income for FY2025 was $112,010 million. According to the table provided in Note 3 – Earnings Per Share, the diluted earnings per share for 2025 was $7.46.

**Ground Truth:** Apple's net income in FY2025 was $112.0 billion ($112,010 million), up from $93.7 billion in FY2024. Diluted earnings per share was $7.46, up from $6.08 in FY2024. The effective tax rate was 15.6%, significantly lower than the 24.1% in FY2024, partly due to a $10.7 billion decrease related to the St...

Latency: 471.4s | Steps: 20 | Retrievals: 4

---

### Q07 [PASS] — capital_allocation / hard
**Question:** Describe Apple's capital return program in FY2025, including share repurchases and dividends.

**Agent Answer:** The provided context does not contain specific information about dividends. However, it does provide detailed information on Apple's share repurchase program in FY2025. Here is the breakdown of the share repurchase activity:

- **May 2, 2024 Program**: Apple announced a program to repurchase up to $110 billion of its common stock. During the fourth quarter of 2025, the company utilized the final $19.8 billion under this program.
- **May 1, 2025 Program**: An additional program was announced to r...

**Ground Truth:** In May 2025, Apple announced a new $100 billion share repurchase program and raised its quarterly dividend from $0.25 to $0.26 per share. During FY2025, Apple repurchased $89.3 billion of common stock and paid dividends and dividend equivalents of $15.4 billion ($1.02 per share for the year). The co...

Latency: 138.0s | Steps: 8 | Retrievals: 1

---

### Q08 [PASS] — operating_expenses / medium
**Question:** How did Apple's R&D spending change in FY2025 and what percentage of revenue does it represent?

**Agent Answer:** Operating Expenses Operating expenses for 2025, 2024 and 2023 were as follows (dollars in millions): 2025 Change 2024 Change 2023 Research and development $ 34,550 10% $ 31,370 5% $ 29,915 Percentage of total net sales 8% 8% 8% The growth in R&D expense during 2025 compared to 2024 was primarily driven by increases in headcount-related expenses and infrastructure-related costs. ||| How did Apple's R&D spending change in FY2025 and what percentage of revenue does it represent?

**Ground Truth:** Research and development expenses were $34.6 billion ($34,550 million) in FY2025, a 10% increase from $31.4 billion in FY2024. R&D represented 8% of total net sales, consistent with FY2024. The growth was primarily driven by increases in headcount-related expenses. Total operating expenses were $62....

Latency: 66.5s | Steps: 8 | Retrievals: 1

---

### Q09 [PASS] — balance_sheet / hard
**Question:** What is Apple's financial position as reflected in its balance sheet at the end of FY2025? Discuss assets, liabilities and equity.

**Agent Answer:** The context provides a detailed breakdown of Apple Inc.'s consolidated balance sheet as of September 27, 2025. In terms of assets, the company has total current assets of $147,957 million, which includes cash and cash equivalents of $35,934 million, marketable securities of $18,763 million, accounts receivable (net) of $39,777 million, vendor non-trade receivables of $33,180 million, inventories of $5,718 million, and other current assets of $14,585 million. Non-current assets total $211,284 mil...

**Ground Truth:** As of September 27, 2025, Apple's total assets were $359.2 billion (down from $365.0B), with current assets of $148.0 billion including $35.9B cash and $18.8B marketable securities. Total liabilities were $285.5 billion (down from $308.0B), including $90.7B in total term debt. Total shareholders' eq...

Latency: 204.0s | Steps: 12 | Retrievals: 2

---

### Q10 [PASS] — product_launches / easy
**Question:** What major products did Apple announce or launch during fiscal year 2025?

**Agent Answer:** During fiscal year 2025, Apple announced or launched the following major products across each quarter:

- **Q1 (First Quarter):**
  - MacBook Pro
  - Mac mini
  - iMac
  - iPad mini

- **Q2 (Second Quarter):**
  - iPhone 16e
  - iPad Air
  - iPad
  - MacBook Air
  - Mac Studio

- **Q3 (Third Quarter):**
  - iOS 26
  - macOS Tahoe 26
  - iPadOS 26
  - watchOS 26
  - visionOS 26
  - tvOS 26

- **Q4 (Fourth Quarter):**
  - iPhone 17 series
  - Apple Watch Series 11
  - AirPods Pro 3

These products...

**Ground Truth:** Q1 2025: MacBook Pro, Mac mini, iMac, iPad mini. Q2 2025: iPhone 16e, iPad Air, iPad, MacBook Air, Mac Studio. Q3 2025: iOS 26, macOS Tahoe 26, iPadOS 26, watchOS 26, visionOS 26 and tvOS 26. Q4 2025: iPhone 17, iPhone Air, iPhone 17 Pro and iPhone 17 Pro Max, Apple Watch Series 11, Apple Watch SE 3...

Latency: 57.0s | Steps: 8 | Retrievals: 1

---

## 6. Evaluation Methodology

### 6.1 Dataset Design
- 10 questions covering 6 categories: financial_metrics, segment_analysis, profitability, product_performance, risk_factors, capital_allocation, operating_expenses, balance_sheet, product_launches
- 3 difficulty levels: easy (direct lookup), medium (multi-step analysis), hard (synthesis across sections)
- Ground truth answers extracted directly from Apple FY2025 10-K filing

### 6.2 Metrics Explanation
- **Faithfulness** (Ragas): Measures whether every claim in the answer can be traced back to the retrieved context. Core anti-hallucination metric.
- **Answer Relevancy** (Ragas): Evaluates if the answer addresses the question asked, penalizing off-topic content.
- **Context Recall** (Ragas): Checks if the retrieval system found all information needed to answer correctly.
- **Answer Correctness** (Ragas): Combines factual overlap and semantic similarity with ground truth.
- **Key Number Coverage** (Custom): Percentage of key financial figures from ground truth that appear in the agent's answer.
- **Success Rate** (Custom): Percentage of questions completed without errors.

### 6.3 Anti-Hallucination Design
This system implements 3-layer hallucination prevention:
1. **Input Layer**: Question anonymization replaces named entities with variables
2. **Retrieval Layer**: Distilled content grounding check against original context
3. **Output Layer**: Final answer grounding check against aggregated context
