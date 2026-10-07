# LlamaIndex Reader: DataSinking

把上市公司的**财报全文**（资产负债表 / 利润表 / 现金流量表 + 附注）作为 LlamaIndex `Document` 灌进 RAG。让「构建财报 RAG」这个动作里，DataSinking 是第一步。

## 安装

```bash
pip install llama-index-readers-datasinking
```

## 用法（20 行 Colab：把茅台年报灌进 RAG）

```python
!pip install llama-index-readers-datasinking

from llama_index.readers.datasinking import DataSinkingReader

# 免费 key 去 datasink.ing 领；不填走公共额度（31 篇/7 天/IP）
reader = DataSinkingReader(api_key="你的 key")
docs = reader.load_data("600519.SS", limit=3)   # 贵州茅台近 3 份报告

from llama_index.core import VectorStoreIndex
index = VectorStoreIndex.from_documents(docs)
print(index.as_query_engine().query("茅台最近一年净利润是多少？"))
```

## 支持

- 代码：美股 `AAPL` / A股 `600519.SS` / 日股 `7203.T` / 韩股 `005930.KS` / 台股 `2330.TW` / 英股 `VOD.L`
- 不知道代码？按公司名搜：`GET https://api.datasink.ing/search?q=Apple`
- 每份报告是一个 `Document`，metadata 带 `symbol` / `report_period` / `doc_type`

API 文档：https://datasink.ing/docs
