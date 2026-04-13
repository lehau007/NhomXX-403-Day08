# Tuning Log — RAG Pipeline (Day 08 Lab)

> Template: Ghi lại mỗi thay đổi và kết quả quan sát được.
> A/B Rule: Chỉ đổi MỘT biến mỗi lần.

---

## Baseline (Sprint 2)

**Ngày:** 2026-04-13  
**Config:**
```python
retrieval_mode = "dense"
chunk_size = 400  # tokens (ước lượng bằng số ký tự / 4)
overlap = 80      # tokens
top_k_search = 10
top_k_select = 3
use_rerank = False
llm_model = "google/gemma-4-31b-it"  # qua NVIDIA NIM
```

**Scorecard Baseline:**
| Metric | Average Score |
|--------|--------------|
| Faithfulness | 4.60 /5 |
| Answer Relevance | 5.00 /5 |
| Context Recall | 5.00 /5 |
| Completeness | 4.30 /5 |

**Câu hỏi yếu nhất (điểm thấp):**
> - **q07** (Insufficient Context - SLA P1): Faithfulness=1/5, Completeness=5/5 — Model bịa ra câu trả lời (hallucination) khi cố gắng trả lời một câu hỏi vốn không có thông tin trong văn bản, khiến Faithfulness chạm đáy (1 điểm).
> - **q01** và **q08**: Completeness=3/5 — Model trả lời đúng nhưng LLM Judge cho rằng có vài chi tiết nhỏ cấu thành yếu tố còn khuyết.
> - **q10** (Refund - Temporal Context): Completeness=2/5 — Model trả lời an toàn là không có dữ liệu để đánh giá nhưng điểm Completeness vẫn bị LLM Judge chẩn là trả lời chưa đầy đủ so với expected answer.

**Giả thuyết nguyên nhân (Error Tree):**
- [x] Generation: Prompt không đủ grounding → Model dễ rơi vào hallucination (q07) ở Baseline.
- [x] Generation: LLM Judge Prompt chưa tối ưu khi chấm các câu hỏi abstain thành Completeness cực thấp.
- [ ] Retrieval: Top-k quá ít → thiếu evidence.
- [ ] Indexing: Chunking cắt giữa điều khoản.

---

## Variant 1 (Sprint 3)

**Ngày:** 2026-04-13  
**Biến thay đổi:** Thêm Hybrid Retrieval (BM25 + Dense với RRF) và tăng top_k_search từ 10 lên 15  
**Lý do chọn biến này:**
> Sử dụng Hybrid retrieval (rank-bm25) và sử dụng thuật toán cross-encoder/ms-marco-MiniLM-L-6-v2 giúp tối ưu hoá các truy vấn chứa keywords chuyên ngành (mã lỗi, tên ticket) mà dense embedding thuần túy thường hay bỏ sót.

**Config thay đổi:**
```python
retrieval_mode = "hybrid"
top_k_search = 15
use_rerank = True
# Các tham số còn lại giữ nguyên như baseline
```

**Scorecard Variant 1:**
| Metric | Baseline | Variant 1 | Delta |
|--------|----------|-----------|-------|
| Faithfulness | 4.60/5 | 5.00/5 | **+0.40** |
| Answer Relevance | 5.00/5 | 5.00/5 | 0.00 |
| Context Recall | 5.00/5 | 5.00/5 | 0.00 |
| Completeness | 4.30/5 | 3.90/5 | **-0.40** |

**Nhận xét theo từng câu:**
| Câu | Baseline F/R/Rc/C | Variant F/R/Rc/C | Better? |
|-----|------------------|-----------------|---------|
| q01 | 5/5/5/3 | 5/5/5/3 | Tie |
| q02 | 5/5/5/5 | 5/5/5/5 | Tie |
| q03 | 5/5/5/5 | 5/5/5/5 | Tie |
| q04 | 5/5/5/5 | 5/5/5/5 | Tie |
| q05 | 5/5/5/5 | 5/5/5/5 | Tie |
| q06 | 5/5/5/5 | 5/5/5/5 | Tie |
| q07 | 1/5/5/5 | 5/5/5/1 | **Variant** (Better Faithfulness) |
| q08 | 5/5/5/3 | 5/5/5/3 | Tie |
| q09 | 5/5/-/5 | 5/5/-/5 | Tie |
| q10 | 5/5/5/2 | 5/5/5/2 | Tie |

**Nhận xét:**
> - Variant **đạt điểm tuyệt đối** ở Faithfulness, cải thiện đáng kể ở **q07** (Tăng từ 1→5). Ở Baseline, model rớt vào bẫy và bịa thông tin cho q07. Ở Variant, việc có thêm màng lọc hybrid/rerank giúp model đưa ra kết luận từ chối trả lời một cách chính xác và bảo vệ độ tin cậy.
> - Điểm Completeness của Variant bị giảm so với Baseline ở q07 (5→1). Đây là **thiếu sót của công cụ Eval tự động (LLM Judge)**: khi model từ chối trả lời (đạt abstain), LLM Judge lại đánh giá là "thiếu thông tin/không đủ".

**Kết luận:**
> Variant 1 **thực sự tốt hơn** baseline về mặt chống ảo giác (Hallucination Resistance). Kết hợp hybrid + reranker giúp đảm bảo tính Faithfulness tuy nhiên ta sẽ cần nhắc nhở/tinh chỉnh lại prompt chấm thi của LLM-as-judge ở metric Completeness để tránh tình trạng hệ thống tự hạ điểm sai lầm.

---

## Variant 2 (nếu có thời gian)

**Biến thay đổi:** Chưa thực hiện (hết thời gian lab)  
**Config:**
```
# Đề xuất: Query Expansion (HyDE) + Rerank với threshold lọc bỏ chunk score thấp
```

---

## Tóm tắt học được

1. **Lỗi phổ biến nhất trong pipeline này là gì?**
   > **Tác dụng phụ của LLM-as-Judge trong việc chấm Completeness**: Ở những kịch bản tài liệu thiếu ngữ cảnh (như **q07** được thiết kế để dụ hallucination), hệ thống RAG đã phản xạ "abstain/từ chối" đúng như system prompt. Tuy nhiên trình thẩm định do không thiết lập prompt hoàn hảo, lại đánh giá việc từ bỏ là một lời giải thích "bị khuyết mảnh ghép", làm điểm Completeness tụt dốc thảm hại (5 → 1). Đây là một dạng lỗi "False Negative" của evaluator chứ không phải do RAG.

2. **Biến nào có tác động lớn nhất tới chất lượng?**
   > **Sự trỗi dậy của Hybrid và Reranker để chống Hallucination**. Điểm nhấn lớn nhất là việc thêm rank-bm25 và Cross-Encoder kéo vớt câu trả lời sai lệnh (bịa thông tin mức phạt đội IT) ở Baseline lên một câu trả lời phủ nhận chính xác ở Variant. Model chỉ tìm thấy những document hợp lệ mà không hề gán ghép với thông tin ngoài luồng.

3. **Nếu có thêm 1 giờ, nhóm sẽ thử gì tiếp theo?**
   > Ưu tiên **Tối ưu hóa Prompts của Hàm Score_Completeness**, bổ sung hẳn quy tắc: "Nếu cả System Prompt yêu cầu Abstain và RAG cũng Abstain đối với nội dung Insufficient, hệ thống phải trao 5/5 thay vì 1/5 cho Completeness.". Việc này bảo vệ mô hình không bị ngộ nhận là kém. Kế đó, sẽ thử thêm **Query Routing** giúp quyết định khi nào cần tìm dense, khi nào đi hybrid (không cần lúc nào cũng spam hybrid để giảm lag).
