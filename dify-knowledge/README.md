# Dify External Knowledge API

基于 [RAGAnything](https://github.com/your-repo/RAG-Anything) 实现的 Dify 外部知识库 API 服务。

## 功能特性

- ✅ 完整实现 Dify 外部知识库 API 规范
- ✅ 支持多模态文档处理（文本、图像、表格、公式）
- ✅ API 密钥认证
- ✅ 元数据过滤
- ✅ 可配置的检索参数
- ✅ 基于 RAGAnything 的强大文档解析能力

## 快速开始

### 1. 安装依赖

```bash
# 安装 dify-knowledge 依赖
cd dify-knowledge
pip install -r requirements.txt

# 安装 RAGAnything（如果还未安装）
cd ..
pip install -e .
```

### 2. 配置环境变量

复制示例配置文件并修改：

```bash
cp .env.example .env
```

编辑 `.env` 文件，配置必要的参数：

```env
# API密钥配置（多个密钥用逗号分隔）
API_KEYS=your-api-key-here

# LLM配置
LLM_MODEL=gpt-4o-mini
LLM_API_KEY=your-openai-api-key

# 向量模型配置
EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_API_KEY=your-openai-api-key
```

### 3. 启动服务

```bash
cd dify-knowledge
python app.py
```

服务将在 `http://0.0.0.0:8000` 启动。

## API 使用

### 检索端点

**端点:** `POST /retrieval`

**请求头:**
```
Authorization: Bearer <your-api-key>
Content-Type: application/json
```

**请求体:**
```json
{
    "knowledge_id": "default",
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
```

**响应:**
```json
{
    "records": [
        {
            "content": "Dify is an innovation engine for GenAI applications...",
            "score": 0.98,
            "title": "knowledge.txt",
            "metadata": {
                "knowledge_id": "default",
                "query": "What is Dify?"
            }
        }
    ]
}
```

### 健康检查

**端点:** `GET /health`

**响应:**
```json
{
    "status": "healthy",
    "service": "Dify External Knowledge API",
    "rag_initialized": true
}
```

## 在 Dify 中配置

1. 在 Dify 中创建知识库
2. 选择"连接外部知识库"
3. 填写以下信息：
   - **API Endpoint:** `http://your-server:8000/retrieval`
   - **API Key:** 在 `.env` 中配置的密钥
   - **Knowledge ID:** `default`（或您配置的知识库ID）

## 配置说明

### API 服务配置

- `HOST`: 服务监听地址（默认: `0.0.0.0`）
- `PORT`: 服务端口（默认: `8000`）
- `DEBUG`: 调试模式（默认: `false`）

### RAG 配置

- `WORKING_DIR`: RAG 存储目录（默认: `./rag_storage`）
- `PARSER`: 解析器选择，`mineru` 或 `docling`（默认: `mineru`）
- `PARSE_METHOD`: 解析方法，`auto`、`ocr` 或 `txt`（默认: `auto`）

### 多模态处理

- `ENABLE_IMAGE_PROCESSING`: 启用图像处理（默认: `true`）
- `ENABLE_TABLE_PROCESSING`: 启用表格处理（默认: `true`）
- `ENABLE_EQUATION_PROCESSING`: 启用公式处理（默认: `true`）

### 模型配置

- `LLM_MODEL`: LLM 模型名称（默认: `gpt-4o-mini`）
- `LLM_API_BASE`: LLM API 基础 URL
- `LLM_API_KEY`: LLM API 密钥

- `EMBEDDING_MODEL`: 嵌入模型名称（默认: `text-embedding-3-small`）
- `EMBEDDING_API_BASE`: 嵌入模型 API 基础 URL
- `EMBEDDING_API_KEY`: 嵌入模型 API 密钥

## 错误代码

| 错误代码 | 说明 |
|---------|------|
| 1001 | 无效的 Authorization 头格式 |
| 1002 | 授权失败 |
| 2001 | 知识库不存在 |
| 500 | 内部服务器错误 |

## 开发

### 项目结构

```
dify-knowledge/
├── app.py              # FastAPI 应用主文件
├── config.py           # 配置管理
├── models.py           # Pydantic 数据模型
├── rag_service.py      # RAG 服务封装
├── requirements.txt    # Python 依赖
├── .env.example        # 环境变量示例
└── README.md           # 本文档
```

### 运行测试

```bash
# 使用 curl 测试 API
curl -X POST http://localhost:8000/retrieval \
  -H "Authorization: Bearer your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "knowledge_id": "default",
    "query": "test query",
    "retrieval_setting": {
        "top_k": 5,
        "score_threshold": 0.5
    }
  }'
```

### 使用 Docker 部署

```bash
# 构建镜像
docker build -t dify-knowledge-api .

# 运行容器
docker run -d \
  -p 8000:8000 \
  -v $(pwd)/.env:/app/.env \
  -v $(pwd)/rag_storage:/app/rag_storage \
  --name dify-knowledge \
  dify-knowledge-api
```

## 许可证

本项目使用与 RAGAnything 相同的许可证。

## 贡献

欢迎提交 Issue 和 Pull Request！

## 相关链接

- [RAGAnything](https://github.com/your-repo/RAG-Anything)
- [Dify 官方文档](https://docs.dify.ai/)
- [Dify 外部知识库 API 文档](https://docs.dify.ai/en/use-dify/knowledge/external-knowledge-api)
