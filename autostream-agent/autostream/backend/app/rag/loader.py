import json
import logging
from pathlib import Path
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class KnowledgeBaseLoader:
    """
    Loads the AutoStream knowledge base from a JSON file and
    converts it into a flat list of searchable document chunks.
    """

    def __init__(self, kb_path: str):
        self.kb_path = Path(kb_path)
        self._raw: Dict[str, Any] = {}
        self.documents: List[Dict[str, Any]] = []
        self._load()

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _load(self) -> None:
        if not self.kb_path.exists():
            raise FileNotFoundError(f"Knowledge base not found at: {self.kb_path}")

        with open(self.kb_path, "r", encoding="utf-8") as f:
            self._raw = json.load(f)

        self._flatten()
        logger.info(f"Loaded {len(self.documents)} knowledge-base chunks from {self.kb_path}")

    def _flatten(self) -> None:
        """Convert the nested JSON into flat, searchable text chunks."""
        data = self._raw

        # Company overview
        company = data.get("company", {})
        self.documents.append(
            {
                "id": "company_overview",
                "category": "company",
                "title": "About AutoStream",
                "content": (
                    f"{company.get('name', '')} – {company.get('tagline', '')}. "
                    f"{company.get('description', '')} "
                    f"Supported platforms: {', '.join(company.get('supported_platforms', []))}."
                ),
            }
        )

        # Pricing – Basic
        basic = data.get("pricing", {}).get("basic", {})
        self.documents.append(
            {
                "id": "pricing_basic",
                "category": "pricing",
                "title": "Basic Plan Pricing & Features",
                "content": (
                    f"Basic Plan: ${basic.get('price_monthly')}/month "
                    f"(or ${basic.get('price_annual')}/month billed annually). "
                    f"Includes: {', '.join(basic.get('features', []))}. "
                    f"Limitations: {', '.join(basic.get('limitations', []))}."
                ),
            }
        )

        # Pricing – Pro
        pro = data.get("pricing", {}).get("pro", {})
        self.documents.append(
            {
                "id": "pricing_pro",
                "category": "pricing",
                "title": "Pro Plan Pricing & Features",
                "content": (
                    f"Pro Plan: ${pro.get('price_monthly')}/month "
                    f"(or ${pro.get('price_annual')}/month billed annually). "
                    f"Includes: {', '.join(pro.get('features', []))}."
                ),
            }
        )

        # Policies
        policies = data.get("policies", {})
        policy_map = {
            "policy_refund": ("Refund Policy", "refund"),
            "policy_support": ("Support Policy", "support"),
            "policy_trial": ("Free Trial Policy", "trial"),
            "policy_cancel": ("Cancellation Policy", "cancellation"),
            "policy_data": ("Data & Storage Policy", "data"),
            "policy_billing": ("Billing Policy", "billing"),
        }
        for doc_id, (title, key) in policy_map.items():
            if key in policies:
                self.documents.append(
                    {
                        "id": doc_id,
                        "category": "policy",
                        "title": title,
                        "content": policies[key],
                    }
                )

        # Features
        features = data.get("features", {})
        for feature_key, feature_data in features.items():
            self.documents.append(
                {
                    "id": f"feature_{feature_key}",
                    "category": "feature",
                    "title": feature_data.get("title", feature_key),
                    "content": (
                        f"{feature_data.get('description', '')} "
                        f"Available on: {feature_data.get('available_on', 'All plans')}."
                    ),
                }
            )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_all_documents(self) -> List[Dict[str, Any]]:
        return self.documents

    def get_full_context(self) -> str:
        """Return the entire knowledge base as a single formatted string."""
        sections: Dict[str, List[str]] = {}
        for doc in self.documents:
            cat = doc["category"].upper()
            sections.setdefault(cat, []).append(f"  • {doc['title']}: {doc['content']}")

        lines = []
        for cat, items in sections.items():
            lines.append(f"[{cat}]")
            lines.extend(items)
            lines.append("")
        return "\n".join(lines)
