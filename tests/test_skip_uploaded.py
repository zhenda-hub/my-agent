"""测试跳过已上传文件功能"""
import sys
sys.path.insert(0, 'src')

from src.vector_store import VectorStore
from src.loaders.base import Document


def test_source_exists():
    """测试 source_exists 方法"""
    vs = VectorStore()

    # 测试1: 检查不存在的文档
    result = vs.source_exists("/fake/path/test.pdf")
    print(f"测试1 - 不存在的文档: {result} (应该为 False)")
    assert result == False, "不存在的文档应该返回 False"

    # 测试2: 添加测试文档后再检查
    test_doc = Document(
        content="测试内容",
        metadata={"test": True},
        source="/test/path/skip_test.pdf"
    )

    vs.add_documents([test_doc], chunk_ids=["skip_test_0"])

    result = vs.source_exists("/test/path/skip_test.pdf")
    print(f"测试2 - 存在的文档: {result} (应该为 True)")
    assert result == True, "存在的文档应该返回 True"

    # 清理测试数据
    vs.delete_by_source("/test/path/skip_test.pdf")
    result = vs.source_exists("/test/path/skip_test.pdf")
    print(f"测试3 - 清理后: {result} (应该为 False)")
    assert result == False, "清理后应该返回 False"

    print("\n所有测试通过！")


if __name__ == "__main__":
    test_source_exists()
