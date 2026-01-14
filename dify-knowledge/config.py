"""
配置模块
基于环境变量的配置管理
"""

import os
from typing import List, Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置"""
    
    # API服务配置
    HOST: str = Field(default="0.0.0.0", description="服务监听地址")
    PORT: int = Field(default=8000, description="服务端口")
    DEBUG: bool = Field(default=False, description="调试模式")
    
    # API密钥配置
    API_KEYS: str = Field(default="", description="有效的API密钥，逗号分隔")
    
    # RAG配置
    WORKING_DIR: str = Field(default="./rag_storage", description="RAG存储目录")
    PARSER: str = Field(default="mineru", description="解析器选择: mineru 或 docling")
    PARSE_METHOD: str = Field(default="auto", description="解析方法: auto, ocr, 或 txt")
    
    # 多模态处理配置
    ENABLE_IMAGE_PROCESSING: bool = Field(default=True, description="启用图像处理")
    ENABLE_TABLE_PROCESSING: bool = Field(default=True, description="启用表格处理")
    ENABLE_EQUATION_PROCESSING: bool = Field(default=True, description="启用公式处理")
    
    # LLM配置
    LLM_MODEL: str = Field(default="gpt-4o-mini", description="LLM模型名称")
    LLM_API_BASE: Optional[str] = Field(default=None, description="LLM API基础URL")
    LLM_API_KEY: Optional[str] = Field(default=None, description="LLM API密钥")
    
    # 向量模型配置
    EMBEDDING_MODEL: str = Field(default="text-embedding-3-small", description="嵌入模型名称")
    EMBEDDING_API_BASE: Optional[str] = Field(default=None, description="嵌入模型API基础URL")
    EMBEDDING_API_KEY: Optional[str] = Field(default=None, description="嵌入模型API密钥")
    
    # 检索配置
    DEFAULT_TOP_K: int = Field(default=5, description="默认返回结果数量")
    DEFAULT_SCORE_THRESHOLD: float = Field(default=0.5, description="默认相关性分数阈值")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
    
    @property
    def VALID_API_KEYS(self) -> List[str]:
        """解析并返回有效的API密钥列表"""
        if not self.API_KEYS:
            return []
        return [key.strip() for key in self.API_KEYS.split(",") if key.strip()]


# 创建全局配置实例
settings = Settings()
