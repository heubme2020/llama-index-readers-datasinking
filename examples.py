"""llama-index-readers-datasinking 示例：3 个例子。

跑法：
    pip install git+https://github.com/heubme2020/llama-index-readers-datasinking
    pip install llama-index-core
    python examples.py

⚠️ 不填 key 走公共额度（约 3 秒/篇、7 天 31 篇）。跑多份建议设环境变量：
    export DATASINKING_API_KEY=你的免费key
"""
import os

from llama_index.readers.datasinking import DataSinkingReader

reader = DataSinkingReader(os.environ.get("DATASINKING_API_KEY", ""))


def example1():
    """例 1：拉一份财报，看 Document 长什么样。"""
    print("=" * 66)
    print("例 1：苹果最新一份 10-Q → Document")
    docs = reader.load_data("AAPL", limit=1)
    d = docs[0]
    print("metadata:", d.metadata)
    print("正文前 160 字:", d.text[:160].replace("\n", " "))


def example2():
    """例 2：把一家公司近 5 年财报全灌进来，拼成一个财报语料库。"""
    print("\n" + "=" * 66)
    print("例 2：苹果近 5 份财报 → 5 个 Document")
    docs = reader.load_data("AAPL", limit=5)
    for d in docs:
        print(f"  {d.metadata['report_period']} · {d.metadata['doc_type']} · {len(d.text):,} 字")
    total = sum(len(d.text) for d in docs)
    print(f"  合计 {total:,} 字，可直接喂给 VectorStoreIndex.from_documents(docs)")


def example3():
    """例 3：两家公司财报 → 关键词对比（不靠向量，先看能不能搜到指标）。"""
    print("\n" + "=" * 66)
    print("例 3：茅台 vs 五粮液，搜「营业收入」")
    for sym, name in [("600519.SS", "茅台"), ("000858.SZ", "五粮液")]:
        docs = reader.load_data(sym, limit=1)
        found = None
        for line in docs[0].text.splitlines():
            if "营业收入" in line and any(ch.isdigit() for ch in line):
                found = line.strip()
                break
        print(f"  {name}（{sym}）:", found or "（未命中）")


if __name__ == "__main__":
    example1()
    example2()
    example3()
