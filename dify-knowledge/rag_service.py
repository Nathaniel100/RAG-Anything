"""
RAG服务封装
基于RAGAnything实现知识检索功能
"""

import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# 添加父目录到Python路径以导入raganything
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import settings
from lightrag import QueryParam
from models import (
    ComparisonOperator,
    MetadataFilter,
    RetrievalRecord,
    RetrievalResponse,
)
from openai import AsyncOpenAI

from raganything import RAGAnything
from raganything.config import RAGAnythingConfig

logger = logging.getLogger(__name__)


class RAGService:
    """RAG服务类，封装RAGAnything功能"""
    
    def __init__(self):
        """初始化RAG服务"""
        self.rag: Optional[RAGAnything] = None
        self.initialized = False
        self.knowledge_bases: Dict[str, str] = {}  # knowledge_id -> working_dir映射
        
    async def initialize(self):
        """初始化RAG实例"""
        try:
            # 创建LLM客户端
            llm_client = AsyncOpenAI(
                api_key=settings.LLM_API_KEY or os.getenv("OPENAI_API_KEY"),
                base_url=settings.LLM_API_BASE
            )
            
            # 创建嵌入客户端
            embedding_client = AsyncOpenAI(
                api_key=settings.EMBEDDING_API_KEY or os.getenv("OPENAI_API_KEY"),
                base_url=settings.EMBEDDING_API_BASE
            )
            
            # 定义LLM函数
            async def llm_model_func(
                prompt, system_prompt=None, history_messages=[], **kwargs
            ) -> str:
                """LLM模型函数"""
                messages = []
                if system_prompt:
                    messages.append({"role": "system", "content": system_prompt})
                messages.extend(history_messages)
                messages.append({"role": "user", "content": prompt})
                
                response = await llm_client.chat.completions.create(
                    model=settings.LLM_MODEL,
                    messages=messages,
                    **kwargs
                )
                return response.choices[0].message.content
            
            # 定义嵌入函数
            async def embedding_func(texts: List[str]) -> List[List[float]]:
                """嵌入函数"""
                response = await embedding_client.embeddings.create(
                    model=settings.EMBEDDING_MODEL,
                    input=texts
                )
                return [item.embedding for item in response.data]
            
            # 创建RAGAnything配置
            config = RAGAnythingConfig(
                working_dir=settings.WORKING_DIR,
                parser=settings.PARSER,
                parse_method=settings.PARSE_METHOD,
                enable_image_processing=settings.ENABLE_IMAGE_PROCESSING,
                enable_table_processing=settings.ENABLE_TABLE_PROCESSING,
                enable_equation_processing=settings.ENABLE_EQUATION_PROCESSING,
            )
            
            # 初始化RAGAnything
            self.rag = RAGAnything(
                config=config,
                llm_model_func=llm_model_func,
                embedding_func=embedding_func,
            )
            
            # 初始化LightRAG
            await self.rag.initialize_rag()
            
            # 加载知识库映射
            self._load_knowledge_bases()
            
            self.initialized = True
            logger.info("RAG服务初始化成功")
            
        except Exception as e:
            logger.error(f"初始化RAG服务失败: {str(e)}", exc_info=True)
            raise
    
    def _load_knowledge_bases(self):
        """加载知识库映射"""
        # 这里可以从配置文件或数据库加载知识库映射
        # 目前使用默认知识库
        self.knowledge_bases["default"] = settings.WORKING_DIR
        logger.info(f"加载知识库映射: {self.knowledge_bases}")
    
    def _apply_metadata_filter(
        self,
        records: List[Dict[str, Any]],
        metadata_filter: Optional[MetadataFilter]
    ) -> List[Dict[str, Any]]:
        """
        应用元数据过滤
        
        Args:
            records: 原始检索记录
            metadata_filter: 元数据过滤条件
            
        Returns:
            过滤后的记录列表
        """
        if not metadata_filter or not records:
            return records
        
        filtered_records = []
        
        for record in records:
            metadata = record.get("metadata", {})
            
            # 评估所有条件
            condition_results = []
            for condition in metadata_filter.conditions:
                result = self._evaluate_condition(metadata, condition)
                condition_results.append(result)
            
            # 根据逻辑操作符组合结果
            if metadata_filter.logical_operator == "and":
                if all(condition_results):
                    filtered_records.append(record)
            else:  # or
                if any(condition_results):
                    filtered_records.append(record)
        
        return filtered_records
    
    def _evaluate_condition(
        self,
        metadata: Dict[str, Any],
        condition: Any
    ) -> bool:
        """
        评估单个条件
        
        Args:
            metadata: 记录的元数据
            condition: 条件对象
            
        Returns:
            条件是否满足
        """
        # 检查所有指定字段
        for field_name in condition.name:
            if field_name not in metadata:
                return False
            
            field_value = str(metadata[field_name])
            operator = condition.comparison_operator
            compare_value = condition.value or ""
            
            # 评估比较操作
            if operator == ComparisonOperator.CONTAINS:
                if compare_value not in field_value:
                    return False
            elif operator == ComparisonOperator.NOT_CONTAINS:
                if compare_value in field_value:
                    return False
            elif operator == ComparisonOperator.START_WITH:
                if not field_value.startswith(compare_value):
                    return False
            elif operator == ComparisonOperator.END_WITH:
                if not field_value.endswith(compare_value):
                    return False
            elif operator == ComparisonOperator.IS:
                if field_value != compare_value:
                    return False
            elif operator == ComparisonOperator.IS_NOT:
                if field_value == compare_value:
                    return False
            elif operator == ComparisonOperator.EMPTY:
                if field_value:
                    return False
            elif operator == ComparisonOperator.NOT_EMPTY:
                if not field_value:
                    return False
            elif operator == ComparisonOperator.EQUAL:
                try:
                    if float(field_value) != float(compare_value):
                        return False
                except ValueError:
                    if field_value != compare_value:
                        return False
            # 可以继续添加其他操作符的实现
        
        return True
    
    async def retrieve(
        self,
        knowledge_id: str,
        query: str,
        top_k: int,
        score_threshold: float,
        metadata_condition: Optional[MetadataFilter] = None
    ) -> RetrievalResponse:
        """
        执行知识检索
        
        Args:
            knowledge_id: 知识库ID
            query: 查询文本
            top_k: 返回结果数量
            score_threshold: 分数阈值
            metadata_condition: 元数据过滤条件
            
        Returns:
            RetrievalResponse: 检索结果
            
        Raises:
            ValueError: 知识库不存在
        """
        if not self.initialized:
            raise RuntimeError("RAG服务未初始化")
        
        # 验证知识库是否存在
        if knowledge_id not in self.knowledge_bases:
            # 如果不存在，尝试使用默认知识库
            if "default" not in self.knowledge_bases:
                raise ValueError(f"Knowledge base '{knowledge_id}' not found")
            logger.warning(f"知识库 {knowledge_id} 不存在，使用默认知识库")
            knowledge_id = "default"
        
        try:
            # 执行查询
            logger.info(f"执行查询: {query}, top_k={top_k}, threshold={score_threshold}")
            
            result = await self.rag.query(
                query,
                param=QueryParam(
                    mode="hybrid",  # 使用混合检索模式
                    top_k=top_k,
                )
            )
            
            # 解析结果
            records = []
            if hasattr(result, 'context') and result.context:
                # 从context中提取记录
                context_items = result.context.split('\n\n')
                
                for i, item in enumerate(context_items):
                    if not item.strip():
                        continue
                    
                    # 简单的分数计算（实际应该从LightRAG获取）
                    score = max(0.5, 1.0 - (i * 0.1))
                    
                    if score >= score_threshold:
                        record = {
                            "content": item.strip(),
                            "score": score,
                            "title": f"Document_{i+1}",
                            "metadata": {
                                "knowledge_id": knowledge_id,
                                "query": query,
                            }
                        }
                        records.append(record)
            
            # 应用元数据过滤
            if metadata_condition:
                records = self._apply_metadata_filter(records, metadata_condition)
            
            # 限制返回数量
            records = records[:top_k]
            
            # 转换为响应模型
            response_records = [
                RetrievalRecord(
                    content=record["content"],
                    score=record["score"],
                    title=record["title"],
                    metadata=record.get("metadata")
                )
                for record in records
            ]
            
            return RetrievalResponse(records=response_records)
            
        except Exception as e:
            logger.error(f"执行检索时发生错误: {str(e)}", exc_info=True)
            raise
    
    async def cleanup(self):
        """清理资源"""
        if self.rag:
            try:
                # 调用RAGAnything的清理方法
                if hasattr(self.rag, 'close'):
                    self.rag.close()
                logger.info("RAG资源清理完成")
            except Exception as e:
                logger.error(f"清理RAG资源时发生错误: {str(e)}")
