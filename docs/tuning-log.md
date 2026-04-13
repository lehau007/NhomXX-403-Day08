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
llm_model = "meta/llama-3.1-405b-instruct"  # qua NVIDIA NIM
```

**Scorecard Baseline:**
| Metric | Average Score |
|--------|--------------|
| Faithfulness | 4.80 /5 |
| Answer Relevance | 3.80 /5 |
| Context Recall | 5.00 /5 |
| Completeness | 3.50 /5 |

**Câu hỏi yếu nhất (điểm thấp):**
> - **q07** (Access Control — Approval Matrix): Faithfulness=3/5, Completeness=3/5 — Dense embedding trả về chunk có đề cập `access-control-sop.md` nhưng LLM trích dẫn sai tên mục. Context recall đạt 5 nhưng faithfulness thấp do answer bám vào section header không chính xác.
> - **q09** (Insufficient Context — ERR-403-AUTH): Relevance=1/5, Completeness=2/5 — Không có tài liệu nào trong corpus chứa thông tin về lỗi ERR-403-AUTH. RAG đúng khi trả lời "không biết" (Faithfulness=5) nhưng hoàn toàn vô dụng với người dùng.
> - **q10** (Refund VIP — Insufficient Context): Relevance=1/5, Completeness=1/5 — Corpus không có quy trình hoàn tiền đặc biệt cho VIP. Kết quả tương tự q09.

**Giả thuyết nguyên nhân (Error Tree):**
- [x] Retrieval: Dense bỏ lỡ exact keyword / alias → q07 bỏ lỡ tên chính xác "Approval Matrix"
- [x] Retrieval: Top-k quá ít → thiếu evidence (q06 thiếu chi tiết escalation đầy đủ)
- [x] Generation: Prompt không đủ grounding → q07 LLM viết sai section name dù context đúng
- [ ] Indexing: Chunking cắt giữa điều khoản
- [ ] Indexing: Metadata thiếu effective_date
- [ ] Generation: Context quá dài → lost in the middle

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
use_rerank = True  # cross-encoder/ms-marco-MiniLM-L-6-v2
# Các tham số còn lại giữ nguyên như baseline
```

**Scorecard Variant 1:**
| Metric | Baseline | Variant 1 | Delta |
|--------|----------|-----------|-------|
| Faithfulness | 4.80/5 | 4.90/5 | +0.10 |
| Answer Relevance | 3.80/5 | 3.60/5 | -0.20 |
| Context Recall | 5.00/5 | 5.00/5 | +0.00 |
| Completeness | 3.50/5 | 3.30/5 | -0.20 |

**Nhận xét theo từng câu:**
| Câu | Baseline F/R/Rc/C | Variant F/R/Rc/C | Better? |
|-----|------------------|-----------------|---------|
| q01 | 5/4/5/3 | 5/4/5/3 | Tie |
| q02 | 5/5/5/5 | 5/5/5/5 | Tie |
| q03 | 5/4/5/5 | 5/5/5/5 | **Variant** |
| q04 | 5/5/5/3 | 5/5/5/3 | Tie |
| q05 | 5/5/5/5 | 5/5/5/5 | Tie |
| q06 | 5/3/5/5 | 4/3/5/5 | **Baseline** |
| q07 | 3/5/5/3 | 5/2/5/1 | **Baseline** |
| q08 | 5/5/5/3 | 5/5/5/3 | Tie |
| q09 | 5/1/-/2 | 5/1/-/2 | Tie |
| q10 | 5/1/5/1 | 5/1/5/1 | Tie |

**Nhận xét:**
> - Variant cải thiện ở **q03** (Access Control — cấp quyền Level 3): Relevance tăng từ 4→5, câu trả lời đầy đủ hơn nhờ hybrid tìm thêm được context liên quan.
> - Variant **kém hơn** ở **q06** (Escalation P1): Faithfulness giảm từ 5→4, hybrid đưa vào chunks dư thừa từ access-control-sop khiến LLM trả lời dài hơn nhưng kém chính xác.
> - Variant **kém hơn nghiêm trọng** ở **q07** (Approval Matrix): Relevance giảm 5→2, Completeness giảm 3→1. Hybrid kéo về nhiều chunks không liên quan, khiến LLM không tìm được Approval Matrix và từ chối trả lời. Đây là regression bất ngờ.
> - q09 và q10 vẫn fail như baseline vì corpus không có thông tin — đây là hạn chế của dữ liệu, không phải retrieval.

**Kết luận:**
> Variant 1 **không tốt hơn** baseline theo tổng điểm. Faithfulness tăng nhẹ (+0.10) nhưng Relevance và Completeness đều giảm (-0.20 mỗi metric). Nguyên nhân chính: hybrid search đưa vào quá nhiều chunks nhiễu (noise) từ các tài liệu không liên quan, đặc biệt với q07, làm giảm khả năng LLM tập trung trả lời. **Baseline Dense vẫn là config tốt hơn** cho tập dữ liệu này (tổng weighted score: Baseline ≈ 17.10/20 vs Variant ≈ 16.80/20).

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
   > **Corpus gap** (thiếu tài liệu): q09 và q10 fail hoàn toàn vì corpus không chứa thông tin được hỏi. Không có thuật toán retrieval nào cứu được nếu dữ liệu không tồn tại. Đây là bài học quan trọng: chất lượng RAG phụ thuộc 80% vào chất lượng corpus.

2. **Biến nào có tác động lớn nhất tới chất lượng?**
   > **Retrieval strategy** (dense vs hybrid) có tác động lớn nhất — nhưng kết quả ngược kỳ vọng: Hybrid không cải thiện mà còn gây regression ở q07. Chứng tỏ với corpus nhỏ (~5 files), BM25 bổ sung noise nhiều hơn là tín hiệu hữu ích.

3. **Nếu có thêm 1 giờ, nhóm sẽ thử gì tiếp theo?**
   > Thử **Query Expansion** (HyDE — Hypothetical Document Embeddings): Sinh câu trả lời giả định trước khi search để tăng semantic coverage. Cũng sẽ bổ sung tài liệu ERR-403-AUTH và VIP refund vào corpus để giải quyết corpus gap.
