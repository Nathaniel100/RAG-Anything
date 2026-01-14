#!/usr/bin/env python
"""
快速启动脚本 - 检查环境并启动服务
"""

import os
import sys
from pathlib import Path


def check_env_file():
    """检查.env文件是否存在"""
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if not env_file.exists():
        print("⚠️  未找到.env文件")
        if env_example.exists():
            print("请复制.env.example并配置:")
            print(f"  cp {env_example} {env_file}")
            print("  然后编辑.env文件配置API密钥等信息")
        return False
    return True


def check_dependencies():
    """检查依赖是否安装"""
    try:
        import fastapi
        import pydantic
        import uvicorn
        from openai import AsyncOpenAI
        print("✓ 依赖检查通过")
        return True
    except ImportError as e:
        print(f"✗ 缺少依赖: {e}")
        print("请运行: pip install -r requirements.txt")
        return False


def check_raganything():
    """检查RAGAnything是否可用"""
    try:
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from raganything import RAGAnything
        print("✓ RAGAnything 可用")
        return True
    except ImportError as e:
        print(f"✗ 无法导入RAGAnything: {e}")
        print("请确保已安装RAGAnything:")
        print("  cd .. && pip install -e .")
        return False


def main():
    """主函数"""
    print("=" * 60)
    print("Dify External Knowledge API - 启动检查")
    print("=" * 60)
    print()
    
    # 检查环境
    checks = [
        ("环境配置文件", check_env_file),
        ("Python依赖", check_dependencies),
        ("RAGAnything", check_raganything),
    ]
    
    all_passed = True
    for name, check_func in checks:
        print(f"检查 {name}...")
        if not check_func():
            all_passed = False
        print()
    
    if not all_passed:
        print("=" * 60)
        print("✗ 环境检查失败，请修复上述问题后重试")
        print("=" * 60)
        sys.exit(1)
    
    print("=" * 60)
    print("✓ 所有检查通过，启动服务...")
    print("=" * 60)
    print()
    
    # 启动服务
    os.system("python app.py")


if __name__ == "__main__":
    main()
