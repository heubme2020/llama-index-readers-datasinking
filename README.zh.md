# LlamaIndex Reader: DataSinking

把上市公司的**财报全文**（资产负债表 / 利润表 / 现金流量表 + 附注）作为 LlamaIndex `Document` 灌进 RAG。让「构建财报 RAG」这个动作里，DataSinking 是第一步。

## 安装

```bash
pip install git+https://github.com/heubme2020/llama-index-readers-datasinking
```

下面 query-engine 的例子还需要 LlamaIndex 本体：`pip install llama-index`。

## 用法（20 行 Colab）

```python
from llama_index.readers.datasinking import DataSinkingReader

# 免费 key 去 datasink.ing 领；不填走公共额度（31 篇/7 天/IP）
reader = DataSinkingReader(api_key="你的 key")
docs = reader.load_data("AAPL", limit=3)   # 苹果最近 3 份财报

from llama_index.core import VectorStoreIndex
index = VectorStoreIndex.from_documents(docs)
print(index.as_query_engine().query("苹果去年的净利润是多少？"))
```

每份报告是一个 `Document`，Markdown 表格原样保留，LLM 能直接读到真实的资产负债表 / 利润表 / 现金流量表。

## 三个例子

仓库里的 [`examples.py`](https://github.com/heubme2020/llama-index-readers-datasinking/blob/main/examples.py) 有三个可直接跑的例子。把 key 设成环境变量再跑：

```bash
export DATASINKING_API_KEY=你的免费key    # Windows：set DATASINKING_API_KEY=你的免费key
python examples.py
```

1. **拉一份财报**——看 `Document` 长什么样（metadata + 全文）。
2. **灌入 5 年财报**——苹果近 5 份共 62 万字的 `Document`，直接喂 `VectorStoreIndex.from_documents`。
3. **跨公司对比**——茅台 vs 五粮液，搜「营业收入」把营收数字并排读出来：

```python
for sym, name in [("600519.SS", "茅台"), ("000858.SZ", "五粮液")]:
    docs = reader.load_data(sym, limit=1)
    # 茅台 → | 营业收入 | 90,703,260,964.48 | ...  ·  五粮液 → | 营业收入（元） | 28,416,674,541.77 | ...
```

## API key / 限额 / 限速

不填 key 也能用，但公共档限速，跑正式 RAG 请用（免费的）key。

| 档位 | 额度 | 限速 |
|---|---|---|
| 无 key（公共） | 7 天 31 篇 / IP | 约 3 秒 1 次 |
| 免费 key | 7 天 8,191 篇 | 3 次/秒 |
| 付费 $31/年 | 7 天 524,287 篇 | 31 次/秒 |

- 额度按「篇」算，不是按请求数——一份财报 = 一篇。
- 撞限速/额度时抛 `QuotaError`，提示里带上面三档明细 + 升级链接（https://datasink.ing/pricing）。

## 支持

- 代码：美股 `AAPL` / A股 `600519.SS` / 日股 `7203.T` / 韩股 `005930.KS` / 台股 `2330.TW` / 英股 `VOD.L`
- 不知道代码？按公司名搜：`GET https://api.datasink.ing/search?q=Apple`
- 每份报告是一个 `Document`，metadata 带 `symbol` / `report_period` / `doc_type`

API 文档：https://datasink.ing/docs
