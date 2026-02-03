"""测试 BaseLoader 的公共功能"""
import pytest
from pathlib import Path
from src.loaders.base import BaseLoader


class TestBaseLoaderValidation:
    """测试 BaseLoader 的文件验证功能"""

    def test_validate_file_path_with_existing_file(self, tmp_path):
        """测试验证存在的文件"""
        test_file = tmp_path / "test.txt"
        test_file.write_text("content", encoding="utf-8")

        # 应该不抛出异常
        result = BaseLoader.validate_file_path(str(test_file))
        assert result == test_file

    def test_validate_file_path_with_nonexistent_file(self):
        """测试验证不存在的文件"""
        with pytest.raises(FileNotFoundError, match="File not found"):
            BaseLoader.validate_file_path("/nonexistent/file.txt")

    def test_validate_file_path_with_custom_error_type(self, tmp_path):
        """测试自定义文件类型错误消息"""
        test_file = tmp_path / "test.pdf"

        with pytest.raises(FileNotFoundError, match="PDF file not found"):
            BaseLoader.validate_file_path(str(test_file), file_type="PDF")

    def test_validate_file_path_returns_path_object(self, tmp_path):
        """测试验证方法返回 Path 对象"""
        test_file = tmp_path / "test.txt"
        test_file.write_text("content", encoding="utf-8")

        result = BaseLoader.validate_file_path(str(test_file))
        assert isinstance(result, Path)
        assert result.exists()
