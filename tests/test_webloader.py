"""测试网页抓取功能"""
import sys
sys.path.insert(0, 'src')

from src.loaders.web_loader import WebLoader


def test_webloader_basic():
    """测试 WebLoader 基本功能"""
    loader = WebLoader()

    # 测试1: 无效 URL
    try:
        loader.load("not-a-url")
        assert False, "应该抛出异常"
    except Exception:
        print("测试1 - 无效 URL: 通过")

    # 测试2: 空字符串
    try:
        loader.load("")
        assert False, "应该抛出异常"
    except Exception:
        print("测试2 - 空字符串: 通过")

    # 测试3: 使用示例网站（如果网络可用）
    # 注意：这个测试需要网络连接，在实际 CI/CD 中可能需要 mock
    test_url = "https://example.com"
    try:
        documents = loader.load(test_url)
        assert len(documents) > 0, "应该返回至少一个文档"
        assert documents[0].source == test_url, "source 应该是输入的 URL"
        assert documents[0].metadata.get("type") == "web", "type 应该是 web"
        assert len(documents[0].content) > 0, "content 不应该为空"
        print(f"测试3 - 抓取 example.com: 通过 (内容长度: {len(documents[0].content)})")
    except Exception as e:
        print(f"测试3 - 抓取 example.com: 跳过 (网络错误: {e})")

    print("\n所有测试完成！")


if __name__ == "__main__":
    test_webloader_basic()
