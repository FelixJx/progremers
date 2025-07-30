#!/usr/bin/env python3
"""使用本地配置的安全测试脚本"""

import os
import sys
from pathlib import Path

# 加载本地配置
sys.path.append(str(Path(__file__).parent / "config"))

try:
    from local_settings import LLM_CONFIGS, AGENT_LLM_MAPPING
    print("✅ 成功加载本地配置")
    print(f"📊 配置的LLM数量: {len(LLM_CONFIGS)}")
    print(f"🤖 配置的Agent数量: {len(AGENT_LLM_MAPPING)}")
    
    # 测试API密钥是否配置
    for name, config in LLM_CONFIGS.items():
        api_key = config.get("api_key", "")
        if api_key and api_key != "your_api_key_here":
            print(f"✅ {name} API密钥已配置")
        else:
            print(f"⚠️ {name} API密钥未配置")
            
except ImportError:
    print("❌ 未找到本地配置文件")
    print("💡 请先运行: python scripts/restore_local_config.py")

# 测试环境变量
env_vars = [
    "DEEPSEEK_API_KEY",
    "ALIBABA_API_KEY", 
    "DATABASE_URL",
    "REDIS_URL"
]

print("\n🔍 检查环境变量:")
for var in env_vars:
    value = os.getenv(var)
    if value:
        # 只显示前8个字符，保护敏感信息
        masked_value = value[:8] + "..." if len(value) > 8 else value
        print(f"✅ {var}: {masked_value}")
    else:
        print(f"⚠️ {var}: 未设置")

print("\n🎯 配置建议:")
print("1. 确保.env文件包含你的实际API密钥")
print("2. 运行数据库: docker-compose up -d postgres redis")
print("3. 初始化数据库: python scripts/setup_database.py")
print("4. 开始测试: python test_core_system.py")
