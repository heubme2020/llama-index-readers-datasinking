# LlamaIndex Reader: DataSinking

Load full-text financial reports (balance sheet, income statement, cash flow + notes) as LlamaIndex `Document`s for your RAG pipeline. Makes DataSinking the first step of "build a financial-report RAG".

## Install

```bash
pip install git+https://github.com/heubme2020/llama-index-readers-datasinking
```

The query-engine example below also needs LlamaIndex itself: `pip install llama-index`.

## Usage (20-line Colab)

```python
from llama_index.readers.datasinking import DataSinkingReader

# Get a free key at datasink.ing; leave empty for the public quota (31 docs / 7 days / IP)
reader = DataSinkingReader(api_key="your key")
docs = reader.load_data("AAPL", limit=3)   # Apple's 3 latest filings

from llama_index.core import VectorStoreIndex
index = VectorStoreIndex.from_documents(docs)
print(index.as_query_engine().query("What was Apple's net income last year?"))
```

Each report becomes one `Document`; its Markdown tables are preserved, so the LLM can read the actual balance sheet / income statement / cash flow.

## Three examples

The repo's [`examples.py`](https://github.com/heubme2020/llama-index-readers-datasinking/blob/main/examples.py) has three runnable examples. Set your key as an env var and run:

```bash
export DATASINKING_API_KEY=your_free_key    # Windows: set DATASINKING_API_KEY=your_free_key
python examples.py
```

1. **Fetch one filing** — see what a `Document` looks like (metadata + full text).
2. **Load 5 years of filings** — 626k characters of Apple filings as 5 `Document`s, ready for `VectorStoreIndex.from_documents`.
3. **Cross-company comparison** — search "营业收入" across Moutai vs Wuliangye and read the revenue figures side by side:

```python
for sym, name in [("600519.SS", "茅台"), ("000858.SZ", "五粮液")]:
    docs = reader.load_data(sym, limit=1)
    # 茅台 → | 营业收入 | 90,703,260,964.48 | ...  ·  五粮液 → | 营业收入（元） | 28,416,674,541.77 | ...
```

## API key, quotas and rate limits

You don't need a key to start, but the public tier is throttled — use a (free) key for real RAG pipelines.

| Tier | Quota | Rate limit |
|---|---|---|
| No key (public) | 31 reports / 7 days / IP | ~1 request / 3 s |
| Free key | 8,191 reports / 7 days | 3 requests / s |
| Paid ($31/yr) | 524,287 reports / 7 days | 31 requests / s |

- Quota counts **reports**, not requests — one report = one unit.
- Hit a limit and you get a `QuotaError` carrying the tier table above plus the upgrade link (https://datasink.ing/pricing).

## Supported symbols

- US `AAPL` · China `600519.SS` · Japan `7203.T` · Korea `005930.KS` · Taiwan `2330.TW` · UK `VOD.L`
- Don't know the ticker? Search by name: `GET https://api.datasink.ing/search?q=Apple`
- Each report is a `Document` with metadata `symbol` / `report_period` / `doc_type`

API docs: https://datasink.ing/docs
