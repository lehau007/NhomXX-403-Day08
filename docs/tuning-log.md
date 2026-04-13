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
use_rerank = False  # ⚠️ Bug: config thực chạy là False dù label ghi 'variant_hybrid_rerank'
                   # Cross-encoder đã được cài nhưng chưa được bật đúng cách trong lần eval này
# Các tham số còn lại giữ nguyên như baseline
```

**Scorecard Variant 1:**
| Metric | Baseline | Variant 1 | Delta |
|--------|----------|-----------|-------|
| Faithfulness | 4.80/5 | 4.90/5 | **+0.10** |
| Answer Relevance | 3.80/5 | 3.60/5 | **-0.20** |
| Context Recall | 5.00/5 | 5.00/5 | 0.00 |
| Completeness | 3.50/5 | 3.30/5 | **-0.20** |

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
   > **Generation không đủ completeness** khi context chỉ có một phần thông tin: 6/10 câu đạt Completeness ≤ 3/5 ở cả baseline lẫn variant (q01, q04, q06, q07, q08, q10). Nguyên nhân: LLM trả lời đúng nhưng thiếu chi tiết phụ (q01 thiếu "phản hồi 15 phút", q08 thiếu điều kiện "Team Lead phê duyệt"). Với q09 (ERR-403-AUTH): corpus thực sự **không có tài liệu** (`expected_sources: []`) — đây là câu được thiết kế để test khả năng abstain, RAG trả lời "không biết" là **đúng** (Faithfulness=5). Với q10 (VIP refund): tài liệu `policy/refund-v4.pdf` **có tồn tại** nhưng không đề cập quy trình VIP, RAG cũng phải abstain đúng cách.

2. **Biến nào có tác động lớn nhất tới chất lượng?**
   > **Retrieval strategy** (dense vs hybrid) có tác động lớn nhất nhưng kết quả ngược kỳ vọng. Q07 được thiết kế đặc biệt để test hybrid (note trong JSON: *"Đây là query alias/tên cũ — thử nghiệm hybrid retrieval"*), nhưng variant lại fail q07 nghiêm trọng (Completeness 3→1). Nguyên nhân thực: config variant chạy với **`use_rerank=False`** (bug, xem terminal.log dòng 77) — nên kết quả variant chỉ phản ánh Hybrid-only (không có rerank), chưa phản ánh đúng ý định thiết kế. Không thể kết luận "hybrid kém hơn dense" vì reranker chưa được bật thực sự.

3. **Nếu có thêm 1 giờ, nhóm sẽ thử gì tiếp theo?**
   > Ưu tiên **sửa bug `use_rerank=False`** và chạy lại eval với reranker thực sự bật để có kết quả hybrid+rerank chính xác (đặc biệt với q07 — đây là câu được thiết kế để test hybrid alias). Sau đó thử **Query Expansion** cho q06 (escalation có nhiều bước) để cải thiện completeness.
