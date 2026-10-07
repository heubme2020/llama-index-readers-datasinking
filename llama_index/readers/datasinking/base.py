"""DataSinking document loader for LlamaIndex.

Load full-text financial reports into your RAG pipeline:
    reader = DataSinkingReader(api_key="...")
    docs = reader.load_data("AAPL", limit=3)
"""
from typing import List, Optional

import requests
from llama_index.core import Document
from llama_index.core.readers.base import BaseReader

PRICING_URL = "https://datasink.ing/pricing"


class QuotaError(RuntimeError):
    """Raised on 429 (rate limit or quota) with tier info and an upgrade link."""


def _quota_message(detail: str = "") -> str:
    msg = (
        "DataSinking rate limit / quota exceeded. Tiers:\n"
        "  no key (public): 31 reports / 7 days / IP, ~1 request / 3 s\n"
        "  free key:        8,191 reports / 7 days, 3 requests / s\n"
        "  paid ($31/yr):   524,287 reports / 7 days, 31 requests / s\n"
        f"  {PRICING_URL}"
    )
    if detail:
        msg += f"\n(server: {detail})"
    return msg


class DataSinkingReader(BaseReader):
    """Load full-text financial reports from DataSinking as LlamaIndex Documents.

    Leave api_key empty to use the public quota (31 docs / 7 days / IP);
    pass a free key to unlock 8,191 docs / 7 days.
    """

    BASE = "https://api.datasink.ing"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = (api_key or "").strip()

    def load_data(
        self,
        symbol: str,
        limit: int = 1,
        **kwargs,
    ) -> List[Document]:
        params = {
            "symbol": symbol,
            "order": "desc",
            "size": limit,
            "with_content": 1,
        }
        if self.api_key:
            params["apikey"] = self.api_key

        r = requests.get(f"{self.BASE}/documents", params=params, timeout=60)
        if r.status_code == 429:
            detail = ""
            try:
                detail = r.json().get("detail", "")
            except Exception:
                pass
            raise QuotaError(_quota_message(detail))
        r.raise_for_status()
        items = r.json().get("items", [])

        docs: List[Document] = []
        for it in items:
            body = it.get("content", "")
            # Strip the YAML frontmatter (--- ... ---) so the body is clean for the LLM.
            if body.startswith("---"):
                end = body.find("\n---", 3)
                if end != -1:
                    body = body[end + 4:]
            docs.append(
                Document(
                    text=body.strip(),
                    metadata={
                        "symbol": it.get("symbol"),
                        "report_period": it.get("report_period"),
                        "doc_type": it.get("doc_type"),
                        "title": it.get("title"),
                        "source": "datasink.ing",
                    },
                )
            )
        return docs
