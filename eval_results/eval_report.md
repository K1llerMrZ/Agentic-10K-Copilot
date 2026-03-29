# Agentic 10-K Copilot — Evaluation Report

> Generated: 2026-03-29 07:22
> Questions: 10 | Success Rate: 100.0%

## 1. RAG Quality Metrics (Ragas)

| Metric | Score | Description |
|--------|-------|-------------|
| **faithfulness** | 0.8635 | 答案是否忠实于检索到的文档（防幻觉核心指标） |
| **answer_relevancy** | 0.9244 | 答案是否切题、与问题相关 |
| **context_recall** | 0.7517 | 关键信息是否被成功检索到 |
| **answer_correctness** | 0.6314 | 答案与标准答案的匹配程度 |
| **answer_similarity** | 0.8551 | 答案与标准答案的语义相似度 |

## 2. System Performance Metrics

| Metric | Value |
|--------|-------|
| Success Rate | 100.0% (10/10) |
| Avg Latency | 119.9s |
| Avg Steps per Question | 9.8 |
| Avg Retrieval Calls | 1.2 |
| Avg Plan Steps | 3.4 |
| Avg Answer Length | 848 chars |
| Avg Context Length | 838 chars |
| Key Number Coverage | 34.4% |

## 3. Performance by Question Category

| Category | Count | Success Rate | Avg Latency |
|----------|-------|--------------|-------------|
| financial_metrics | 2 | 100% | 108.9s |
| segment_analysis | 1 | 100% | 161.3s |
| profitability | 1 | 100% | 87.3s |
| product_performance | 1 | 100% | 142.5s |
| risk_factors | 1 | 100% | 109.3s |
| capital_allocation | 1 | 100% | 121.1s |
| operating_expenses | 1 | 100% | 104.3s |
| balance_sheet | 1 | 100% | 172.8s |
| product_launches | 1 | 100% | 83.0s |

## 4. Performance by Difficulty

| Difficulty | Count | Success Rate | Avg Latency |
|------------|-------|--------------|-------------|
| easy | 3 | 100% | 100.3s |
| medium | 4 | 100% | 123.9s |
| hard | 3 | 100% | 134.4s |

## 5. Per-Question Results

### Q01 [PASS] — financial_metrics / easy
**Question:** What was Apple's total net sales in fiscal year 2025?

**Agent Answer:** The total net sales for Apple in fiscal year 2025, as provided in the context, was $416,161 million. The context includes a variety of growth percentages for different segments and regions over the years 2025, 2024, and 2023. These include Mac's 12% increase, Services' 14% growth, Europe's 10% rise, and Japan's 15% increase in 2025. Additionally, there are smaller increases such as the 5% for iPad, and slighter changes like the 2% and 3% for Mac and Americas, respectively. There is also a mentio...

**Ground Truth:** Apple's total net sales in fiscal year 2025 were $416.2 billion ($416,161 million), representing a 6% increase compared to fiscal year 2024's $391.0 billion....

Latency: 135.3s | Steps: 9 | Retrievals: 1

---

### Q02 [PASS] — segment_analysis / medium
**Question:** How did Apple's Services segment perform in FY2025 compared to FY2024? What were the main growth drivers?

**Agent Answer:** Apple's Services segment performed well in FY2025 compared to FY2024, with a 14% increase in net sales. In FY2024, the Services segment had already shown a 13% growth over FY2023. The main growth drivers for the 14% increase in FY2025 were higher net sales from advertising, the App Store, and cloud services. This strong performance of the Services segment contributed to the overall total net sales growth, which was 6% in FY2025, an improvement from the 2% growth seen in FY2024.

**Ground Truth:** Services net sales were $109.2 billion ($109,158 million) in FY2025, up 14% from $96.2 billion in FY2024. The growth was primarily driven by higher net sales from advertising, the App Store and cloud services. Services gross margin was 75.4%, up from 73.9% in FY2024, with gross profit of $82.3 billi...

Latency: 161.3s | Steps: 13 | Retrievals: 2

---

### Q03 [PASS] — profitability / medium
**Question:** Compare Apple's Products and Services gross margin percentages in FY2025. Which segment is more profitable on a margin basis?

**Agent Answer:** To compare Apple's Products and Services gross margin percentages in FY2025, we need to look at the provided figures. The context states that for 2025, the gross margin percentage for Products was 36.8% and for Services it was 75.4%.

Step 1: Identify the gross margin percentages for each segment.
- Products gross margin percentage: 36.8%
- Services gross margin percentage: 75.4%

Step 2: Compare the two percentages.
- 75.4% (Services) is greater than 36.8% (Products).

Step 3: Determine which s...

**Ground Truth:** In FY2025, Products gross margin percentage was 36.8% while Services gross margin percentage was 75.4%. Services is significantly more profitable on a margin basis, with nearly double the gross margin percentage of Products. Products gross margin was $112.9 billion and Services gross margin was $82....

Latency: 87.3s | Steps: 9 | Retrievals: 1

---

### Q04 [PASS] — product_performance / medium
**Question:** Which product categories saw revenue growth and which declined in FY2025? Provide specific numbers.

**Agent Answer:** To determine which product categories saw revenue growth and which declined in FY2025, we can examine the 'Change' percentages provided for 2025. The specific numbers given for each category's change are as follows:

- iPhone: 4 % increase
- Mac: 12 % increase
- iPad: 5 % increase
- Wearables, Home and Accessories: (4) % decrease
- Services: 14 % increase

The positive percentages indicate growth, while the negative percentage indicates a decline. Therefore, the product categories that saw reven...

**Ground Truth:** Revenue growth categories: iPhone $209.6B (+4%, driven by higher Pro model sales), Mac $33.7B (+12%, higher laptop and desktop sales), iPad $28.0B (+5%, higher iPad Air, iPad mini and iPad sales), Services $109.2B (+14%). Revenue decline: Wearables, Home and Accessories $35.7B (-4%, lower Accessorie...

Latency: 142.5s | Steps: 9 | Retrievals: 1

---

### Q05 [PASS] — risk_factors / hard
**Question:** What tariff-related risks does Apple face according to its FY2025 10-K? How might these impact the business?

**Agent Answer:** Tariffs and other measures that are applied to the Company's products or their components can have a material adverse impact on the Company's business, results of operations and financial condition, including impacting the Company's supply chain, the availability of rare earths and other raw materials and components, pricing and gross margin. The ultimate impact remains uncertain and will depend on several factors, including whether additional or incremental U.S. Tariffs or other measures are an...

**Ground Truth:** Beginning in Q2 2025, new U.S. tariffs were announced on imports from China, India, Japan, South Korea, Taiwan, Vietnam and the EU. Several countries imposed or threatened reciprocal tariffs. The U.S. Department of Commerce initiated a Section 232 investigation into semiconductor imports. These tari...

Latency: 109.3s | Steps: 9 | Retrievals: 1

---

### Q06 [PASS] — financial_metrics / easy
**Question:** What was Apple's net income and diluted earnings per share in FY2025?

**Agent Answer:** The context provides the following financial data for 2025:
- Net income: $112,010 million
- Diluted earnings per share: $7.46
Therefore, Apple's net income in FY2025 was $112,010 million and the diluted earnings per share were $7.46.

**Ground Truth:** Apple's net income in FY2025 was $112.0 billion ($112,010 million), up from $93.7 billion in FY2024. Diluted earnings per share was $7.46, up from $6.08 in FY2024. The effective tax rate was 15.6%, significantly lower than the 24.1% in FY2024, partly due to a $10.7 billion decrease related to the St...

Latency: 82.5s | Steps: 9 | Retrievals: 1

---

### Q07 [PASS] — capital_allocation / hard
**Question:** Describe Apple's capital return program in FY2025, including share repurchases and dividends.

**Agent Answer:** In FY2025, Apple's capital return program included both share repurchases and dividends. For the share repurchase, there were two programs in place:

1. The May 2, 2024 Program allowed for the repurchase of up to $110 billion of common stock. By the end of the fourth quarter of 2025, the remaining amount utilized under this program was $19.8 billion.

2. The May 1, 2025 Program was an additional initiative to repurchase up to $100 billion of the company's common stock. As of September 27, 2025, ...

**Ground Truth:** In May 2025, Apple announced a new $100 billion share repurchase program and raised its quarterly dividend from $0.25 to $0.26 per share. During FY2025, Apple repurchased $89.3 billion of common stock and paid dividends and dividend equivalents of $15.4 billion ($1.02 per share for the year). The co...

Latency: 121.1s | Steps: 9 | Retrievals: 1

---

### Q08 [PASS] — operating_expenses / medium
**Question:** How did Apple's R&D spending change in FY2025 and what percentage of revenue does it represent?

**Agent Answer:** To answer the question, let's break down the information provided in the context and analyze it step-by-step.

1. R&D spending for 2025 was $34,550 million.
2. The change from 2024 to 2025 is indicated as a 10% increase.
3. R&D spending for 2024 was $31,370 million.
4. The change from 2023 to 2024 is indicated as a 5% increase.
5. R&D spending for 2023 was $29,915 million.
6. The percentage of total net sales that R&D represents is 8% for all three years, 2025, 2024, and 2023.

Now, we can summa...

**Ground Truth:** Research and development expenses were $34.6 billion ($34,550 million) in FY2025, a 10% increase from $31.4 billion in FY2024. R&D represented 8% of total net sales, consistent with FY2024. The growth was primarily driven by increases in headcount-related expenses. Total operating expenses were $62....

Latency: 104.3s | Steps: 9 | Retrievals: 1

---

### Q09 [PASS] — balance_sheet / hard
**Question:** What is Apple's financial position as reflected in its balance sheet at the end of FY2025? Discuss assets, liabilities and equity.

**Agent Answer:** Based on the provided balance sheet for Apple Inc. as of September 27, 2025, we can analyze the company's financial position in terms of its assets, liabilities, and shareholders' equity.

Assets:
- Total current assets are $147,957 million, which includes:
  - Cash and cash equivalents of $35,934 million
  - Marketable securities of $18,763 million
  - Accounts receivable, net of $39,777 million
  - Vendor non-trade receivables of $33,180 million
  - Inventories of $5,718 million
  - Other curr...

**Ground Truth:** As of September 27, 2025, Apple's total assets were $359.2 billion (down from $365.0B), with current assets of $148.0 billion including $35.9B cash and $18.8B marketable securities. Total liabilities were $285.5 billion (down from $308.0B), including $90.7B in total term debt. Total shareholders' eq...

Latency: 172.8s | Steps: 13 | Retrievals: 2

---

### Q10 [PASS] — product_launches / easy
**Question:** What major products did Apple announce or launch during fiscal year 2025?

**Agent Answer:** During fiscal year 2025, Apple announced or launched the following major products:

First Quarter 2025:
- MacBook Pro
- Mac mini
- iMac
- iPad mini

Second Quarter 2025:
- iPhone 16e
- iPad Air
- iPad
- MacBook Air
- Mac Studio

Third Quarter 2025:
- iOS 26, macOS Tahoe 26, iPadOS 26, watchOS 26, visionOS 26 and tvOS 26 (These are software updates, not physical products)

Fourth Quarter 2025:
- iPhone 17, iPhone Air, iPhone 17 Pro, and iPhone 17 Pro Max
- Apple Watch Series 11, Apple Watch SE 3,...

**Ground Truth:** Q1 2025: MacBook Pro, Mac mini, iMac, iPad mini. Q2 2025: iPhone 16e, iPad Air, iPad, MacBook Air, Mac Studio. Q3 2025: iOS 26, macOS Tahoe 26, iPadOS 26, watchOS 26, visionOS 26 and tvOS 26. Q4 2025: iPhone 17, iPhone Air, iPhone 17 Pro and iPhone 17 Pro Max, Apple Watch Series 11, Apple Watch SE 3...

Latency: 83.0s | Steps: 9 | Retrievals: 1

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
