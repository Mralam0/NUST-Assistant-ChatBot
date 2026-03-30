import json
import os
import pickle
import numpy as np
import faiss
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import FeatureUnion

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FAQ_PATH = os.path.join(BASE_DIR, "faq.json")
INDEX_PATH = os.path.join(BASE_DIR, "faiss_index", "faq.index")
VECTORIZER_PATH = os.path.join(BASE_DIR, "model_assets", "tfidf_vectorizer.pkl")

_model = None


class LocalFAQEncoder:
    def __init__(self, vectorizer):
        self.vectorizer = vectorizer

    def encode(self, texts, normalize_embeddings=True):
        matrix = self.vectorizer.transform(texts)
        return matrix.toarray().astype("float32")


def load_faqs():
    with open(FAQ_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _make_vectorizer():
    return FeatureUnion([
        (
            "word",
            TfidfVectorizer(
                lowercase=True,
                strip_accents="unicode",
                analyzer="word",
                ngram_range=(1, 2),
                stop_words="english",
                sublinear_tf=True,
            ),
        ),
        (
            "char",
            TfidfVectorizer(
                lowercase=True,
                strip_accents="unicode",
                analyzer="char_wb",
                ngram_range=(3, 5),
                sublinear_tf=True,
            ),
        ),
    ])


def _save_vectorizer(vectorizer):
    os.makedirs(os.path.dirname(VECTORIZER_PATH), exist_ok=True)
    with open(VECTORIZER_PATH, "wb") as f:
        pickle.dump(vectorizer, f)


def _fit_vectorizer(faqs=None):
    if faqs is None:
        faqs = load_faqs()

    questions = [faq["question"] for faq in faqs]
    vectorizer = _make_vectorizer()
    vectorizer.fit(questions)
    _save_vectorizer(vectorizer)
    return LocalFAQEncoder(vectorizer)


def get_model():
    global _model
    if _model is None:
        if os.path.exists(VECTORIZER_PATH):
            with open(VECTORIZER_PATH, "rb") as f:
                _model = LocalFAQEncoder(pickle.load(f))
        else:
            _model = _fit_vectorizer()
    return _model


def build_index(faqs=None):
    global _model
    if faqs is None:
        faqs = load_faqs()

    _model = _fit_vectorizer(faqs)
    questions = [faq["question"] for faq in faqs]
    embeddings = _model.encode(questions, normalize_embeddings=True)
    embeddings = np.array(embeddings, dtype="float32")

    dimension = embeddings.shape[1]
    index = faiss.IndexFlatIP(dimension)
    index.add(embeddings)

    os.makedirs(os.path.dirname(INDEX_PATH), exist_ok=True)
    faiss.write_index(index, INDEX_PATH)
    print(f"FAISS index built with {len(faqs)} entries and saved to {INDEX_PATH}")
    return index


def load_index():
    faqs = load_faqs()
    model = get_model()
    dimension = model.encode([faqs[0]["question"]], normalize_embeddings=True).shape[1]

    if not os.path.exists(INDEX_PATH):
        return build_index(faqs)

    index = faiss.read_index(INDEX_PATH)
    if index.d != dimension or index.ntotal != len(faqs):
        return build_index(faqs)
    return index
