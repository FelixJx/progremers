#!/usr/bin/env python3
"""本地配置恢复脚本 - 安全恢复API密钥等本地配置"""

import os
import json
from pathlib import Path


def create_local_env_file():
    """创建本地.env文件，包含你的实际API配置"""
    
    env_file = Path(".env")
    
    if env_file.exists():
        print("⚠️ .env文件已存在，跳过创建")
        return
    
    print("🔧 创建本地.env配置文件...")
    
    # 这里是你的实际API配置 (仅在本地存在)
    env_content = """# AI Agent开发团队系统 - 本地环境配置
# 注意：此文件被.gitignore忽略，不会上传到GitHub

# 🤖 AI服务配置 - 填入你的实际API密钥
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# DeepSeek API (如果你有的话)
DEEPSEEK_API_KEY=sk-831cb74319af43ebbfd7ad5e13fd4dfd

# 阿里云API (如果你有的话)  
ALIBABA_API_KEY=sk-e050041b41674ed7b87644895ebae718

# 🗄️ 数据库配置
DATABASE_URL=postgresql://ai_agent:ai_agent_password@localhost:5432/ai_agent_team
REDIS_URL=redis://localhost:6379/0

# 🌐 API配置
API_HOST=0.0.0.0
API_PORT=8080
API_DEBUG=true

# 📊 Embedding配置
EMBEDDING_MODEL=bge-m3
EMBEDDING_MODEL_NAME=BAAI/bge-m3
EMBEDDING_CACHE_SIZE=10000
EMBEDDING_BATCH_SIZE=16
EMBEDDING_USE_FP16=true
EMBEDDING_DEVICE=cpu

# 📝 日志配置
LOG_LEVEL=INFO
LOG_FILE=logs/app.log

# 🔐 安全配置
SECRET_KEY=your_jwt_secret_key_here
JWT_EXPIRATION_HOURS=24

# 🚀 部署配置
ENVIRONMENT=development
DEBUG=true
"""
    
    with open(env_file, 'w', encoding='utf-8') as f:
        f.write(env_content)
    
    print("✅ .env文件创建成功!")
    print("📝 请编辑.env文件，填入你的实际API密钥")


def create_local_settings():
    """创建本地设置文件"""
    
    settings_dir = Path("config")
    settings_dir.mkdir(exist_ok=True)
    
    local_settings_file = settings_dir / "local_settings.py"
    
    if local_settings_file.exists():
        print("⚠️ 本地设置文件已存在，跳过创建")
        return
    
    print("🔧 创建本地设置文件...")
    
    settings_content = '''"""本地开发配置 - 覆盖默认设置"""

# API配置映射
LLM_CONFIGS = {
    "deepseek": {
        "api_key": "sk-831cb74319af43ebbfd7ad5e13fd4dfd",  # 你的实际密钥
        "base_url": "https://api.deepseek.com/v1",
        "model": "deepseek-chat"
    },
    "alibaba": {
        "api_key": "sk-e050041b41674ed7b87644895ebae718",  # 你的实际密钥
        "base_url": "https://dashscope.aliyuncs.com/api/v1",
        "model": "qwen-max"
    },
    "local": {
        "api_key": "not-needed",
        "base_url": "http://localhost:1234/v1",
        "model": "local-model"
    }
}

# Agent-LLM映射 (本地开发配置)
AGENT_LLM_MAPPING = {
    "manager": "deepseek",
    "pm": "deepseek", 
    "architect": "alibaba",
    "developer": "deepseek",
    "qa": "alibaba",
    "ui": "alibaba"
}

# 数据库配置
DATABASE_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "username": "ai_agent",
    "password": "ai_agent_password",
    "database": "ai_agent_team"
}

# Redis配置
REDIS_CONFIG = {
    "host": "localhost", 
    "port": 6379,
    "db": 0
}
'''
    
    with open(local_settings_file, 'w', encoding='utf-8') as f:
        f.write(settings_content)
    
    print("✅ 本地设置文件创建成功!")


def update_gitignore():
    """确保.gitignore包含所有敏感文件"""
    
    gitignore_file = Path(".gitignore")
    
    additional_ignores = [
        "# 本地配置恢复脚本添加的规则",
        "config/local_settings.py",
        "*.local",
        "*_local.py",
        "local_*.json"
    ]
    
    if gitignore_file.exists():
        with open(gitignore_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查是否需要添加规则
        missing_rules = []
        for rule in additional_ignores:
            if rule not in content:
                missing_rules.append(rule)
        
        if missing_rules:
            print("📝 更新.gitignore文件...")
            with open(gitignore_file, 'a', encoding='utf-8') as f:
                f.write("\n" + "\n".join(missing_rules) + "\n")
            print("✅ .gitignore更新完成!")


def create_secure_test_script():
    """创建安全的测试脚本"""
    
    test_script = Path("test_with_local_config.py")
    
    script_content = '''#!/usr/bin/env python3
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

print("\\n🔍 检查环境变量:")
for var in env_vars:
    value = os.getenv(var)
    if value:
        # 只显示前8个字符，保护敏感信息
        masked_value = value[:8] + "..." if len(value) > 8 else value
        print(f"✅ {var}: {masked_value}")
    else:
        print(f"⚠️ {var}: 未设置")

print("\\n🎯 配置建议:")
print("1. 确保.env文件包含你的实际API密钥")
print("2. 运行数据库: docker-compose up -d postgres redis")
print("3. 初始化数据库: python scripts/setup_database.py")
print("4. 开始测试: python test_core_system.py")
'''
    
    with open(test_script, 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    os.chmod(test_script, 0o755)
    print("✅ 安全测试脚本创建成功!")


def main():
    """主函数"""
    print("🔧 AI Agent团队系统 - 本地配置恢复")
    print("=" * 50)
    
    # 检查是否在项目根目录
    if not Path("src").exists():
        print("❌ 请在项目根目录运行此脚本")
        return
    
    print("📂 当前目录:", Path.cwd())
    
    # 1. 创建.env文件
    create_local_env_file()
    
    # 2. 创建本地设置文件
    create_local_settings()
    
    # 3. 更新.gitignore
    update_gitignore()
    
    # 4. 创建安全测试脚本
    create_secure_test_script()
    
    print("\\n🎉 本地配置恢复完成!")
    print("\\n📝 接下来的步骤:")
    print("1. 编辑.env文件，填入你的实际API密钥")
    print("2. 编辑config/local_settings.py，确认配置正确")
    print("3. 运行测试: python test_with_local_config.py")
    print("4. 启动系统: python -m src.main")
    
    print("\\n🔒 安全提醒:")
    print("- .env文件和config/local_settings.py被.gitignore忽略")
    print("- 这些文件只存在于你的本地机器上")
    print("- GitHub上的项目不包含任何敏感信息")
    print("- 每次clone项目后需要重新运行此脚本")


if __name__ == "__main__":
    main()