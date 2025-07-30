#!/usr/bin/env python3
"""BGE-M3模型安装和验证脚本"""

import asyncio
import sys
import subprocess
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.memory.bge_embedding import create_embedding_service
from src.utils import get_logger

logger = get_logger(__name__)


async def install_dependencies():
    """安装BGE-M3相关依赖"""
    
    print("🚀 开始安装BGE-M3依赖...")
    
    dependencies = [
        "FlagEmbedding==1.2.5",
        "sentence-transformers==2.2.2", 
        "torch>=2.0.0",
        "transformers>=4.33.0"
    ]
    
    for dep in dependencies:
        print(f"📦 安装 {dep}...")
        try:
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", dep
            ], capture_output=True, text=True, check=True)
            print(f"✅ {dep} 安装成功")
        except subprocess.CalledProcessError as e:
            print(f"❌ {dep} 安装失败: {e.stderr}")
            return False
    
    print("🎉 所有依赖安装完成!")
    return True


async def test_bge_embedding():
    """测试BGE-M3 embedding功能"""
    
    print("\n🧪 测试BGE-M3 Embedding服务...")
    
    try:
        # 创建embedding服务
        embedding_service = create_embedding_service()
        
        # 初始化
        print("⚙️ 初始化embedding服务...")
        success = await embedding_service.initialize()
        
        if not success:
            print("❌ Embedding服务初始化失败")
            return False
        
        print("✅ Embedding服务初始化成功")
        
        # 获取模型信息
        model_info = embedding_service.get_model_info()
        print(f"📊 模型信息: {model_info}")
        
        # 测试单个文本embedding
        test_text = "这是一个测试文本，用于验证BGE-M3模型的embedding功能。"
        print(f"🔤 测试文本: {test_text}")
        
        embedding = await embedding_service.embed_text(test_text)
        print(f"📐 Embedding维度: {len(embedding)}")
        print(f"🎯 Embedding样本: {embedding[:5]}...")
        
        # 测试批量embedding
        test_texts = [
            "用户登录功能实现",
            "数据库连接配置", 
            "API接口设计",
            "前端页面开发",
            "测试用例编写"
        ]
        
        print(f"\n📚 测试批量embedding ({len(test_texts)}个文本)...")
        batch_embeddings = await embedding_service.embed_batch(test_texts)
        print(f"✅ 批量embedding完成: {len(batch_embeddings)}个向量")
        
        # 测试相似度计算
        text1 = "用户登录功能"
        text2 = "用户注册功能"
        text3 = "数据库备份"
        
        sim1 = await embedding_service.get_similarity(text1, text2)
        sim2 = await embedding_service.get_similarity(text1, text3)
        
        print(f"\n🔍 相似度测试:")
        print(f"   '{text1}' vs '{text2}': {sim1:.3f}")
        print(f"   '{text1}' vs '{text3}': {sim2:.3f}")
        
        if sim1 > sim2:
            print("✅ 相似度计算正确: 相关文本相似度更高")
        else:
            print("⚠️ 相似度计算异常: 请检查模型")
        
        # 清理资源
        await embedding_service.shutdown()
        print("🧹 资源清理完成")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        return False


async def performance_benchmark():
    """性能基准测试"""
    
    print("\n⏱️ 性能基准测试...")
    
    try:
        embedding_service = create_embedding_service()
        await embedding_service.initialize()
        
        import time
        
        # 单个文本性能测试
        test_text = "这是一个中等长度的测试文本，用于评估BGE-M3模型的处理速度和性能表现。" * 10
        
        start_time = time.time()
        embedding = await embedding_service.embed_text(test_text)
        single_time = time.time() - start_time
        
        print(f"📊 单个文本embedding耗时: {single_time:.3f}秒")
        
        # 批量处理性能测试
        batch_texts = [f"测试文本{i}: 这是用于批量处理性能评估的示例文本。" * 5 for i in range(20)]
        
        start_time = time.time()
        batch_embeddings = await embedding_service.embed_batch(batch_texts)
        batch_time = time.time() - start_time
        
        print(f"📊 批量embedding({len(batch_texts)}个)耗时: {batch_time:.3f}秒")
        print(f"📊 平均每个文本耗时: {batch_time/len(batch_texts):.3f}秒")
        
        # 缓存性能测试
        start_time = time.time()
        cached_embedding = await embedding_service.embed_text(test_text)  # 应该命中缓存
        cache_time = time.time() - start_time
        
        print(f"📊 缓存命中耗时: {cache_time:.6f}秒")
        
        if cache_time < single_time * 0.1:
            print("✅ 缓存工作正常")
        else:
            print("⚠️ 缓存可能未生效")
        
        await embedding_service.shutdown()
        return True
        
    except Exception as e:
        print(f"❌ 性能测试失败: {str(e)}")
        return False


async def main():
    """主函数"""
    
    print("🤖 BGE-M3 Embedding模型安装和测试工具")
    print("=" * 50)
    
    # 检查Python版本
    if sys.version_info < (3, 8):
        print("❌ 需要Python 3.8+")
        return
    
    print(f"🐍 Python版本: {sys.version}")
    
    # 安装依赖
    if not await install_dependencies():
        print("❌ 依赖安装失败，退出")
        return
    
    # 测试功能
    if not await test_bge_embedding():
        print("❌ 功能测试失败")
        return
    
    # 性能测试
    if not await performance_benchmark():
        print("❌ 性能测试失败")
        return
    
    print("\n🎉 BGE-M3安装和测试完成!")
    print("\n📝 使用说明:")
    print("1. 在RAG检索器中，现在会自动使用BGE-M3模型")
    print("2. 如果BGE-M3不可用，会自动降级到fallback模式")
    print("3. 可以通过环境变量配置模型参数:")
    print("   EMBEDDING_MODEL=bge-m3")
    print("   EMBEDDING_MODEL_NAME=BAAI/bge-m3")
    print("   EMBEDDING_DEVICE=cpu  # 或 cuda")
    print("   EMBEDDING_USE_FP16=true")


if __name__ == "__main__":
    asyncio.run(main())