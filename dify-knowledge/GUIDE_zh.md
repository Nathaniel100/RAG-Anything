# Dify 外部知识库 API 使用指南

## 目录

1. [快速开始](#快速开始)
2. [详细配置](#详细配置)
3. [导入文档到知识库](#导入文档到知识库)
4. [API 使用](#api-使用)
5. [与 Dify 集成](#与-dify-集成)
6. [常见问题](#常见问题)

## 快速开始

### 步骤 1: 安装依赖

```bash
# 进入 dify-knowledge 目录
cd dify-knowledge

# 安装服务依赖
pip install -r requirements.txt

# 安装 RAGAnything（如果还未安装）
cd ..
pip install -e .
```

### 步骤 2: 配置环境

```bash
# 复制环境变量示例文件
cd dify-knowledge
cp .env.example .env

# 使用文本编辑器编辑 .env 文件
notepad .env  # Windows
# 或
nano .env     # Linux/Mac
```

**必须配置的项目：**

```env
# API密钥（建议设置强密钥）
API_KEYS=your-secure-api-key-here

# OpenAI API配置
LLM_API_KEY=sk-xxx  # 你的OpenAI API密钥
EMBEDDING_API_KEY=sk-xxx  # 你的OpenAI API密钥（可以与LLM相同）
```

### 步骤 3: 初始化知识库（可选）

如果你有文档需要导入：

```bash
# 编辑 init_knowledge.py，添加文档路径
# 然后运行
python init_knowledge.py
```

### 步骤 4: 启动服务

```bash
# 使用快速启动脚本（推荐）
python start.py

# 或直接启动
python app.py
```

服务启动后，访问 http://localhost:8000/health 检查状态。

## 详细配置

### API 服务配置

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `HOST` | 服务监听地址 | `0.0.0.0` |
| `PORT` | 服务端口 | `8000` |
| `DEBUG` | 调试模式 | `false` |

### API 密钥配置

```env
# 单个密钥
API_KEYS=my-secret-key

# 多个密钥（用逗号分隔）
API_KEYS=key-for-team-a,key-for-team-b,key-for-dify
```

### RAG 配置

| 配置项 | 说明 | 可选值 | 默认值 |
|--------|------|--------|--------|
| `WORKING_DIR` | RAG存储目录 | 任意路径 | `./rag_storage` |
| `PARSER` | 文档解析器 | `mineru`, `docling` | `mineru` |
| `PARSE_METHOD` | 解析方法 | `auto`, `ocr`, `txt` | `auto` |

### 多模态处理配置

```env
# 启用图像处理
ENABLE_IMAGE_PROCESSING=true

# 启用表格处理
ENABLE_TABLE_PROCESSING=true

# 启用公式处理
ENABLE_EQUATION_PROCESSING=true
```

### LLM 模型配置

#### 使用 OpenAI

```env
LLM_MODEL=gpt-4o-mini
LLM_API_BASE=https://api.openai.com/v1
LLM_API_KEY=sk-xxx

EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_API_BASE=https://api.openai.com/v1
EMBEDDING_API_KEY=sk-xxx
```

#### 使用本地模型（如 LM Studio）

```env
LLM_MODEL=local-model
LLM_API_BASE=http://localhost:1234/v1
LLM_API_KEY=not-needed

EMBEDDING_MODEL=local-embedding
EMBEDDING_API_BASE=http://localhost:1234/v1
EMBEDDING_API_KEY=not-needed
```

#### 使用 Azure OpenAI

```env
LLM_MODEL=gpt-4
LLM_API_BASE=https://your-resource.openai.azure.com/
LLM_API_KEY=your-azure-key

EMBEDDING_MODEL=text-embedding-ada-002
EMBEDDING_API_BASE=https://your-resource.openai.azure.com/
EMBEDDING_API_KEY=your-azure-key
```

## 导入文档到知识库

### 方法 1: 使用初始化脚本

编辑 `init_knowledge.py`:

```python
documents = [
    "./docs/company_handbook.pdf",
    "./docs/product_guide.docx",
    "./docs/faq.md",
]
```

运行脚本：

```bash
python init_knowledge.py
```

### 方法 2: 使用 Python 代码

```python
import asyncio
from raganything import RAGAnything
from raganything.config import RAGAnythingConfig

async def import_documents():
    config = RAGAnythingConfig(working_dir="./rag_storage")
    rag = RAGAnything(config=config)
    await rag.initialize_rag()
    
    # 导入单个文件
    await rag.insert_file("path/to/document.pdf")
    
    # 批量导入
    files = ["doc1.pdf", "doc2.docx", "doc3.txt"]
    await rag.insert_files(files)

asyncio.run(import_documents())
```

### 支持的文件格式

- **文档**: PDF, DOCX, DOC, TXT, MD
- **表格**: XLSX, XLS, CSV
- **图像**: PNG, JPG, JPEG
- **演示文稿**: PPTX, PPT

## API 使用

### 1. 健康检查

```bash
curl http://localhost:8000/health
```

响应:
```json
{
    "status": "healthy",
    "service": "Dify External Knowledge API",
    "rag_initialized": true
}
```

### 2. 基本检索

```bash
curl -X POST http://localhost:8000/retrieval \
  -H "Authorization: Bearer your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "knowledge_id": "default",
    "query": "如何使用这个产品？",
    "retrieval_setting": {
        "top_k": 5,
        "score_threshold": 0.5
    }
  }'
```

### 3. 带元数据过滤的检索

```bash
curl -X POST http://localhost:8000/retrieval \
  -H "Authorization: Bearer your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "knowledge_id": "default",
    "query": "产品功能介绍",
    "retrieval_setting": {
        "top_k": 3,
        "score_threshold": 0.6
    },
    "metadata_condition": {
        "logical_operator": "and",
        "conditions": [
            {
                "name": ["category"],
                "comparison_operator": "contains",
                "value": "产品"
            }
        ]
    }
  }'
```

### 4. 使用 Python 测试

```bash
# 先安装 httpx
pip install httpx

# 运行测试脚本
python test_api.py
```

## 与 Dify 集成

### 步骤 1: 在 Dify 中创建知识库

1. 登录 Dify 平台
2. 进入"知识库"页面
3. 点击"创建知识库"

### 步骤 2: 配置外部知识库

1. 选择"连接外部知识库"
2. 填写以下信息：
   - **知识库名称**: 自定义名称
   - **API Endpoint**: `http://your-server-ip:8000/retrieval`
   - **API Key**: 你在 `.env` 中配置的 `API_KEYS`
   - **Knowledge ID**: `default`

### 步骤 3: 配置检索参数

- **Top K**: 建议 3-10
- **Score Threshold**: 建议 0.5-0.7

### 步骤 4: 测试连接

在 Dify 中点击"测试连接"，输入测试查询，查看返回结果。

### 步骤 5: 在应用中使用

将知识库添加到你的 Dify 应用中，开始使用！

## 常见问题

### Q1: 服务启动失败

**A**: 检查以下几点：
1. 是否正确配置了 `.env` 文件
2. 是否安装了所有依赖：`pip install -r requirements.txt`
3. 端口 8000 是否被占用：`netstat -ano | findstr 8000`（Windows）
4. 查看错误日志获取详细信息

### Q2: API 返回 403 错误

**A**: 这是认证失败，请检查：
1. 请求头中是否包含正确的 `Authorization: Bearer <api-key>`
2. API Key 是否在 `.env` 的 `API_KEYS` 中配置
3. API Key 格式是否正确（不要有多余的空格或引号）

### Q3: 检索结果为空

**A**: 可能的原因：
1. 知识库中没有导入文档
2. `score_threshold` 设置过高，降低到 0.3 试试
3. 查询与文档内容相关性太低

### Q4: 如何更换模型？

**A**: 编辑 `.env` 文件：

```env
# 使用 GPT-4
LLM_MODEL=gpt-4

# 使用本地模型
LLM_MODEL=local-model
LLM_API_BASE=http://localhost:1234/v1
```

然后重启服务。

### Q5: 如何部署到生产环境？

**A**: 推荐使用 Docker：

```bash
# 构建镜像
docker build -t dify-knowledge-api .

# 运行容器
docker-compose up -d
```

或使用 systemd 等进程管理工具。

### Q6: 支持多个知识库吗？

**A**: 当前版本默认使用单个知识库（`default`）。如需支持多个知识库，可以修改 `rag_service.py` 中的 `_load_knowledge_bases` 方法，为不同的 `knowledge_id` 配置不同的 `working_dir`。

### Q7: 如何备份知识库？

**A**: 直接备份 `WORKING_DIR` 指定的目录（默认 `./rag_storage`）：

```bash
# 创建备份
tar -czf rag_backup_$(date +%Y%m%d).tar.gz rag_storage/

# 恢复备份
tar -xzf rag_backup_20240115.tar.gz
```

### Q8: 性能优化建议

**A**: 
1. 使用更快的嵌入模型
2. 调整 `top_k` 和 `score_threshold` 参数
3. 增加服务器资源（CPU、内存）
4. 使用 Redis 等缓存系统（需自定义实现）

## 技术支持

遇到问题？
- 查看日志文件
- 访问 RAGAnything GitHub 仓库提 Issue
- 参考 Dify 官方文档

## 更新日志

### v1.0.0 (2024-01-14)
- ✅ 初始版本发布
- ✅ 完整实现 Dify 外部知识库 API
- ✅ 支持多模态文档处理
- ✅ API 密钥认证
- ✅ 元数据过滤功能
