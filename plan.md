# Kế hoạch Triển khai Lab Day 08 — Nhóm 3 người

## 1. Phân chia Vai trò (Role Assignment)

| Vai trò | Trách nhiệm chính | Thành viên phụ trách |
| :--- | :--- | :--- |
| **Tech Lead & Integration** | Thiết lập môi trường, nối pipeline, xử lý LLM API, chạy kết quả cuối cùng (`eval.py`, `rag_answer.py`). | [Tên Thành viên 1] |
| **Retrieval & Tuning Owner** | Xử lý dữ liệu (Chunking, Metadata), cài đặt phương pháp tìm kiếm (Dense, Hybrid/Rerank) (`index.py`, `rag_answer.py`). | [Tên Thành viên 2] |
| **Eval & Documentation Owner** | Quản lý câu hỏi test, chạy Scorecard, viết tài liệu kiến trúc và nhật ký tối ưu (`architecture.md`, `tuning-log.md`). | [Tên Thành viên 3] |

---

## 2. Kế hoạch Sprint (60 phút/Sprint)

### Sprint 1: Indexing (13:00 - 14:00)
*   **Tech Lead**: Setup `.env`, cài `requirements.txt`, viết hàm `get_embedding()`.
*   **Retrieval Owner**: Hoàn thiện logic chunking và metadata trong `build_index()`.
*   **Eval Owner**: Đọc dữ liệu mẫu, chuẩn bị tiêu chí chấm điểm cho 10 câu hỏi test.

### Sprint 2: Baseline RAG (14:00 - 15:00)
*   **Tech Lead**: Cài đặt `call_llm()` và logic trình bày câu trả lời (Citation).
*   **Retrieval Owner**: Cài đặt `retrieve_dense()` để kết nối với ChromaDB.
*   **Eval Owner**: Chạy thử Baseline với 3 câu hỏi mẫu, kiểm tra tính chính xác của nguồn trích dẫn.

### Sprint 3: Optimization & Tuning (15:00 - 16:00)
*   **Retrieval Owner**: Cài đặt **Variant** (Hybrid Search hoặc Rerank).
*   **Eval Owner**: Chạy `eval.py` để so sánh Baseline vs Variant. Ghi kết quả vào `tuning-log.md`.
*   **Tech Lead**: Hỗ trợ fix bug khi nối các phần tối ưu vào pipeline chính.

### Sprint 4: Finalization & Grading (16:00 - 18:00)
*   **Cả nhóm**: Kiểm tra lại toàn bộ pipeline (End-to-End).
*   **Eval Owner**: Hoàn thiện `architecture.md` (vẽ sơ đồ pipeline).
*   **17:00 (Giờ G)**: Nhận `grading_questions.json`, Tech Lead chạy log và nộp `grading_run.json`.
*   **Sau 18:00**: Mỗi thành viên tự viết báo cáo cá nhân trong thư mục `reports/individual/`.

---

## 3. Quy trình phối hợp (Git/Files)
- **Cảnh báo quan trọng**: Tuyệt đối không sửa chung một file cùng lúc để tránh xung đột (Conflict).
- **Quy tắc đặt tên đóng góp**: Thêm comment `# [Role] - [Tên]` trước các đoạn code mình viết.
- **Dùng chung API Key**: Thống nhất dùng chung key trong `.env` để kết quả đánh giá đồng nhất.

---

## 4. Danh sách kiểm tra trước 18:00 (Checklist)
- [ ] `index.py` chạy tạo được DB với 5 tài liệu.
- [ ] `rag_answer.py` trả về câu trả lời có citation `[1]`.
- [ ] `logs/grading_run.json` có đủ 10 câu hỏi grading.
- [ ] `docs/architecture.md` và `docs/tuning-log.md` đã đầy đủ nội dung.
- [ ] Không có file `.py` nào được chỉnh sửa sau 18:00.
