from ragas import evaluate
from ragas.llms import LangchainLLMWrapper

evaluator_llm = LangchainLLMWrapper(llm)
from ragas.dataset_schema import RagasDataset


def run_ragas_scorecard(test_questions: Optional[List[Dict]] = None) -> List[Dict[str, Any]]:
    dataset = RagasDataset.from_list(test_questions)
    results = evaluate(dataset=dataset, metrics=[])
    return
