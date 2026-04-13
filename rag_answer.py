"""
rag_answer.py — Sprint 2 + Sprint 3: Retrieval & Grounded Answer
================================================================
Sprint 2 (60 phút): Baseline RAG
  - Dense retrieval từ ChromaDB
  - Grounded answer function với prompt ép citation
  - Trả lời được ít nhất 3 câu hỏi mẫu, output có source

Sprint 3 (60 phút): Tuning tối thiểu
  - Thêm hybrid retrieval (dense + sparse/BM25)
  - Hoặc thêm rerank (cross-encoder)
  - Hoặc thử query transformation (expansion, decomposition, HyDE)
  - Tạo bảng so sánh baseline vs variant
"""

import os
from typing import Any, Dict, List

from dotenv import load_dotenv

load_dotenv()

# =============================================================================
# CẤU HÌNH
# =============================================================================

TOP_K_SEARCH = 10  # Số chunk lấy từ vector store trước rerank (search rộng)
TOP_K_SELECT = 3  # Số chunk gửi vào prompt sau rerank/select (top-3 sweet spot)

LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")


# =============================================================================
# RETRIEVAL — DENSE (Vector Search)
# =============================================================================


def retrieve_dense(query: str, top_k: int = TOP_K_SEARCH) -> List[Dict[str, Any]]:
    """
    Dense retrieval: tìm kiếm theo embedding similarity trong ChromaDB.
    """
    import chromadb

    from index import CHROMA_DB_DIR, COLLECTION_NAME, get_embedding

    client = chromadb.PersistentClient(path=str(CHROMA_DB_DIR))
    collection = client.get_collection(COLLECTION_NAME)

    query_embedding = get_embedding(query)
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=["documents", "metadatas", "distances"]
    )

    chunks = []
    if results["documents"]:
        for i in range(len(results["documents"][0])):
            chunks.append({
                "text": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "score": 1 - results["distances"][0][i]  # Cosine similarity approximation
            })
    return chunks


# =============================================================================
# RETRIEVAL — SPARSE / BM25 (Keyword Search)
# Dùng cho Sprint 3 Variant hoặc kết hợp Hybrid
# =============================================================================


def retrieve_sparse(query: str, top_k: int = TOP_K_SEARCH) -> List[Dict[str, Any]]:
    """
    Sparse retrieval: tìm kiếm theo keyword (BM25).
    """
    from rank_bm25 import BM25Okapi
    import chromadb

    from index import CHROMA_DB_DIR, COLLECTION_NAME
    client = chromadb.PersistentClient(path=str(CHROMA_DB_DIR))
    collection = client.get_collection(COLLECTION_NAME)

    all_chunks = collection.get(include=["documents", "metadatas"])
    corpus = [chunk["text"] for chunk in all_chunks]
    
    tokenized_corpus = [doc.lower().split() for doc in corpus]
    bm25 = BM25Okapi(tokenized_corpus)
    tokenized_query = query.lower().split()
    scores = bm25.get_scores(tokenized_query)
    top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]

    return [
        {
            "text": all_chunks["documents"][i],
            "metadata": all_chunks["metadatas"][i],
            "score": scores[i],
        }
        for i in top_indices
    ]

# =============================================================================
# RETRIEVAL — HYBRID (Dense + Sparse với Reciprocal Rank Fusion)
# =============================================================================


def retrieve_hybrid(
    query: str,
    top_k: int = TOP_K_SEARCH,
    dense_weight: float = 0.6,
    sparse_weight: float = 0.4,
) -> List[Dict[str, Any]]:
    """
    Hybrid retrieval: kết hợp dense và sparse bằng Reciprocal Rank Fusion (RRF).
    """
    dense_results = retrieve_dense(query, top_k=top_k)
    sparse_results = retrieve_sparse(query, top_k=top_k)

    rrf_scores: Dict[str, float] = {}
    chunks_map: Dict[str, Dict[str, Any]] = {}

    for rank, chunk in enumerate(dense_results):
        key = chunk["metadata"].get("source", "") + chunk["text"][:50]
        rrf_scores[key] = rrf_scores.get(key, 0) + dense_weight * (1 / (60 + rank))
        chunks_map[key] = chunk

    for rank, chunk in enumerate(sparse_results):
        key = chunk["metadata"].get("source", "") + chunk["text"][:50]
        rrf_scores[key] = rrf_scores.get(key, 0) + sparse_weight * (1 / (60 + rank))
        chunks_map[key] = chunk

    sorted_keys = sorted(rrf_scores, key=lambda k: rrf_scores[k], reverse=True)[:top_k]

    return [
        {**chunks_map[key], "score": rrf_scores[key]}
        for key in sorted_keys
    ]


# =============================================================================
# RERANK (Cross-Encoder)
# =============================================================================


def rerank(
    query: str,
    candidates: List[Dict[str, Any]],
    top_k: int = TOP_K_SELECT,
) -> List[Dict[str, Any]]:
    """
    Rerank các chunk bằng Cross-Encoder model.
    """
    from sentence_transformers import CrossEncoder
    model = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
    
    sentence_pairs = [[query, chunk["text"]] for chunk in candidates]
    scores = model.predict(sentence_pairs)
    
    for i, score in enumerate(scores):
        candidates[i]["rerank_score"] = float(score)
        
    reranked_chunks = sorted(candidates, key=lambda x: x["rerank_score"], reverse=True)
    return reranked_chunks[:top_k]


# =============================================================================
# QUERY TRANSFORMATION (Sprint 3 alternative)
# =============================================================================


def transform_query(query: str, strategy: str = "expansion") -> List[str]:
    """
    Biến đổi query để tăng recall.

    Strategies:
      - "expansion": Thêm từ đồng nghĩa, alias, tên cũ
      - "decomposition": Tách query phức tạp thành 2-3 sub-queries
      - "hyde": Sinh câu trả lời giả (hypothetical document) để embed thay query

    TODO Sprint 3 (nếu chọn query transformation):
    Gọi LLM với prompt phù hợp với từng strategy.

    Ví dụ expansion prompt:
        "Given the query: '{query}'
         Generate 2-3 alternative phrasings or related terms in Vietnamese.
         Output as JSON array of strings."

    Ví dụ decomposition:
        "Break down this complex query into 2-3 simpler sub-queries: '{query}'
         Output as JSON array."

    Khi nào dùng:
    - Expansion: query dùng alias/tên cũ (ví dụ: "Approval Matrix" → "Access Control SOP")
    - Decomposition: query hỏi nhiều thứ một lúc
    - HyDE: query mơ hồ, search theo nghĩa không hiệu quả
    """
    # TODO Sprint 3: Implement query transformation
    # Tạm thời trả về query gốc
    return [query]


# =============================================================================
# GENERATION — GROUNDED ANSWER FUNCTION
# =============================================================================


def build_context_block(chunks: List[Dict[str, Any]]) -> str:
    """
    Biến danh sách chunks thành một khối text context có đánh số [1], [2], ...
    """
    context_parts = []
    for i, chunk in enumerate(chunks):
        source = chunk["metadata"].get("source", "Unknown")
        section = chunk["metadata"].get("section", "General")
        context_parts.append(f"[{i+1}] (Source: {source}, Section: {section})\n{chunk['text']}")
    
    return "\n\n".join(context_parts)


def build_grounded_prompt(query: str, context_block: str) -> str:
    """
    Tạo prompt yêu cầu LLM trả lời CHỈ dựa trên context và trích dẫn [1], [2].
    """
    return f"""Bạn là một trợ lý nội bộ chuyên nghiệp. Hãy trả lời câu hỏi dưới đây dựa TRỰC TIẾP trên các tài liệu được cung cấp.

QUY TẮC:
1. Chỉ sử dụng thông tin từ phần 'BẰNG CHỨNG' dưới đây.
2. Nếu thông tin không có trong bằng chứng, hãy trả lời: "Tôi không tìm thấy đủ thông tin trong tài liệu để trả lời câu hỏi này."
3. PHẢI trích dẫn nguồn bằng cách thêm [số thứ tự] vào cuối mỗi câu hoặc đoạn văn có sử dụng thông tin đó. Ví dụ: "Thời gian xử lý ticket P1 là 4 giờ. [1]"

BẰNG CHỨNG:
{context_block}

CÂU HỎI: {query}

CÂU TRẢ LỜI:"""


def call_llm(prompt: str) -> str:
    """
    Gọi LLM để sinh câu trả lời. Hỗ trợ openai, gemini, nvidia.
    """
    provider = os.getenv("LLM_PROVIDER", "openai").lower()
    model_name = os.getenv("LLM_MODEL", "gpt-4o-mini")

    if provider == "nvidia":
        from openai import OpenAI
        client = OpenAI(
            base_url=os.getenv("NVIDIA_API_BASE", "https://integrate.api.nvidia.com/v1"),
            api_key=os.getenv("NVIDIA_API_KEY")
        )
        response = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=1024,
        )
        return response.choices[0].message.content

    elif provider == "openai":
        from openai import OpenAI
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=1024,
        )
        return response.choices[0].message.content

    elif provider == "gemini":
        import google.generativeai as genai
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        return response.text

    else:
        raise ValueError(f"Provider LLM '{provider}' không được hỗ trợ.")


def rag_answer(
    query: str,
    retrieval_mode: str = "dense",
    top_k_search: int = TOP_K_SEARCH,
    top_k_select: int = TOP_K_SELECT,
    use_rerank: bool = False,
    verbose: bool = False,
) -> Dict[str, Any]:
    """
    Pipeline RAG hoàn chỉnh.
    """
    config = {
        "retrieval_mode": retrieval_mode,
        "top_k_search": top_k_search,
        "top_k_select": top_k_select,
        "use_rerank": use_rerank,
    }

    # --- Bước 1: Retrieve ---
    if retrieval_mode == "dense":
        candidates = retrieve_dense(query, top_k=top_k_search)
    elif retrieval_mode == "sparse":
        candidates = retrieve_sparse(query, top_k=top_k_search)
    elif retrieval_mode == "hybrid":
        candidates = retrieve_hybrid(query, top_k=top_k_search)
    else:
        raise ValueError(f"retrieval_mode không hợp lệ: {retrieval_mode}")

    if verbose:
        print(f"\n[RAG] Query: {query}")
        print(f"[RAG] Retrieved {len(candidates)} candidates (mode={retrieval_mode})")
<<<<<<< HEAD
=======
        for i, c in enumerate(candidates[:3]):
            print(f"  [{i + 1}] score={c.get('score', 0):.3f} | {c['metadata'].get('source', '?')}")
>>>>>>> dev/tuna_sprint2

    # --- Bước 2: Rerank (optional) ---
    if use_rerank:
        candidates = rerank(query, candidates, top_k=top_k_select)
    else:
        candidates = candidates[:top_k_select]

    # --- Bước 3: Build context và prompt ---
    context_block = build_context_block(candidates)
    prompt = build_grounded_prompt(query, context_block)

    # --- Bước 4: Generate ---
    answer = call_llm(prompt)

    # --- Bước 5: Extract sources ---
    sources = list({c["metadata"].get("source", "unknown") for c in candidates})

    return {
        "query": query,
        "answer": answer,
        "sources": sources,
        "chunks_used": candidates,
        "config": config,
    }


# =============================================================================
# SPRINT 3: SO SÁNH BASELINE VS VARIANT
# =============================================================================


def compare_retrieval_strategies(query: str) -> None:
    """
    So sánh các retrieval strategies.
    """
    print(f"\n{'=' * 60}")
    print(f"Query: {query}")
    print("=" * 60)

    strategies = ["dense", "hybrid"]

    for strategy in strategies:
        print(f"\n--- Strategy: {strategy} ---")
        try:
            result = rag_answer(query, retrieval_mode=strategy, verbose=False)
            print(f"Answer: {result['answer']}")
            print(f"Sources: {result['sources']}")
        except Exception as e:
            print(f"Lỗi: {e}")


# =============================================================================
# MAIN — Demo và Test
# =============================================================================

if __name__ == "__main__":
    # Test queries
    test_queries = [
        "SLA xử lý ticket P1 là bao lâu?",
        "Khách hàng có thể yêu cầu hoàn tiền trong bao nhiêu ngày?",
        "Ai phải phê duyệt để cấp quyền Level 3?",
    ]

    print("\n--- Sprint 2: Test Baseline (Dense) ---")
    for query in test_queries:
        print(f"\nQuery: {query}")
        try:
            result = rag_answer(query, retrieval_mode="dense", verbose=True)
            print(f"Answer: {result['answer']}")
            print(f"Sources: {result['sources']}")
        except Exception as e:
            print(f"Lỗi: {e}")
