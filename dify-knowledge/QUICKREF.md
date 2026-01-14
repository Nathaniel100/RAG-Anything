# 快速参考卡片 - Dify External Knowledge API

## 📦 安装

```bash
cd dify-knowledge
pip install -r requirements.txt
cd .. && pip install -e .
```

## ⚙️ 配置

```bash
cp .env.example .env
# 编辑 .env 文件，设置 API_KEYS 和 LLM 配置
```

## 🚀 启动

```bash
# 方法 1: 快速启动（推荐）
python start.py

# 方法 2: 直接启动
python app.py

# 方法 3: Docker
docker-compose up -d
```

## 🧪 测试

```bash
# 健康检查
curl http://localhost:8000/health

# 运行测试脚本
python test_api.py
```

## 📝 API 快速示例

### 基本检索
```bash
curl -X POST http://localhost:8000/retrieval \
  -H "Authorization: Bearer your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "knowledge_id": "default",
    "query": "What is RAG?",
    "retrieval_setting": {
      "top_k": 5,
      "score_threshold": 0.5
    }
  }'
```

### Python 示例
```python
import httpx

async def query_knowledge():
    response = await httpx.post(
        "http://localhost:8000/retrieval",
        headers={"Authorization": "Bearer your-api-key"},
        json={
            "knowledge_id": "default",
            "query": "What is RAG?",
            "retrieval_setting": {
                "top_k": 5,
                "score_threshold": 0.5
            }
        }
    )
    return response.json()
```

## 🔗 Dify 集成

1. **创建知识库** → 选择"外部知识库"
2. **填写配置**:
   - Endpoint: `http://your-server:8000/retrieval`
   - API Key: 你的 API 密钥
   - Knowledge ID: `default`
3. **测试连接** → 完成！

## 📂 项目结构

```
dify-knowledge/
├── app.py              # FastAPI 主应用
├── rag_service.py      # RAG 服务封装
├── models.py           # 数据模型
├── config.py           # 配置管理
├── requirements.txt    # 依赖列表
├── .env.example        # 配置示例
├── test_api.py         # 测试脚本
├── init_knowledge.py   # 初始化脚本
├── start.py            # 启动脚本
├── README.md           # 英文文档
├── GUIDE_zh.md         # 中文指南
└── ARCHITECTURE.md     # 架构说明
```

## 🔧 常用命令

```bash
# 查看日志
tail -f logs/app.log

# 重启服务
docker-compose restart

# 查看端口占用
netstat -ano | findstr 8000  # Windows
lsof -i :8000                # Linux/Mac

# 测试 API
python test_api.py
```

## 📊 环境变量速查

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `API_KEYS` | API密钥（逗号分隔） | - |
| `HOST` | 监听地址 | `0.0.0.0` |
| `PORT` | 端口号 | `8000` |
| `LLM_MODEL` | LLM模型 | `gpt-4o-mini` |
| `LLM_API_KEY` | LLM密钥 | - |
| `EMBEDDING_MODEL` | 嵌入模型 | `text-embedding-3-small` |
| `WORKING_DIR` | 存储目录 | `./rag_storage` |

## 🐛 常见问题

### 服务启动失败
```bash
# 检查端口占用
netstat -ano | findstr 8000
# 检查依赖
pip list | grep fastapi
```

### API 返回 403
- 检查 Authorization 头格式: `Bearer <api-key>`
- 确认 API Key 在 `.env` 中配置

### 检索结果为空
- 确认已导入文档
- 降低 `score_threshold` (例如 0.3)
- 检查查询是否与文档相关

## 📚 更多文档

- 完整中文指南: [GUIDE_zh.md](GUIDE_zh.md)
- 架构说明: [ARCHITECTURE.md](ARCHITECTURE.md)
- 英文文档: [README.md](README.md)
- Dify 官方文档: https://docs.dify.ai/

## 🆘 获取帮助

- GitHub Issues
- Discord 社区
- 微信交流群

---

**版本**: v1.0.0 | **更新**: 2024-01-14
