import re
import logging
from typing import List, Dict, Any

from rank_bm25 import BM25Okapi

logger = logging.getLogger(__name__)


class BM25Retriever:
    """
    Lightweight BM25 retriever over the AutoStream knowledge base.

    No external embedding model or vector DB required – perfect for a
    bounded domain with a small-to-medium document set.
    """

    def __init__(self, documents: List[Dict[str, Any]]):
        self.documents = documents
        tokenized = [self._tokenize(doc["content"]) for doc in documents]
        self.bm25 = BM25Okapi(tokenized)
        logger.info(f"BM25Retriever initialised with {len(documents)} documents")

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _tokenize(text: str) -> List[str]:
        """Lowercase, strip punctuation, split on whitespace."""
        return re.sub(r"[^\w\s]", "", text.lower()).split()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def retrieve(self, query: str, top_k: int = 4) -> List[Dict[str, Any]]:
        """Return the top-k most relevant documents for *query*."""
        tokens = self._tokenize(query)
        scores = self.bm25.get_scores(tokens)

        ranked = sorted(
            zip(self.documents, scores),
            key=lambda x: x[1],
            reverse=True,
        )

        results = [
            {**doc, "score": float(score)}
            for doc, score in ranked[:top_k]
            if score > 0.0
        ]

        logger.debug(f"Retrieved {len(results)} chunks for query: '{query}'")
        return results

    def get_context_string(self, query: str, top_k: int = 4) -> str:
        """Return a formatted context string suitable for injection into a prompt."""
        results = self.retrieve(query, top_k=top_k)
        if not results:
            return "(No relevant knowledge-base entries found.)"

        lines = []
        for r in results:
            lines.append(f"[{r['category'].upper()} – {r['title']}]\n{r['content']}")

        return "\n\n".join(lines)

    def get_source_titles(self, query: str, top_k: int = 4) -> List[str]:
        """Return just the titles of the matched documents (for API response metadata)."""
        return [r["title"] for r in self.retrieve(query, top_k=top_k)]
