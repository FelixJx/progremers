#!/usr/bin/env python3.11
"""
项目导入示例脚本
"""

import requests
import json
import sys
from datetime import datetime

def import_project_via_api():
    """通过API导入项目"""
    
    # API基础URL
    base_url = "http://localhost:8080"
    
    # 示例项目配置
    project_data = {
        "name": "智能客服系统",
        "description": "基于AI的智能客服系统，支持多轮对话、情感分析、自动回复等功能",
        "type": "web",
        "priority": "high",
        "budget": 500000,
        "timeline": "3个月",
        "requirements": [
            "用户注册登录",
            "智能对话机器人",
            "客服工单管理", 
            "数据分析dashboard",
            "多渠道接入(微信/网页/APP)"
        ],
        "tech_stack": [
            "React.js",
            "Node.js", 
            "PostgreSQL",
            "Redis",
            "Docker",
            "AI模型集成"
        ],
        "business_goals": [
            "提升客服效率50%",
            "降低人工成本30%",
            "提高客户满意度",
            "支持7x24小时服务"
        ]
    }
    
    try:
        print("🚀 正在导入项目到AI开发团队...")
        print(f"项目名称: {project_data['name']}")
        print(f"项目类型: {project_data['type']}")
        print(f"预算: ¥{project_data['budget']:,}")
        print(f"时间线: {project_data['timeline']}")
        
        # 发送创建项目请求
        response = requests.post(
            f"{base_url}/api/projects/create",
            json=project_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("\n✅ 项目导入成功!")
            print(f"📋 项目ID: {result['project_id']}")
            print(f"📊 项目状态: {result['status']}")
            print(f"💬 消息: {result['message']}")
            
            # 显示分配的AI团队
            if 'project_status' in result and 'assigned_agents' in result['project_status']:
                print(f"\n👥 分配的AI团队:")
                for agent in result['project_status']['assigned_agents']:
                    print(f"   🤖 {agent}")
                    
            return result['project_id']
            
        else:
            print(f"❌ 项目导入失败: {response.status_code}")
            print(f"错误信息: {response.text}")
            return None
            
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到AI开发团队API服务")
        print("请确保服务正在运行: python3.11 start_team.py")
        return None
    except Exception as e:
        print(f"❌ 导入过程中出现错误: {str(e)}")
        return None

def check_project_status(project_id):
    """检查项目状态"""
    base_url = "http://localhost:8080"
    
    try:
        response = requests.get(f"{base_url}/api/projects/{project_id}")
        if response.status_code == 200:
            project = response.json()
            print(f"\n📊 项目状态更新:")
            print(f"   名称: {project['project']['name']}")
            print(f"   状态: {project['project']['status']}")
            print(f"   进度: {project['project'].get('progress', 0)}%")
            
            if 'phases' in project and project['phases']:
                print(f"\n📋 项目阶段:")
                for phase_name, phase_info in project['phases'].items():
                    status = "✅" if phase_info.get('completed') else "🔄"
                    print(f"   {status} {phase_name}: {phase_info.get('description', 'N/A')}")
                    
        else:
            print(f"❌ 无法获取项目状态: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 检查状态时出现错误: {str(e)}")

def list_all_projects():
    """列出所有项目"""
    base_url = "http://localhost:8080"
    
    try:
        response = requests.get(f"{base_url}/api/projects")
        if response.status_code == 200:
            data = response.json()
            projects = data['projects']
            
            print(f"\n📁 当前项目列表 (共{len(projects)}个):")
            print("-" * 60)
            
            for project in projects:
                status_icon = {
                    'planning': '📋',
                    'in_progress': '🔄', 
                    'completed': '✅',
                    'paused': '⏸️'
                }.get(project['status'], '❓')
                
                print(f"{status_icon} {project['name']}")
                print(f"   ID: {project['id']}")
                print(f"   类型: {project['type']}")
                print(f"   状态: {project['status']}")
                print(f"   进度: {project['progress']}%")
                print(f"   团队: {', '.join(project['assigned_agents'])}")
                print(f"   更新: {project['last_update']}")
                print()
                
        else:
            print(f"❌ 无法获取项目列表: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 获取项目列表时出现错误: {str(e)}")

def main():
    """主函数"""
    print("🤖 AI开发团队 - 项目导入工具")
    print("=" * 50)
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "import":
            project_id = import_project_via_api()
            if project_id:
                print(f"\n🔍 检查项目状态...")
                check_project_status(project_id)
                
        elif command == "list":
            list_all_projects()
            
        elif command == "status" and len(sys.argv) > 2:
            project_id = sys.argv[2]
            check_project_status(project_id)
            
        else:
            print("❌ 无效命令")
            print_usage()
    else:
        print_usage()

def print_usage():
    """打印使用说明"""
    print("\n📖 使用说明:")
    print("   python3.11 import_project_example.py import   - 导入示例项目")
    print("   python3.11 import_project_example.py list     - 列出所有项目") 
    print("   python3.11 import_project_example.py status <project_id> - 检查项目状态")
    print("\n💡 提示:")
    print("   - 确保AI开发团队服务正在运行")
    print("   - 可以修改脚本中的project_data来导入自定义项目")
    print("   - 访问 http://localhost:3000/launchpad 使用图形界面")

if __name__ == "__main__":
    main()