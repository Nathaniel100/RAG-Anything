"""
Dify External Knowledge API数据模型
定义请求和响应的Pydantic模型
"""

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class LogicalOperator(str, Enum):
    """逻辑操作符"""
    AND = "and"
    OR = "or"


class ComparisonOperator(str, Enum):
    """比较操作符"""
    CONTAINS = "contains"
    NOT_CONTAINS = "not contains"
    START_WITH = "start with"
    END_WITH = "end with"
    IS = "is"
    IS_NOT = "is not"
    EMPTY = "empty"
    NOT_EMPTY = "not empty"
    EQUAL = "="
    NOT_EQUAL = "≠"
    GREATER_THAN = ">"
    LESS_THAN = "<"
    GREATER_EQUAL = "≥"
    LESS_EQUAL = "≤"
    BEFORE = "before"
    AFTER = "after"


class MetadataCondition(BaseModel):
    """元数据条件"""
    name: List[str] = Field(..., description="要过滤的元数据字段名列表")
    comparison_operator: ComparisonOperator = Field(..., description="比较操作符")
    value: Optional[str] = Field(None, description="比较值")


class MetadataFilter(BaseModel):
    """元数据过滤器"""
    logical_operator: LogicalOperator = Field(
        default=LogicalOperator.AND,
        description="逻辑操作符，可以是and或or，默认为and"
    )
    conditions: List[MetadataCondition] = Field(..., description="条件列表")


class RetrievalSetting(BaseModel):
    """检索设置"""
    top_k: int = Field(..., description="最大检索结果数量", ge=1, le=100)
    score_threshold: float = Field(
        ...,
        description="结果与查询的相关性分数限制，范围：0~1",
        ge=0.0,
        le=1.0
    )


class RetrievalRequest(BaseModel):
    """检索请求模型"""
    knowledge_id: str = Field(..., description="知识库唯一ID")
    query: str = Field(..., description="用户查询")
    retrieval_setting: RetrievalSetting = Field(..., description="检索参数")
    metadata_condition: Optional[MetadataFilter] = Field(
        None,
        description="元数据过滤条件"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "knowledge_id": "AAA-BBB-CCC",
                "query": "What is Dify?",
                "retrieval_setting": {
                    "top_k": 5,
                    "score_threshold": 0.5
                },
                "metadata_condition": {
                    "logical_operator": "and",
                    "conditions": [
                        {
                            "name": ["category"],
                            "comparison_operator": "contains",
                            "value": "AI"
                        }
                    ]
                }
            }
        }


class RetrievalRecord(BaseModel):
    """检索记录"""
    content: str = Field(..., description="数据源中的文本块")
    score: float = Field(..., description="结果与查询的相关性分数，范围：0~1")
    title: str = Field(..., description="文档标题")
    metadata: Optional[Dict[str, Any]] = Field(
        None,
        description="包含文档的元数据属性及其值"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "content": "Dify: The Innovation Engine for GenAI Applications",
                "score": 0.98,
                "title": "knowledge.txt",
                "metadata": {
                    "path": "s3://dify/knowledge.txt",
                    "description": "dify knowledge document"
                }
            }
        }


class RetrievalResponse(BaseModel):
    """检索响应模型"""
    records: List[RetrievalRecord] = Field(..., description="查询知识库的记录列表")

    class Config:
        json_schema_extra = {
            "example": {
                "records": [
                    {
                        "metadata": {
                            "path": "s3://dify/knowledge.txt",
                            "description": "dify knowledge document"
                        },
                        "score": 0.98,
                        "title": "knowledge.txt",
                        "content": "This is the document for external knowledge."
                    },
                    {
                        "metadata": {
                            "path": "s3://dify/introduce.txt",
                            "description": "dify introduce"
                        },
                        "score": 0.66,
                        "title": "introduce.txt",
                        "content": "The Innovation Engine for GenAI Applications"
                    }
                ]
            }
        }


class ErrorResponse(BaseModel):
    """错误响应模型"""
    error_code: int = Field(..., description="错误代码")
    error_msg: str = Field(..., description="API异常描述")

    class Config:
        json_schema_extra = {
            "example": {
                "error_code": 1001,
                "error_msg": "Invalid Authorization header format. Expected 'Bearer <api-key>' format."
            }
        }
