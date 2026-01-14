"""
Dify External Knowledge API
基于RAGAnything实现的Dify外部知识库API服务
"""

__version__ = "1.0.0"
__author__ = "RAGAnything Team"
__description__ = "Dify External Knowledge API based on RAGAnything"

from .config import settings
from .models import (
    ErrorResponse,
    MetadataCondition,
    MetadataFilter,
    RetrievalRecord,
    RetrievalRequest,
    RetrievalResponse,
    RetrievalSetting,
)
from .rag_service import RAGService

__all__ = [
    "settings",
    "RetrievalRequest",
    "RetrievalResponse",
    "RetrievalRecord",
    "RetrievalSetting",
    "MetadataFilter",
    "MetadataCondition",
    "ErrorResponse",
    "RAGService",
]
