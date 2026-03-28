"""
build_vector_stores.py
======================
一键重建 Apple 10-K 财报的三个 FAISS 向量库:
  1. chunks_vector_store        — 正文切片 (1000 tokens, 200 overlap)
  2. chapter_summaries_vector_store — 章节摘要 (LLM 生成)
  3. book_quotes_vectorstore     — 核心财务指标句子

用法:
    python build_vector_stores.py
"""

import os
import shutil
from time import monotonic
from dotenv import load_dotenv

load_dotenv(override=True)
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
os.environ["OPENAI_BASE_URL"] = os.getenv("OPENAI_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.docstore.document import Document
from langchain.chains.summarize import load_summarize_chain
from langchain.prompts import PromptTemplate


class DashScopeEmbeddings(OpenAIEmbeddings):
    """兼容 DashScope 的 Embedding 包装类，避免发送 token 数组"""

    def embed_documents(self, texts, **kwargs):
        results = []
        batch_size = 6  # DashScope 限制 batch <= 10，留余量用 6
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            response = self.client.create(input=batch, model=self.model)
            results.extend([r.embedding for r in response.data])
        return results

    def embed_query(self, text):
        response = self.client.create(input=[text], model=self.model)
        return response.data[0].embedding

from helper_functions import (
    num_tokens_from_string,
    replace_t_with_space,
    replace_double_lines_with_one_line,
    split_into_chapters,
    extract_book_quotes_as_documents,
)

# ============================================================
# 配置
# ============================================================
PDF_PATH = "_10-K-2025-As-Filed.pdf"
MODEL_NAME = "qwen-max"
EMBEDDING_MODEL = "text-embedding-v3"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# ============================================================
# 1. 正文切片向量库
# ============================================================
def build_chunks_vector_store(pdf_path):
    print("\n[1/3] 正在构建正文切片向量库 (chunks_vector_store) ...")
    loader = PyPDFLoader(pdf_path)
    documents = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP, length_function=len
    )
    texts = text_splitter.split_documents(documents)
    texts = replace_t_with_space(texts)

    print(f"   切片数量: {len(texts)}")

    embeddings = DashScopeEmbeddings(model=EMBEDDING_MODEL)
    vectorstore = FAISS.from_documents(texts, embeddings)
    return vectorstore


# ============================================================
# 2. 章节摘要向量库
# ============================================================
summarization_prompt_template = """You are a financial analyst. Write a comprehensive summary of the following section from a 10-K annual filing.
Focus on key business metrics, strategic initiatives, risks, and financial performance mentioned in this section.

{text}

SUMMARY:"""

summarization_prompt = PromptTemplate(
    template=summarization_prompt_template, input_variables=["text"]
)


def create_chapter_summary(chapter):
    """为单个章节生成摘要"""
    chapter_txt = chapter.page_content
    llm = ChatOpenAI(temperature=0, model_name=MODEL_NAME)
    max_tokens = 16000

    num_tokens = num_tokens_from_string(chapter_txt, MODEL_NAME)
    print(f"   章节 {chapter.metadata.get('chapter', '?')} ({chapter.metadata.get('title', 'N/A')}): {num_tokens} tokens", end="")

    if num_tokens < max_tokens:
        chain = load_summarize_chain(llm, chain_type="stuff", prompt=summarization_prompt, verbose=False)
    else:
        chain = load_summarize_chain(llm, chain_type="map_reduce", map_prompt=summarization_prompt, combine_prompt=summarization_prompt, verbose=False)

    start = monotonic()
    doc_chapter = Document(page_content=chapter_txt)
    summary = chain.invoke([doc_chapter])
    summary_text = replace_double_lines_with_one_line(summary["output_text"])
    print(f" -> 完成 ({monotonic() - start:.1f}s)")

    return Document(page_content=summary_text, metadata=chapter.metadata)


def build_chapter_summaries_vector_store(pdf_path):
    print("\n[2/3] 正在构建章节摘要向量库 (chapter_summaries_vector_store) ...")
    chapters = split_into_chapters(pdf_path)
    chapters = replace_t_with_space(chapters)
    print(f"   检测到 {len(chapters)} 个章节")

    chapter_summaries = []
    for chapter in chapters:
        summary = create_chapter_summary(chapter)
        chapter_summaries.append(summary)

    embeddings = DashScopeEmbeddings(model=EMBEDDING_MODEL)
    vectorstore = FAISS.from_documents(chapter_summaries, embeddings)
    return vectorstore


# ============================================================
# 3. 核心财务指标向量库
# ============================================================
def build_financial_metrics_vector_store(pdf_path):
    print("\n[3/3] 正在构建核心财务指标向量库 (book_quotes_vectorstore) ...")
    loader = PyPDFLoader(pdf_path)
    documents = loader.load()
    documents = replace_t_with_space(documents)

    financial_quotes = extract_book_quotes_as_documents(documents)
    print(f"   提取到 {len(financial_quotes)} 条财务数据句子")

    embeddings = DashScopeEmbeddings(model=EMBEDDING_MODEL)
    vectorstore = FAISS.from_documents(financial_quotes, embeddings)
    return vectorstore


# ============================================================
# 主流程
# ============================================================
def main():
    print("=" * 60)
    print("  Apple 10-K 向量库构建工具")
    print("=" * 60)
    print(f"  PDF: {PDF_PATH}")
    print(f"  LLM: {MODEL_NAME}")
    print(f"  Embedding: {EMBEDDING_MODEL}")
    print("=" * 60)

    if not os.path.exists(PDF_PATH):
        print(f"\n[错误] 找不到 PDF 文件: {PDF_PATH}")
        print("请确保 _10-K-2025-As-Filed.pdf 位于项目根目录下。")
        return

    # 删除旧的向量库
    for store_dir in ["chunks_vector_store", "chapter_summaries_vector_store", "book_quotes_vectorstore"]:
        if os.path.exists(store_dir):
            shutil.rmtree(store_dir)
            print(f"   已删除旧的 {store_dir}")

    start_total = monotonic()

    # 构建三个向量库
    chunks_vs = build_chunks_vector_store(PDF_PATH)
    chunks_vs.save_local("chunks_vector_store")
    print("   -> 已保存 chunks_vector_store/")

    summaries_vs = build_chapter_summaries_vector_store(PDF_PATH)
    summaries_vs.save_local("chapter_summaries_vector_store")
    print("   -> 已保存 chapter_summaries_vector_store/")

    metrics_vs = build_financial_metrics_vector_store(PDF_PATH)
    metrics_vs.save_local("book_quotes_vectorstore")
    print("   -> 已保存 book_quotes_vectorstore/")

    total_time = monotonic() - start_total
    print(f"\n{'=' * 60}")
    print(f"  全部完成! 总耗时: {total_time:.1f}s")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
