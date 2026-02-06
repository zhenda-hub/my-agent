#!/usr/bin/env python3
"""文档摄入脚本 - 加载文档、切片并存入向量数据库"""
import argparse
from pathlib import Path
from typing import List
from src.chunking.splitter import get_text_splitter
from src.loaders import get_loader
from src.loaders.base import Document
from src.vector_store import get_vector_store


def split_documents(documents: List[Document]) -> List[Document]:
    """
    切分文档

    Args:
        documents: 原始文档列表

    Returns:
        切分后的文档列表
    """
    chunked_docs = []

    for doc in documents:
        chunks = get_text_splitter().split_text(doc.content)

        for i, chunk in enumerate(chunks):
            chunked_doc = Document(
                content=chunk,
                metadata={
                    **doc.metadata,
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                },
                source=doc.source,
            )
            chunked_docs.append(chunked_doc)

    return chunked_docs


def ingest_file(file_path: str, vector_store, clear_source: bool = False):
    """
    摄入单个文件

    Args:
        file_path: 文件路径
        vector_store: 向量存储实例
        clear_source: 是否先清除该来源的旧数据
    """
    path = Path(file_path)

    if not path.exists():
        print(f"❌ 文件不存在: {file_path}")
        return

    print(f"📄 正在处理: {path.name}")

    # 获取加载器
    loader = get_loader(str(path))

    # 加载文档
    documents = loader.load(str(path))
    print(f"   加载了 {len(documents)} 个文档段")

    # 切分文档
    chunked_docs = split_documents(documents)
    print(f"   切分为 {len(chunked_docs)} 个块")

    # 清除旧数据（如果需要）
    if clear_source:
        vector_store.delete_by_source(str(path))

    # 添加到向量存储
    vector_store.add_documents(chunked_docs)
    print(f"   ✅ 已添加到向量数据库")


def ingest_directory(
    directory: str,
    vector_store,
    recursive: bool = True,
    clear: bool = False,
):
    """
    摄入目录中的所有支持的文档

    Args:
        directory: 目录路径
        vector_store: 向量存储实例
        recursive: 是否递归处理子目录
        clear: 是否先清空数据库
    """
    dir_path = Path(directory)

    if not dir_path.exists() or not dir_path.is_dir():
        print(f"❌ 目录不存在: {directory}")
        return

    if clear:
        print("🗑️  清空向量数据库...")
        vector_store.clear()

    # 支持的文件扩展名
    extensions = [".pdf", ".docx", ".doc", ".md", ".markdown"]

    # 查找文件
    if recursive:
        files = [
            f for ext in extensions
            for f in dir_path.rglob(f"*{ext}")
        ]
    else:
        files = [
            f for ext in extensions
            for f in dir_path.glob(f"*{ext}")
        ]

    if not files:
        print(f"⚠️  在 {directory} 中未找到支持的文档文件")
        return

    print(f"📁 找到 {len(files)} 个文档文件\n")

    for file_path in sorted(files):
        ingest_file(str(file_path), vector_store)

    print(f"\n✨ 摄入完成！共处理 {len(files)} 个文件")


def main():
    parser = argparse.ArgumentParser(description="文档摄入脚本")
    parser.add_argument(
        "--path",
        type=str,
        default=str(config.DOCUMENTS_DIR),
        help="文件或目录路径（默认: data/documents）",
    )
    parser.add_argument(
        "--recursive",
        action="store_true",
        default=True,
        help="递归处理子目录",
    )
    parser.add_argument(
        "--clear",
        action="store_true",
        help="清空向量数据库后重新摄入",
    )

    args = parser.parse_args()

    # 获取向量存储
    vector_store = get_vector_store()

    path = Path(args.path)

    if path.is_file():
        # 处理单个文件
        ingest_file(str(path), vector_store, clear_source=args.clear)
    elif path.is_dir():
        # 处理目录
        ingest_directory(str(path), vector_store, args.recursive, args.clear)
    else:
        print(f"❌ 路径不存在: {args.path}")


if __name__ == "__main__":
    main()
