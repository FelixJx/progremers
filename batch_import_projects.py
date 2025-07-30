#!/usr/bin/env python3.11
"""
批量项目导入脚本
"""

import requests
import json
import time
from datetime import datetime

def batch_import_projects():
    """批量导入多个项目"""
    
    # 预定义的项目模板
    project_templates = [
        {
            "name": "电商购物平台",
            "description": "全功能电商平台，支持商品展示、购物车、支付、订单管理",
            "type": "web",
            "priority": "high",
            "requirements": ["用户注册", "商品管理", "购物车", "支付系统", "订单跟踪"],
            "tech_stack": ["React", "Node.js", "MongoDB", "Redis"],
            "business_goals": ["GMV增长", "用户体验优化", "转化率提升"]
        },
        {
            "name": "在线教育App",
            "description": "移动端在线学习平台，支持视频课程、作业提交、进度跟踪",
            "type": "mobile",
            "priority": "medium",
            "requirements": ["视频播放", "用户学习进度", "作业系统", "社区讨论"],
            "tech_stack": ["React Native", "Django", "PostgreSQL"],
            "business_goals": ["用户留存提升", "学习效果优化", "平台活跃度"]
        },
        {
            "name": "企业CRM系统",
            "description": "客户关系管理系统，支持销售流程、客户跟踪、数据分析",
            "type": "enterprise",
            "priority": "high",
            "requirements": ["客户管理", "销售流程", "数据分析", "权限控制"],
            "tech_stack": ["Vue.js", "Spring Boot", "MySQL"],
            "business_goals": ["销售效率提升", "客户满意度", "数据驱动决策"]
        },
        {
            "name": "智能数据分析平台",
            "description": "基于AI的数据分析和可视化平台，支持多数据源接入",
            "type": "data",
            "priority": "medium",
            "requirements": ["数据接入", "ETL处理", "可视化图表", "AI预测"],
            "tech_stack": ["Python", "FastAPI", "Apache Spark", "TensorFlow"],
            "business_goals": ["数据价值挖掘", "决策支持", "预测准确性"]
        },
        {
            "name": "物联网监控系统",
            "description": "IoT设备监控和管理平台，支持实时数据采集和告警",
            "type": "iot",
            "priority": "high",
            "requirements": ["设备接入", "实时监控", "告警系统", "数据存储"],
            "tech_stack": ["Go", "InfluxDB", "MQTT", "Grafana"],
            "business_goals": ["设备稳定性", "故障预防", "运维效率"]
        }
    ]
    
    base_url = "http://localhost:8080"
    imported_projects = []
    
    print("🚀 开始批量导入项目到AI开发团队...")
    print(f"计划导入 {len(project_templates)} 个项目")
    print("=" * 60)
    
    for i, template in enumerate(project_templates, 1):
        print(f"\n📋 导入项目 {i}/{len(project_templates)}: {template['name']}")
        
        try:
            response = requests.post(
                f"{base_url}/api/projects/create",
                json=template,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ 导入成功 - ID: {result['project_id']}")
                imported_projects.append({
                    'name': template['name'],
                    'id': result['project_id'],
                    'status': 'success'
                })
            else:
                print(f"❌ 导入失败: {response.status_code}")
                imported_projects.append({
                    'name': template['name'], 
                    'id': None,
                    'status': 'failed',
                    'error': response.text
                })
                
        except Exception as e:
            print(f"❌ 导入异常: {str(e)}")
            imported_projects.append({
                'name': template['name'],
                'id': None, 
                'status': 'error',
                'error': str(e)
            })
        
        # 添加延迟避免API压力
        time.sleep(1)
    
    # 显示导入结果
    print("\n" + "=" * 60)
    print("📊 批量导入结果统计:")
    print("=" * 60)
    
    success_count = len([p for p in imported_projects if p['status'] == 'success'])
    failed_count = len(imported_projects) - success_count
    
    print(f"✅ 成功导入: {success_count} 个项目")
    print(f"❌ 导入失败: {failed_count} 个项目")
    
    if success_count > 0:
        print(f"\n🎉 成功导入的项目:")
        for project in imported_projects:
            if project['status'] == 'success':
                print(f"   📋 {project['name']} (ID: {project['id']})")
    
    if failed_count > 0:
        print(f"\n⚠️ 失败的项目:")
        for project in imported_projects:
            if project['status'] != 'success':
                print(f"   ❌ {project['name']} - {project.get('error', 'Unknown error')}")
    
    return imported_projects

def create_custom_project():
    """创建自定义项目"""
    print("🛠️ 创建自定义项目")
    print("=" * 30)
    
    # 交互式收集项目信息
    name = input("📝 项目名称: ").strip()
    if not name:
        print("❌ 项目名称不能为空")
        return None
    
    description = input("📋 项目描述: ").strip() 
    
    print("\n📂 项目类型选择:")
    types = ["web", "mobile", "desktop", "api", "data", "iot", "enterprise"]
    for i, t in enumerate(types, 1):
        print(f"   {i}) {t}")
    
    try:
        type_choice = int(input("选择类型 (1-7): ")) - 1
        project_type = types[type_choice] if 0 <= type_choice < len(types) else "web"
    except:
        project_type = "web"
    
    print("\n📊 优先级选择:")
    priorities = ["low", "medium", "high", "urgent"]
    for i, p in enumerate(priorities, 1):
        print(f"   {i}) {p}")
    
    try:
        priority_choice = int(input("选择优先级 (1-4): ")) - 1
        priority = priorities[priority_choice] if 0 <= priority_choice < len(priorities) else "medium"
    except:
        priority = "medium"
    
    # 收集需求
    print("\n📋 核心需求 (每行一个，空行结束):")
    requirements = []
    while True:
        req = input("需求: ").strip()
        if not req:
            break
        requirements.append(req)
    
    # 收集技术栈
    print("\n🛠️ 技术栈 (每行一个，空行结束):")
    tech_stack = []
    while True:
        tech = input("技术: ").strip()
        if not tech:
            break
        tech_stack.append(tech)
    
    # 构建项目数据
    project_data = {
        "name": name,
        "description": description,
        "type": project_type,
        "priority": priority,
        "requirements": requirements,
        "tech_stack": tech_stack,
        "business_goals": []
    }
    
    # 发送创建请求
    base_url = "http://localhost:8080"
    
    try:
        print(f"\n🚀 正在创建项目: {name}")
        response = requests.post(
            f"{base_url}/api/projects/create",
            json=project_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ 项目创建成功!")
            print(f"📋 项目ID: {result['project_id']}")
            return result['project_id']
        else:
            print(f"❌ 项目创建失败: {response.status_code}")
            print(f"错误: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ 创建过程中出现错误: {str(e)}")
        return None

def main():
    """主函数"""
    print("🤖 AI开发团队 - 项目批量导入工具")
    print("=" * 50)
    
    print("选择操作:")
    print("1) 批量导入预设项目模板")
    print("2) 创建自定义项目")
    print("3) 退出")
    
    try:
        choice = input("\n请选择 (1-3): ").strip()
        
        if choice == "1":
            batch_import_projects()
        elif choice == "2":
            create_custom_project()
        elif choice == "3":
            print("👋 再见!")
        else:
            print("❌ 无效选择")
            
    except KeyboardInterrupt:
        print("\n\n👋 操作已取消")
    except Exception as e:
        print(f"\n❌ 程序出现错误: {str(e)}")

if __name__ == "__main__":
    main()