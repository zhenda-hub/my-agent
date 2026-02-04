"""测试 Embeddings 嵌入模块"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import numpy as np
from src.embeddings import Embeddings, get_embeddings


class TestEmbeddings:
    """测试 Embeddings 类"""

    @patch('src.embeddings.SentenceTransformer')
    def test_embed_documents_batch(self, mock_transformer_class):
        """测试批量文档嵌入"""
        # Mock 模型
        mock_model = Mock()
        mock_model.get_sentence_embedding_dimension.return_value = 384
        mock_model.encode.return_value = np.array([[0.1, 0.2], [0.3, 0.4]])
        mock_transformer_class.return_value = mock_model

        embeddings = Embeddings()
        result = embeddings.embed_documents(["doc1", "doc2"])

        assert len(result) == 2
        assert result[0] == [0.1, 0.2]
        assert result[1] == [0.3, 0.4]
        mock_model.encode.assert_called_once()

    @patch('src.embeddings.SentenceTransformer')
    def test_embed_query(self, mock_transformer_class):
        """测试查询嵌入"""
        mock_model = Mock()
        mock_model.get_sentence_embedding_dimension.return_value = 384
        mock_model.encode.return_value = np.array([0.5, 0.6])
        mock_transformer_class.return_value = mock_model

        embeddings = Embeddings()
        result = embeddings.embed_query("test query")

        assert result == [0.5, 0.6]
        mock_model.encode.assert_called_once()

    @patch('src.embeddings.SentenceTransformer')
    def test_get_dimension(self, mock_transformer_class):
        """测试获取维度"""
        mock_model = Mock()
        mock_model.get_sentence_embedding_dimension.return_value = 768
        mock_transformer_class.return_value = mock_model

        embeddings = Embeddings()
        result = embeddings.get_dimension()

        assert result == 768

    @patch('src.embeddings.SentenceTransformer')
    def test_lazy_model_loading(self, mock_transformer_class):
        """测试延迟加载模型"""
        mock_model = Mock()
        mock_model.get_sentence_embedding_dimension.return_value = 384
        mock_transformer_class.return_value = mock_model

        embeddings = Embeddings()

        # 模型应该还没加载
        assert embeddings._model is None

        # 访问 model 属性应该触发加载
        _ = embeddings.model
        assert embeddings._model is not None
        mock_transformer_class.assert_called_once()

    @patch('src.embeddings.SentenceTransformer')
    def test_model_custom_device(self, mock_transformer_class):
        """测试自定义设备"""
        mock_model = Mock()
        mock_model.get_sentence_embedding_dimension.return_value = 384
        mock_transformer_class.return_value = mock_model

        embeddings = Embeddings(device="cuda")
        _ = embeddings.model

        # 验证使用了正确的设备
        mock_transformer_class.assert_called_once()
        call_kwargs = mock_transformer_class.call_args[1]
        assert call_kwargs["device"] == "cuda"

    @patch('src.embeddings.SentenceTransformer')
    def test_model_custom_name(self, mock_transformer_class):
        """测试自定义模型名称"""
        mock_model = Mock()
        mock_model.get_sentence_embedding_dimension.return_value = 384
        mock_transformer_class.return_value = mock_model

        embeddings = Embeddings(model_name="custom-model")
        _ = embeddings.model

        # 验证使用了正确的模型名称
        mock_transformer_class.assert_called_once_with("custom-model", device="cpu")

    def test_embeddings_singleton(self):
        """测试全局单例模式"""
        with patch('src.embeddings.SentenceTransformer'):
            # 清除全局实例
            import src.embeddings
            src.embeddings._embeddings_instance = None

            instance1 = get_embeddings()
            instance2 = get_embeddings()

            assert instance1 is instance2


class TestGetEmbeddings:
    """测试 get_embeddings 全局函数"""

    @patch('src.embeddings.SentenceTransformer')
    def test_get_embeddings_returns_instance(self, mock_transformer_class):
        """测试返回 Embeddings 实例"""
        mock_model = Mock()
        mock_model.get_sentence_embedding_dimension.return_value = 384
        mock_transformer_class.return_value = mock_model

        # 清除全局实例
        import src.embeddings
        src.embeddings._embeddings_instance = None

        result = get_embeddings()

        assert isinstance(result, Embeddings)
