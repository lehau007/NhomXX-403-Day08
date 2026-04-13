# Lộ trình Lab Day 08 — Full RAG Pipeline

## 1. Mục tiêu chính
Xây dựng trợ lý nội bộ (CS + IT Helpdesk) thực hiện đầy đủ quy trình: **Indexing → Retrieval → Generation → Evaluation**.

---

## 2. Kế hoạch thực hiện (4 Sprints)

### Sprint 1: Build Index (`index.py`) - [60']
- [ ] Implement `get_embedding()` (Sử dụng OpenAI hoặc Sentence Transformers).
- [ ] Hoàn thiện `build_index()`: Thêm logic embed và upsert vào ChromaDB.
- [ ] Đảm bảo mỗi chunk có ít nhất 3 metadata fields: `source`, `section`, `effective_date`.
- [ ] Kiểm tra bằng `list_chunks()` để xác nhận dữ liệu đã vào DB đúng cấu trúc.

### Sprint 2: Baseline Retrieval + Answer (`rag_answer.py`) - [60']
- [ ] Implement `retrieve_dense()`: Truy vấn ChromaDB bằng vector embedding.
- [ ] Implement `call_llm()`: Kết nối API OpenAI hoặc Gemini.
- [ ] Hoàn thiện hàm `rag_answer()`: Trình bày câu trả lời kèm citation `[1]`.
- [ ] Xử lý trường hợp không tìm thấy thông tin (**Abstain**): Trả về "Không đủ dữ liệu" thay vì bịa đặt.

### Sprint 3: Tuning & Optimization (`rag_answer.py`) - [60']
- [ ] Chọn và cài đặt **1 trong 3** phương pháp:
    - **Hybrid Search**: Kết hợp Dense + Sparse (BM25).
    - **Rerank**: Sử dụng Cross-encoder để lọc lại kết quả.
    - **Query Transform**: Chuyển đổi câu hỏi của người dùng để tối ưu truy vấn.
- [ ] So sánh Baseline vs Variant (Dùng `compare_retrieval_strategies()`).
- [ ] Ghi lại lý do chọn và kết quả vào `docs/tuning-log.md`.

### Sprint 4: Evaluation & Reporting (`eval.py`) - [60']
- [ ] Chấm điểm (thủ công hoặc LLM) cho 10 câu hỏi test.
- [ ] Chạy Scorecard cho cả Baseline và Variant.
- [ ] Cập nhật `docs/architecture.md` (Mô tả chunking, retrieval strategy, sơ đồ pipeline).
- [ ] **17:00 - 18:00**: Chạy 10 câu hỏi grading ẩn và nộp `logs/grading_run.json`.
- [ ] Viết báo cáo cá nhân (500-800 từ) trong `reports/individual/`.

---

## 3. Danh sách sản phẩm bàn giao (Deliverables)

| Loại file | Tên file | Deadline |
| :--- | :--- | :--- |
| **Code** | `index.py`, `rag_answer.py`, `eval.py` | 18:00 |
| **Dữ liệu & Log** | `data/test_questions.json`, `logs/grading_run.json` | 18:00 |
| **Tài liệu kỹ thuật** | `docs/architecture.md`, `docs/tuning-log.md`, `results/scorecard_*.md` | 18:00 |
| **Báo cáo** | `reports/group_report.md`, `reports/individual/[tên].md` | Sau 18:00 |

---

## 4. Lưu ý quan trọng
- **Hallucination (Ảo giác)**: Bị chế thông tin sẽ bị trừ 50% điểm câu đó.
- **Tính nhất quán**: Report cá nhân phải khớp với bằng chứng đóng góp code/commit thực tế.
- **Commit**: Sau 18:00, hệ thống sẽ khóa các file code và log kỹ thuật.
