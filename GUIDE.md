# Hướng dẫn Thiết lập Dự án (Setup Guide)

Chào mừng các thành viên vào dự án **Lab Day 08 — Full RAG Pipeline**. Dưới đây là các bước để cài đặt môi trường làm việc trên cả **Windows** và **Linux/macOS**.

---

## 1. Yêu cầu hệ thống (Prerequisites)
- **Python**: Phiên bản 3.10 trở lên.
- **Git**: Đã được cài đặt.

---

## 2. Các bước cài đặt (Setup Steps)

### Đối với Windows (Sử dụng PowerShell)
1.  **Clone dự án** (nếu chưa):
    ```powershell
    git clone <url-repo-cua-nhom>
    cd <thu-muc-du-an>
    ```
2.  **Tạo môi trường ảo (venv)**:
    ```powershell
    python -m venv venv
    ```
3.  **Kích hoạt môi trường ảo**:
    ```powershell
    .\venv\Scripts\Activate.ps1
    ```
    *(Nếu lỗi "Execution Policy", chạy: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process`)*
4.  **Cài đặt thư viện**:
    ```powershell
    pip install -r requirements.txt
    ```

### Đối với Linux / macOS (Sử dụng Terminal)
1.  **Clone dự án** (nếu chưa):
    ```bash
    git clone <url-repo-cua-nhom>
    cd <thu-muc-du-an>
    ```
2.  **Tạo môi trường ảo (venv)**:
    ```bash
    python3 -m venv venv
    ```
3.  **Kích hoạt môi trường ảo**:
    ```bash
    source venv/bin/activate
    ```
4.  **Cài đặt thư viện**:
    ```bash
    pip install -r requirements.txt
    ```

---

## 3. Cấu hình Biến môi trường (.env)
Copy file `.env.example` thành `.env` và điền các thông tin sau (Liên hệ Tech Lead để lấy Key/Endpoint):
```env
# NVIDIA NIM (LLM)
NVIDIA_API_KEY=nvapi-xxxxxx
NVIDIA_API_BASE=https://integrate.api.nvidia.com/v1
LLM_MODEL=meta/llama-3.1-70b-instruct

# Google Colab (Embedding)
EMBEDDING_ENDPOINT=http://xxxx.ngrok-free.app/embed

# Vector DB
CHROMA_DB_PATH=./data/chroma_db
COLLECTION_NAME=lab8_rag_collection
```

---

## 4. Kiểm tra Setup (Verification)
Sau khi cài đặt xong, hãy chạy lệnh sau để kiểm tra xem script có lỗi thư viện hay không:
```bash
python index.py
```
Nếu thấy danh sách tài liệu hiện ra và thông báo "Sprint 1 setup hoàn thành!", bạn đã sẵn sàng!

---

## 5. Quy tắc làm việc Nhóm (Team Rules)
- **Git Commit**: Luôn thêm role và tên vào commit message. Ví dụ: `[Retrieval] Implement chunking logic`.
- **Code Comment**: Ghi tên mình trước các hàm quan trọng.
- **Merge Code**: Chỉ Tech Lead mới được merge vào nhánh `main`.
