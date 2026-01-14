"""
初始化脚本 - 导入文档到知识库
"""

import asyncio
import sys
from pathlib import Path

# 添加父目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from raganything import RAGAnything
from raganything.config import RAGAnythingConfig


async def init_knowledge_base(document_paths: list[str]):
    """
    初始化知识库并导入文档
    
    Args:
        document_paths: 文档路径列表
    """
    print("=" * 60)
    print("初始化 Dify 外部知识库")
    print("=" * 60)
    
    # 创建配置
    config = RAGAnythingConfig(
        working_dir="./rag_storage",
        parser="mineru",
        parse_method="auto"
    )
    
    # 初始化 RAGAnything
    print("\n1. 初始化 RAGAnything...")
    rag = RAGAnything(config=config)
    await rag.initialize_rag()
    print("   ✓ 初始化完成")
    
    # 导入文档
    print(f"\n2. 导入 {len(document_paths)} 个文档...")
    for i, doc_path in enumerate(document_paths, 1):
        print(f"\n   [{i}/{len(document_paths)}] 处理: {doc_path}")
        try:
            result = await rag.insert_file(doc_path)
            print(f"   ✓ 导入成功")
        except Exception as e:
            print(f"   ✗ 导入失败: {str(e)}")
    
    print("\n3. 测试检索...")
    test_query = "What is this document about?"
    result = await rag.query(test_query)
    print(f"   查询: {test_query}")
    print(f"   结果: {result[:200]}..." if len(result) > 200 else f"   结果: {result}")
    
    print("\n" + "=" * 60)
    print("知识库初始化完成!")
    print("=" * 60)
    print(f"\n存储位置: {config.working_dir}")
    print("现在可以启动API服务: python app.py")


if __name__ == "__main__":
    # 示例：导入文档
    # 修改为实际的文档路径
    documents = [
        # "./docs/sample.pdf",
        # "./docs/readme.md",
    ]
    
    if not documents:
        print("请在脚本中指定要导入的文档路径")
        print("编辑 init_knowledge.py 中的 documents 列表")
        sys.exit(1)
    
    asyncio.run(init_knowledge_base(documents))
