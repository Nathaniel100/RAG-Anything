"""
Dify External Knowledge API Server
基于RAGAnything实现的Dify外部知识库API服务
"""

import logging
from contextlib import asynccontextmanager
from typing import Optional

import uvicorn
from config import settings
from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.responses import JSONResponse
from models import ErrorResponse, RetrievalRequest, RetrievalResponse
from rag_service import RAGService

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 全局RAG服务实例
rag_service: Optional[RAGService] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    global rag_service
    
    # 启动时初始化RAG服务
    logger.info("初始化RAG服务...")
    rag_service = RAGService()
    await rag_service.initialize()
    logger.info("RAG服务初始化完成")
    
    yield
    
    # 关闭时清理资源
    logger.info("清理RAG服务...")
    if rag_service:
        await rag_service.cleanup()
    logger.info("RAG服务清理完成")


app = FastAPI(
    title="Dify External Knowledge API",
    description="基于RAGAnything实现的Dify外部知识库API",
    version="1.0.0",
    lifespan=lifespan
)


def verify_api_key(authorization: Optional[str]) -> bool:
    """
    验证API密钥
    
    Args:
        authorization: Authorization头部值
        
    Returns:
        bool: 验证是否通过
    """
    if not authorization:
        return False
    
    # 检查格式: Bearer <api-key>
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return False
    
    api_key = parts[1]
    
    # 验证API密钥
    if settings.VALID_API_KEYS:
        return api_key in settings.VALID_API_KEYS
    
    # 如果没有配置密钥，则跳过验证（开发模式）
    logger.warning("未配置有效的API密钥，跳过验证")
    return True


@app.post("/retrieval", response_model=RetrievalResponse)
async def retrieval(
    request: RetrievalRequest,
    authorization: Optional[str] = Header(None)
):
    """
    知识库检索端点
    
    Args:
        request: 检索请求
        authorization: Authorization头部
        
    Returns:
        RetrievalResponse: 检索结果
        
    Raises:
        HTTPException: 验证失败或处理错误
    """
    # 验证API密钥
    if not verify_api_key(authorization):
        raise HTTPException(
            status_code=403,
            detail={
                "error_code": 1001,
                "error_msg": "Invalid Authorization header format. Expected 'Bearer <api-key>' format."
            }
        )
    
    try:
        # 执行检索
        logger.info(f"处理检索请求 - knowledge_id: {request.knowledge_id}, query: {request.query}")
        
        response = await rag_service.retrieve(
            knowledge_id=request.knowledge_id,
            query=request.query,
            top_k=request.retrieval_setting.top_k,
            score_threshold=request.retrieval_setting.score_threshold,
            metadata_condition=request.metadata_condition
        )
        
        logger.info(f"检索完成，返回 {len(response.records)} 条结果")
        return response
        
    except ValueError as e:
        logger.error(f"知识库不存在: {str(e)}")
        raise HTTPException(
            status_code=404,
            detail={
                "error_code": 2001,
                "error_msg": f"The knowledge does not exist: {str(e)}"
            }
        )
    except Exception as e:
        logger.error(f"处理检索请求时发生错误: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error_code": 500,
                "error_msg": f"Internal server error: {str(e)}"
            }
        )


@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "service": "Dify External Knowledge API",
        "rag_initialized": rag_service is not None and rag_service.initialized
    }


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """统一的HTTP异常处理"""
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.detail
    )


if __name__ == "__main__":
    # 启动服务
    uvicorn.run(
        "app:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
