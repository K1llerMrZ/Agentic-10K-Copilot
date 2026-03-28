# Agentic 10-K Copilot — Evaluation Report

> Generated: 2026-03-28 21:40
> Questions: 10 | Success Rate: 90.0%

## 1. RAG Quality Metrics (Ragas)

Ragas evaluation encountered an error: `Skipped by user (--skip-ragas)`

Custom fallback metrics are provided below.

## 2. System Performance Metrics

| Metric | Value |
|--------|-------|
| Success Rate | 90.0% (9/10) |
| Avg Latency | 112.2s |
| Avg Steps per Question | 10.7 |
| Avg Retrieval Calls | 1.7 |
| Avg Plan Steps | 3.6 |
| Avg Answer Length | 1118 chars |
| Avg Context Length | 1098 chars |
| Key Number Coverage | 45.7% |

## 3. Performance by Question Category

| Category | Count | Success Rate | Avg Latency |
|----------|-------|--------------|-------------|
| financial_metrics | 2 | 100% | 91.7s |
| segment_analysis | 1 | 100% | 169.3s |
| profitability | 1 | 100% | 67.0s |
| product_performance | 1 | 100% | 114.1s |
| risk_factors | 1 | 100% | 117.1s |
| capital_allocation | 1 | 0% | 0s |
| operating_expenses | 1 | 100% | 61.7s |
| balance_sheet | 1 | 100% | 233.8s |
| product_launches | 1 | 100% | 63.1s |

## 4. Performance by Difficulty

| Difficulty | Count | Success Rate | Avg Latency |
|------------|-------|--------------|-------------|
| easy | 3 | 100% | 82.1s |
| medium | 4 | 100% | 103.0s |
| hard | 3 | 67% | 175.4s |

## 5. Per-Question Results

### Q01 [PASS] — financial_metrics / easy
**Question:** What was Apple's total net sales in fiscal year 2025?

**Agent Answer:** Based on the provided context, Apple's total net sales in fiscal year 2025 increased by 6% to $416,161 million.

**Ground Truth:** Apple's total net sales in fiscal year 2025 were $416.2 billion ($416,161 million), representing a 6% increase compared to fiscal year 2024's $391.0 billion....

Latency: 121.3s | Steps: 12 | Retrievals: 2

---

### Q02 [PASS] — segment_analysis / medium
**Question:** How did Apple's Services segment perform in FY2025 compared to FY2024? What were the main growth drivers?

**Agent Answer:** The Services segment of Apple performed better in FY2025 compared to FY2024. The main growth drivers for the Services segment were higher net sales from advertising, the App Store, and cloud services. In terms of financials, the net sales for the Services segment increased from $96,169 million in FY2024 to $109,158 million in FY2025, which is a 14% increase. Additionally, the gross margin for the Services segment also saw an improvement, going from $71,050 million (73.9% of net sales) in FY2024 ...

**Ground Truth:** Services net sales were $109.2 billion ($109,158 million) in FY2025, up 14% from $96.2 billion in FY2024. The growth was primarily driven by higher net sales from advertising, the App Store and cloud services. Services gross margin was 75.4%, up from 73.9% in FY2024, with gross profit of $82.3 billi...

Latency: 169.3s | Steps: 12 | Retrievals: 2

---

### Q03 [PASS] — profitability / medium
**Question:** Compare Apple's Products and Services gross margin percentages in FY2025. Which segment is more profitable on a margin basis?

**Agent Answer:** To compare Apple's Products and Services gross margin percentages in FY2025, we need to look at the given gross margin percentages for each segment. The Products segment has a gross margin of 36.8%, while the Services segment has a gross margin of 75.4%. Gross margin percentage is a measure of profitability, as it represents the portion of revenue that remains after subtracting the cost of goods sold (COGS). A higher gross margin percentage indicates that a larger fraction of the revenue is left...

**Ground Truth:** In FY2025, Products gross margin percentage was 36.8% while Services gross margin percentage was 75.4%. Services is significantly more profitable on a margin basis, with nearly double the gross margin percentage of Products. Products gross margin was $112.9 billion and Services gross margin was $82....

Latency: 67.0s | Steps: 8 | Retrievals: 1

---

### Q04 [PASS] — product_performance / medium
**Question:** Which product categories saw revenue growth and which declined in FY2025? Provide specific numbers.

**Agent Answer:** To answer the question, we need to analyze the '2025 Change' column for each product category. The positive or negative percentage in this column indicates whether the net sales increased or decreased compared to the previous year (FY2024). Let's break it down by each category:

1. iPhone: The 2025 Change is +4%, indicating an increase in revenue.
   - 2025 Net Sales: $209,586 million
   - 2024 Net Sales: $201,183 million
   - Increase: $209,586 million - $201,183 million = $8,403 million

2. Ma...

**Ground Truth:** Revenue growth categories: iPhone $209.6B (+4%, driven by higher Pro model sales), Mac $33.7B (+12%, higher laptop and desktop sales), iPad $28.0B (+5%, higher iPad Air, iPad mini and iPad sales), Services $109.2B (+14%). Revenue decline: Wearables, Home and Accessories $35.7B (-4%, lower Accessorie...

Latency: 114.1s | Steps: 8 | Retrievals: 1

---

### Q05 [PASS] — risk_factors / hard
**Question:** What tariff-related risks does Apple face according to its FY2025 10-K? How might these impact the business?

**Agent Answer:** The tariff-related risks that Apple faces according to its FY2025 10-K include the following, as derived from the provided context:

- **Tariffs and Trade Disputes**: The imposition of new tariffs on imports to the U.S. (U.S. Tariffs) can increase costs for Apple, which may be passed on to consumers or absorbed by the company, thereby affecting profit margins.
- **Geopolitical Tensions**: An escalation of geopolitical tensions could lead to significant disruptions in global supply chains, which ...

**Ground Truth:** Beginning in Q2 2025, new U.S. tariffs were announced on imports from China, India, Japan, South Korea, Taiwan, Vietnam and the EU. Several countries imposed or threatened reciprocal tariffs. The U.S. Department of Commerce initiated a Section 232 investigation into semiconductor imports. These tari...

Latency: 117.1s | Steps: 12 | Retrievals: 2

---

### Q06 [PASS] — financial_metrics / easy
**Question:** What was Apple's net income and diluted earnings per share in FY2025?

**Agent Answer:** From the provided context, Apple's net income for FY2025 was $112,010 million. The diluted earnings per share (EPS) for the same period was $7.46.

**Ground Truth:** Apple's net income in FY2025 was $112.0 billion ($112,010 million), up from $93.7 billion in FY2024. Diluted earnings per share was $7.46, up from $6.08 in FY2024. The effective tax rate was 15.6%, significantly lower than the 24.1% in FY2024, partly due to a $10.7 billion decrease related to the St...

Latency: 62.0s | Steps: 8 | Retrievals: 1

---

### Q07 [FAIL] — capital_allocation / hard
**Question:** Describe Apple's capital return program in FY2025, including share repurchases and dividends.

**Error:** Recursion limit of 40 reachedwithout hitting a stop condition. You can increase the limit by setting the `recursion_limit` config key.

---

### Q08 [PASS] — operating_expenses / medium
**Question:** How did Apple's R&D spending change in FY2025 and what percentage of revenue does it represent?

**Agent Answer:** To answer the question about how Apple's R&D spending changed in FY2025 and what percentage of revenue it represents, we need to analyze the provided context. The context gives us the following information:

- R&D expenses for 2025 were $34,550 million.
- R&D expenses for 2024 were $31,370 million.
- The percentage of total net sales for R&D was 8% for both 2025 and 2024.

Let's break down the analysis into a chain of thought:
1. Calculate the change in R&D spending from 2024 to 2025.
2. Determi...

**Ground Truth:** Research and development expenses were $34.6 billion ($34,550 million) in FY2025, a 10% increase from $31.4 billion in FY2024. R&D represented 8% of total net sales, consistent with FY2024. The growth was primarily driven by increases in headcount-related expenses. Total operating expenses were $62....

Latency: 61.7s | Steps: 8 | Retrievals: 1

---

### Q09 [PASS] — balance_sheet / hard
**Question:** What is Apple's financial position as reflected in its balance sheet at the end of FY2025? Discuss assets, liabilities and equity.

**Agent Answer:** The balance sheet as of September 27, 2025, shows the following for Apple's financial position:

**Assets:**
- **Right-of-use (ROU) assets:** Total ROU assets amount to $12,238 million, which are split into operating leases classified as other non-current assets ($11,205 million) and finance leases included in property, plant and equipment, net ($1,033 million).
- **Property, plant and equipment (PPE):** Gross PPE is $125,848 million, with accumulated depreciation of $(76,014) million, resulting...

**Ground Truth:** As of September 27, 2025, Apple's total assets were $359.2 billion (down from $365.0B), with current assets of $148.0 billion including $35.9B cash and $18.8B marketable securities. Total liabilities were $285.5 billion (down from $308.0B), including $90.7B in total term debt. Total shareholders' eq...

Latency: 233.8s | Steps: 20 | Retrievals: 4

---

### Q10 [PASS] — product_launches / easy
**Question:** What major products did Apple announce or launch during fiscal year 2025?

**Agent Answer:** To answer the question about the major products Apple announced or launched during fiscal year 2025, we can break down the information provided in the context by each quarter (Q1, Q2, Q3, and Q4) and list the products mentioned for each. Here's the chain of thought:

- In Q1, Apple released the following hardware products: MacBook Pro, Mac mini, iMac, and iPad mini.
- In Q2, the company introduced a new iPhone model, the iPhone 16e, as well as updated versions of the iPad Air, iPad, MacBook Air,...

**Ground Truth:** Q1 2025: MacBook Pro, Mac mini, iMac, iPad mini. Q2 2025: iPhone 16e, iPad Air, iPad, MacBook Air, Mac Studio. Q3 2025: iOS 26, macOS Tahoe 26, iPadOS 26, watchOS 26, visionOS 26 and tvOS 26. Q4 2025: iPhone 17, iPhone Air, iPhone 17 Pro and iPhone 17 Pro Max, Apple Watch Series 11, Apple Watch SE 3...

Latency: 63.1s | Steps: 8 | Retrievals: 1

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
