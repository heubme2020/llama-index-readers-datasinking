"""DataSinking document loader for LlamaIndex.

把 DataSinking 的财报全文灌进 RAG：
    reader = DataSinkingReader(api_key="...")
    docs = reader.load_data("600519.SS", limit=3)
"""
from typing import List, Optional

import requests
from llama_index.core import Document
from llama_index.core.readers.base import BaseReader


class DataSinkingReader(BaseReader):
    """Load full-text financial reports from DataSinking as LlamaIndex Documents.

    免费档可不填 api_key（走公共额度，31 篇/7 天/IP）；填 key 解锁 8191 篇/7 天。
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
        r.raise_for_status()
        items = r.json().get("items", [])

        docs: List[Document] = []
        for it in items:
            body = it.get("content", "")
            # 去掉 YAML frontmatter（--- ... ---），喂给 LLM 更干净
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
