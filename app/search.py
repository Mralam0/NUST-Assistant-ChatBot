import numpy as np
from embed import get_model, load_faqs, load_index

BEST_MATCH_THRESHOLD = 0.58
RELATED_MATCH_THRESHOLD = 0.3
SEARCH_CANDIDATES = 8
DEFAULT_RELATED_LIMIT = 3

_faqs = None
_index = None


def init():
    global _faqs, _index
    _faqs = load_faqs()
    _index = load_index()


def _format_result(idx: int, score: float):
    return {
        "question": _faqs[idx]["question"],
        "answer": _faqs[idx]["answer"],
        "score": round(float(score), 4),
    }


def find_matches(query: str, related_limit: int = DEFAULT_RELATED_LIMIT):
    global _faqs, _index
    if _faqs is None or _index is None:
        init()

    model = get_model()
    query_embedding = model.encode([query], normalize_embeddings=True)
    query_embedding = np.array(query_embedding, dtype="float32")

    candidate_count = max(related_limit + 3, SEARCH_CANDIDATES)
    scores, indices = _index.search(query_embedding, candidate_count)

    best_result = None
    related_results = []
    seen_questions = set()

    for score, idx in zip(scores[0], indices[0]):
        if idx < 0:
            continue

        result = _format_result(idx, score)
        question_key = result["question"].strip().lower()
        if question_key in seen_questions:
            continue
        seen_questions.add(question_key)

        if best_result is None and score >= BEST_MATCH_THRESHOLD:
            best_result = result
            continue

        if score >= RELATED_MATCH_THRESHOLD:
            related_results.append(result)

    if best_result is not None:
        related_results = [
            item for item in related_results
            if item["question"].strip().lower() != best_result["question"].strip().lower()
        ]

    return {
        "best_match": best_result,
        "related": related_results[:related_limit],
    }


def search(query: str, top_k: int = DEFAULT_RELATED_LIMIT + 1):
    matches = find_matches(query, related_limit=max(top_k - 1, 0))
    if matches["best_match"] is None:
        return matches["related"]
    return [matches["best_match"], *matches["related"]]


def rebuild_index():
    global _faqs, _index
    from embed import build_index
    _faqs = load_faqs()
    _index = build_index(_faqs)
