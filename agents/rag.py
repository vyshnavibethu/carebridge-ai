import json
import os
from pathlib import Path
from typing import List, Dict, Any
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

KNOWLEDGE_FILE = Path(__file__).parent.parent / "medical_knowledge.json"

class MedicalRAG:
    def __init__(self, knowledge_path: Path = KNOWLEDGE_FILE):
        self.knowledge_path = knowledge_path
        self.data = self._load_data()
        self.vectorizer = TfidfVectorizer(stop_words='english')
        self.corpus_vectors = None
        self._build_index()

    def _load_data(self) -> List[Dict[str, Any]]:
        if not self.knowledge_path.exists():
            return []
        with open(self.knowledge_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _build_index(self):
        if not self.data:
            return
        corpus = []
        for item in self.data:
            # Combine symptoms, topic, and simple explanation for rich embedding text
            symptoms_str = " ".join(item.get("symptoms", []))
            topic = item.get("topic", "")
            exp = item.get("simple_explanation", "")
            doc_text = f"{topic} {symptoms_str} {exp}"
            corpus.append(doc_text)

        if corpus:
            self.corpus_vectors = self.vectorizer.fit_transform(corpus)

    def search(self, query: str, top_k: int = 2) -> List[Dict[str, Any]]:
        if not self.data or not query:
            return []

        # Vectorize query
        query_vec = self.vectorizer.transform([query])
        similarities = cosine_similarity(query_vec, self.corpus_vectors).flatten()

        # Get top-k indices
        top_indices = similarities.argsort()[::-1][:top_k]

        results = []
        for idx in top_indices:
            score = float(similarities[idx])
            item = dict(self.data[idx])
            item["relevance_score"] = round(score, 4)
            results.append(item)

        return results

# Singleton instance
_rag_instance = None

def get_rag_engine():
    global _rag_instance
    if _rag_instance is None:
        _rag_instance = MedicalRAG()
    return _rag_instance

def search_medical_knowledge(query: str, top_k: int = 2) -> List[Dict[str, Any]]:
    """
    RAG Tool function to retrieve verified medical knowledge for a given symptom query.
    """
    engine = get_rag_engine()
    return engine.search(query, top_k=top_k)
