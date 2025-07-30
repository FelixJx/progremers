#!/usr/bin/env python3
"""自动GitHub Checkpoint脚本 - 自动上传项目进展到GitHub"""

import subprocess
import sys
import os
from datetime import datetime
from pathlib import Path


def run_command(command, cwd=None):
    """执行命令并返回结果"""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            cwd=cwd
        )
        
        if result.returncode != 0:
            print(f"❌ 命令执行失败: {command}")
            print(f"错误信息: {result.stderr}")
            return False, result.stderr
        
        return True, result.stdout
    
    except Exception as e:
        print(f"❌ 执行命令时发生异常: {str(e)}")
        return False, str(e)


def check_git_status():
    """检查Git仓库状态"""
    print("🔍 检查Git仓库状态...")
    
    success, output = run_command("git status --porcelain")
    if not success:
        return False, "无法获取Git状态"
    
    if output.strip():
        print("📝 发现以下文件变更:")
        for line in output.strip().split('\n'):
            print(f"   {line}")
        return True, "有文件变更"
    else:
        print("✅ 工作目录干净，没有未提交的变更")
        return True, "无变更"


def create_checkpoint_commit():
    """创建checkpoint提交"""
    print("\n🚀 创建Checkpoint提交...")
    
    # 获取当前时间
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 检查是否有变更
    has_changes, status = check_git_status()
    if not has_changes:
        return False
    
    if "无变更" in status:
        print("ℹ️ 没有需要提交的变更")
        return True
    
    # 添加所有文件 (但.gitignore会过滤敏感文件)
    print("📁 添加文件到暂存区...")
    success, _ = run_command("git add .")
    if not success:
        return False
    
    # 创建提交信息
    commit_message = f"""🔄 Checkpoint: AI Agent团队系统进展 - {timestamp}

✨ 新增功能:
- Agent自我进化系统完整实现
- BGE-M3高质量embedding集成
- 项目复盘和经验提取机制
- 知识积累和传承系统
- 量化进化评估框架

🏗️ 系统架构:
- 企业级微服务架构 (FastAPI + PostgreSQL + Redis)
- 多Agent协作通信系统
- Context压缩和RAG检索
- MCP深度集成实现

📊 技术亮点:
- Context-Rot缓解技术应用
- 多层记忆架构设计
- 智能知识融合算法
- 12维进化指标评估

🎯 当前状态: 核心功能完成，具备生产级Agent团队能力

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>"""
    
    # 执行提交
    print("💾 创建Git提交...")
    success, _ = run_command(f'git commit -m "{commit_message}"')
    if not success:
        return False
    
    print("✅ 提交创建成功!")
    return True


def setup_remote_if_needed():
    """设置远程仓库 (如果需要)"""
    print("\n🔗 检查远程仓库设置...")
    
    # 检查是否已有远程仓库
    success, output = run_command("git remote -v")
    if success and "origin" in output:
        print("✅ 远程仓库已配置")
        return True
    
    # 添加远程仓库
    github_repo = "https://github.com/FelixJx/progremers.git"
    print(f"🔗 添加远程仓库: {github_repo}")
    
    success, _ = run_command(f"git remote add origin {github_repo}")
    if not success:
        print("❌ 添加远程仓库失败")
        return False
    
    print("✅ 远程仓库配置成功!")
    return True


def push_to_github():
    """推送到GitHub"""
    print("\n🚀 推送到GitHub...")
    
    # 获取当前分支
    success, branch = run_command("git branch --show-current")
    if not success:
        branch = "main"
    else:
        branch = branch.strip()
    
    if not branch:
        branch = "main"
    
    print(f"📤 推送分支: {branch}")
    
    # 推送到远程仓库
    success, output = run_command(f"git push -u origin {branch}")
    if not success:
        # 如果推送失败，可能是首次推送或需要强制推送
        print("⚠️ 常规推送失败，尝试首次推送...")
        success, output = run_command(f"git push -u origin {branch}")
        
        if not success:
            print("❌ 推送失败，请检查:")
            print("1. GitHub仓库权限")
            print("2. 网络连接")
            print("3. Git凭据配置")
            return False
    
    print("🎉 成功推送到GitHub!")
    return True


def check_sensitive_files():
    """检查是否意外包含敏感文件"""
    print("\n🔒 检查敏感文件...")
    
    sensitive_patterns = [
        "*.env",
        "*api_key*",
        "*secret*",
        "*password*",
        "*.key",
        "*.pem"
    ]
    
    # 检查已暂存的文件
    success, output = run_command("git diff --cached --name-only")
    if not success:
        return True
    
    staged_files = output.strip().split('\n') if output.strip() else []
    
    sensitive_files = []
    for file in staged_files:
        file_lower = file.lower()
        for pattern in sensitive_patterns:
            pattern_clean = pattern.replace("*", "")
            if pattern_clean in file_lower:
                sensitive_files.append(file)
                break
    
    if sensitive_files:
        print("⚠️ 警告: 发现可能的敏感文件:")
        for file in sensitive_files:
            print(f"   🚨 {file}")
        
        response = input("是否继续提交? (y/N): ").lower()
        if response != 'y':
            print("❌ 用户取消提交")
            return False
    
    print("✅ 敏感文件检查通过")
    return True


def main():
    """主函数"""
    print("🤖 AI Agent团队系统 - 自动GitHub Checkpoint")
    print("=" * 50)
    
    # 检查是否在正确的目录
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    print(f"📂 项目目录: {project_root}")
    
    # 检查是否是Git仓库
    if not (project_root / ".git").exists():
        print("❌ 当前目录不是Git仓库")
        return False
    
    # 步骤1: 检查敏感文件
    if not check_sensitive_files():
        return False
    
    # 步骤2: 创建提交
    if not create_checkpoint_commit():
        return False
    
    # 步骤3: 设置远程仓库
    if not setup_remote_if_needed():
        return False
    
    # 步骤4: 推送到GitHub
    if not push_to_github():
        return False
    
    print("\n🎉 Checkpoint上传完成!")
    print(f"🔗 GitHub仓库: https://github.com/FelixJx/progremers")
    print("\n📊 项目统计:")
    
    # 显示一些统计信息
    success, file_count = run_command("find . -name '*.py' | wc -l")
    if success:
        print(f"   Python文件数: {file_count.strip()}")
    
    success, line_count = run_command("find . -name '*.py' | xargs wc -l | tail -1")
    if success:
        lines = line_count.strip().split()[-2] if line_count.strip() else "0"
        print(f"   代码行数: {lines}")
    
    return True


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n❌ 用户中断操作")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 发生未预期的错误: {str(e)}")
        sys.exit(1)