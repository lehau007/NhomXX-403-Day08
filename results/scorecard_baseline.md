# Scorecard: baseline_dense
Generated: 2026-04-13 17:09

## Summary

| Metric | Average Score |
|--------|--------------|
| Faithfulness | 4.80/5 |
| Relevance | 3.80/5 |
| Context Recall | 5.00/5 |
| Completeness | 3.50/5 |

## Per-Question Results

| ID | Category | Faithful | Relevant | Recall | Complete | Notes |
|----|----------|----------|----------|--------|----------|-------|
| q01 | SLA | 5 | 4 | 5 | 3 | Fallback heuristic due to judge error: No module n |
| q02 | Refund | 5 | 5 | 5 | 5 | Fallback heuristic due to judge error: No module n |
| q03 | Access Control | 5 | 4 | 5 | 5 | Fallback heuristic due to judge error: No module n |
| q04 | Refund | 5 | 5 | 5 | 3 | Fallback heuristic due to judge error: No module n |
| q05 | IT Helpdesk | 5 | 5 | 5 | 5 | Fallback heuristic due to judge error: No module n |
| q06 | SLA | 5 | 3 | 5 | 5 | Fallback heuristic due to judge error: No module n |
| q07 | Access Control | 3 | 5 | 5 | 3 | Fallback heuristic due to judge error: No module n |
| q08 | HR Policy | 5 | 5 | 5 | 3 | Fallback heuristic due to judge error: No module n |
| q09 | Insufficient Context | 5 | 1 | None | 2 | Answer correctly states lack of information (truth |
| q10 | Refund | 5 | 1 | 5 | 1 | Answer correctly states lack of information (truth |

## Terminal Log

```text
============================================================

 python eval.py (Variant: Hybrid Only)
============================================================
Sprint 4: Evaluation & Scorecard
============================================================

Loading test questions tu: C:\Users\msilaptop\Desktop\VinUni\lab8\lab\data\test_questions.json
Tim thay 10 cau hoi
	[q01] SLA xu ly ticket P1 la bao lau? (SLA)
	[q02] Khach hang co the yeu cau hoan tien trong bao nhieu ngay? (Refund)
	[q03] Ai phai phe duyet de cap quyen Level 3? (Access Control)
	...

--- Chay Baseline ---
Luu y: Can hoan thanh Sprint 2 truoc khi chay scorecard!

======================================================================
Chay scorecard: baseline_dense
Config: {'retrieval_mode': 'dense', 'top_k_search': 10, 'top_k_select': 3, 'use_rerank': False, 'label': 'baseline_dense'}
======================================================================

[q01] SLA xu ly ticket P1 la bao lau?
	Answer: SLA xu ly (resolution) cho ticket P1 la **4 gio**. [1]...
	Faithful: 5 | Relevant: 4 | Recall: 5 | Complete: 3

[q02] Khach hang co the yeu cau hoan tien trong bao nhieu ngay?
	Answer: Khach hang co the yeu cau hoan tien trong vong **7 ngay lam viec** ke tu thoi diem xac nhan don hang...
	Faithful: 5 | Relevant: 5 | Recall: 5 | Complete: 5

[q03] Ai phai phe duyet de cap quyen Level 3?
	Answer: De cap quyen Level 3 (Elevated Access), can co su phe duyet cua **Line Manager, IT Admin va IT Security**...
	Faithful: 5 | Relevant: 4 | Recall: 5 | Complete: 5

[q04] San pham ky thuat so co duoc hoan tien khong?
	Answer: San pham ky thuat so khong duoc hoan tien, vi chung nam trong danh muc ngoai le khong duoc hoan tien...
	Faithful: 5 | Relevant: 5 | Recall: 5 | Complete: 3

[q05] Tai khoan bi khoa sau bao nhieu lan dang nhap sai?
	Answer: Tai khoan se bi khoa sau 5 lan dang nhap sai lien tiep. [1]...
	Faithful: 5 | Relevant: 5 | Recall: 5 | Complete: 5

[q06] Escalation trong su co P1 dien ra nhu the nao?
	Answer: Trong mot ticket P1, neu khong co phan hoi nao trong vong **10 phut** ke tu khi ticket duoc tao, he ...
	Faithful: 5 | Relevant: 3 | Recall: 5 | Complete: 5

[q07] Approval Matrix de cap quyen he thong la tai lieu nao?
	Answer: Approval Matrix de cap quyen he thong duoc mo ta trong tai lieu **it/access-control-sop.md**, muc **...
	Faithful: 3 | Relevant: 5 | Recall: 5 | Complete: 3

[q08] Nhan vien duoc lam remote toi da may ngay moi tuan?
	Answer: Nhan vien duoc lam remote toi da **2 ngay moi tuan**. [1]...
	Faithful: 5 | Relevant: 5 | Recall: 5 | Complete: 3

[q09] ERR-403-AUTH la loi gi va cach xu ly?
	Answer: Toi khong tim thay du thong tin trong tai lieu de tra loi cau hoi nay....
	Faithful: 5 | Relevant: 1 | Recall: None | Complete: 2

[q10] Neu can hoan tien khan cap cho khach hang VIP, quy trinh co khac khong?
	Answer: Toi khong tim thay du thong tin trong tai lieu de tra loi cau hoi nay....
	Faithful: 5 | Relevant: 1 | Recall: 5 | Complete: 1

Average faithfulness: 4.80
Average relevance: 3.80
Average context_recall: 5.00
Average completeness: 3.50

Scorecard luu tai: C:\Users\msilaptop\Desktop\VinUni\lab8\lab\results\scorecard_baseline.md

--- Chay Variant ---

======================================================================
Chay scorecard: variant_hybrid_rerank
Config: {'retrieval_mode': 'hybrid', 'top_k_search': 15, 'top_k_select': 3, 'use_rerank': False, 'label': 'variant_hybrid_rerank'}
======================================================================

[q01] SLA xu ly ticket P1 la bao lau?
	Answer: SLA xu ly (resolution) cho ticket P1 la **4 gio**. [1]...
	Faithful: 5 | Relevant: 4 | Recall: 5 | Complete: 3

[q02] Khach hang co the yeu cau hoan tien trong bao nhieu ngay?
	Answer: Khach hang co the yeu cau hoan tien trong vong **7 ngay lam viec** ke tu thoi diem xac nhan don hang...
	Faithful: 5 | Relevant: 5 | Recall: 5 | Complete: 5

[q03] Ai phai phe duyet de cap quyen Level 3?
	Answer: De cap quyen Level 3 (Elevated Access), yeu cau phai duoc phe duyet boi Line Manager, IT Admin va IT...
	Faithful: 5 | Relevant: 5 | Recall: 5 | Complete: 5

[q04] San pham ky thuat so co duoc hoan tien khong?
	Answer: San pham ky thuat so khong duoc hoan tien, vi chung nam trong danh muc ngoai le khong duoc hoan tien...
	Faithful: 5 | Relevant: 5 | Recall: 5 | Complete: 3

[q05] Tai khoan bi khoa sau bao nhieu lan dang nhap sai?
	Answer: Tai khoan se bi khoa sau 5 lan dang nhap sai lien tiep. [1]...
	Faithful: 5 | Relevant: 5 | Recall: 5 | Complete: 5

[q06] Escalation trong su co P1 dien ra nhu the nao?
	Answer: Trong truong hop su co P1, khi ticket duoc tao, neu khong co phan hoi nao trong vong **10 phut** thi...
	Faithful: 4 | Relevant: 3 | Recall: 5 | Complete: 5

[q07] Approval Matrix de cap quyen he thong la tai lieu nao?
	Answer: Toi khong tim thay du thong tin trong tai lieu de tra loi cau hoi nay....
	Faithful: 5 | Relevant: 2 | Recall: 5 | Complete: 1

[q08] Nhan vien duoc lam remote toi da may ngay moi tuan?
	Answer: Nhan vien duoc lam remote toi da **2 ngay moi tuan**. [1]...
	Faithful: 5 | Relevant: 5 | Recall: 5 | Complete: 3

[q09] ERR-403-AUTH la loi gi va cach xu ly?
	Answer: Toi khong tim thay du thong tin trong tai lieu de tra loi cau hoi nay....
	Faithful: 5 | Relevant: 1 | Recall: None | Complete: 2

[q10] Neu can hoan tien khan cap cho khach hang VIP, quy trinh co khac khong?
	Answer: Toi khong tim thay du thong tin trong tai lieu de tra loi cau hoi nay....
	Faithful: 5 | Relevant: 1 | Recall: 5 | Complete: 1

Average faithfulness: 4.90
Average relevance: 3.60
Average context_recall: 5.00
Average completeness: 3.30

Scorecard variant luu tai: C:\Users\msilaptop\Desktop\VinUni\lab8\lab\results\scorecard_variant.md

======================================================================
A/B Comparison: Baseline vs Variant
======================================================================
Metric                 Baseline    Variant    Delta
-------------------------------------------------------
faithfulness               4.80       4.90    +0.10
relevance                  3.80       3.60    -0.20
context_recall             5.00       5.00    +0.00
completeness               3.50       3.30    -0.20

Cau    Baseline F/R/Rc/C      Variant F/R/Rc/C       Better?
-----------------------------------------------------------------
q01    5/4/5/3                5/4/5/3                Tie
q02    5/5/5/5                5/5/5/5                Tie
q03    5/4/5/5                5/5/5/5                Variant
q04    5/5/5/3                5/5/5/3                Tie
q05    5/5/5/5                5/5/5/5                Tie
q06    5/3/5/5                4/3/5/5                Baseline
q07    3/5/5/3                5/2/5/1                Baseline
q08    5/5/5/3                5/5/5/3                Tie
q09    5/1/None/2             5/1/None/2             Tie
q10    5/1/5/1                5/1/5/1                Tie

Ket qua da luu vao: C:\Users\msilaptop\Desktop\VinUni\lab8\lab\results\ab_comparison.csv
``` 
