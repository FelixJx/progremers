#!/usr/bin/env python3.11
"""
手动代码分析工具 - 模拟Serena MCP的符号级分析功能
分析酒店分析工具项目的代码结构和质量
"""

import os
import ast
import json
from pathlib import Path
from typing import Dict, List, Any
from collections import defaultdict

def analyze_project_structure(project_path: str) -> Dict[str, Any]:
    """分析项目结构"""
    
    analysis = {
        "project_overview": {},
        "code_metrics": {},
        "dependency_analysis": {},
        "architecture_patterns": {},
        "code_quality_issues": [],
        "improvement_suggestions": []
    }
    
    project_path = Path(project_path)
    
    # 基础统计
    total_files = 0
    python_files = 0
    lines_of_code = 0
    
    # 代码结构分析
    classes = []
    functions = []
    imports = defaultdict(int)
    
    for py_file in project_path.rglob("*.py"):
        if "venv" in str(py_file) or "__pycache__" in str(py_file):
            continue
            
        python_files += 1
        
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
                lines_of_code += len(content.split('\n'))
                
            # AST解析
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    classes.append({
                        "name": node.name,
                        "file": str(py_file.relative_to(project_path)),
                        "line": node.lineno,
                        "methods": [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
                    })
                elif isinstance(node, ast.FunctionDef):
                    functions.append({
                        "name": node.name,
                        "file": str(py_file.relative_to(project_path)),
                        "line": node.lineno,
                        "args": len(node.args.args)
                    })
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        imports[alias.name] += 1
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports[node.module] += 1
                        
        except Exception as e:
            analysis["code_quality_issues"].append(f"解析错误 {py_file}: {str(e)}")
    
    # 统计分析
    analysis["project_overview"] = {
        "total_python_files": python_files,
        "total_lines_of_code": lines_of_code,
        "average_file_size": lines_of_code // python_files if python_files > 0 else 0,
        "total_classes": len(classes),
        "total_functions": len(functions)
    }
    
    # 核心业务类分析
    core_classes = [cls for cls in classes if any(
        keyword in cls["name"].lower() 
        for keyword in ["analyzer", "calculator", "monitor", "service", "manager"]
    )]
    
    analysis["architecture_patterns"] = {
        "core_business_classes": len(core_classes),
        "service_classes": len([cls for cls in classes if "service" in cls["name"].lower()]),
        "analyzer_classes": len([cls for cls in classes if "analyzer" in cls["name"].lower()]),
        "model_classes": len([cls for cls in classes if any(
            "model" in cls["file"] for cls in classes
        )])
    }
    
    # 依赖分析
    top_imports = dict(sorted(imports.items(), key=lambda x: x[1], reverse=True)[:10])
    analysis["dependency_analysis"] = {
        "total_unique_imports": len(imports),
        "most_used_imports": top_imports,
        "external_dependencies": {
            "data_processing": imports.get("pandas", 0) + imports.get("numpy", 0),
            "web_framework": imports.get("fastapi", 0) + imports.get("starlette", 0),
            "database": imports.get("sqlalchemy", 0) + imports.get("pymysql", 0),
            "async_processing": imports.get("asyncio", 0) + imports.get("aiohttp", 0)
        }
    }
    
    # 代码质量评估
    analysis["code_metrics"] = {
        "complexity_indicators": {
            "large_classes": len([cls for cls in classes if len(cls["methods"]) > 10]),
            "long_functions": len([func for func in functions if func["args"] > 5]),
            "deep_file_structure": len([cls for cls in classes if cls["file"].count("/") > 3])
        },
        "maintainability_score": calculate_maintainability_score(classes, functions, lines_of_code)
    }
    
    # 改进建议
    analysis["improvement_suggestions"] = generate_improvement_suggestions(analysis)
    
    return analysis

def calculate_maintainability_score(classes: List, functions: List, total_loc: int) -> float:
    """计算可维护性评分 (0-10)"""
    
    score = 10.0
    
    # 类复杂度惩罚
    large_classes = len([cls for cls in classes if len(cls["methods"]) > 10])
    score -= (large_classes * 0.5)
    
    # 函数复杂度惩罚  
    complex_functions = len([func for func in functions if func["args"] > 5])
    score -= (complex_functions * 0.3)
    
    # 代码行数惩罚
    if total_loc > 10000:
        score -= 1.0
    elif total_loc > 5000:
        score -= 0.5
    
    return max(0.0, min(10.0, score))

def generate_improvement_suggestions(analysis: Dict) -> List[str]:
    """生成改进建议"""
    
    suggestions = []
    
    metrics = analysis["code_metrics"]["complexity_indicators"]
    
    if metrics["large_classes"] > 3:
        suggestions.append("🔧 发现多个大型类，建议拆分为更小的单一职责类")
    
    if metrics["long_functions"] > 5:
        suggestions.append("🔧 发现多个复杂函数，建议重构为更小的函数")
    
    if analysis["project_overview"]["average_file_size"] > 500:
        suggestions.append("🔧 平均文件大小较大，建议拆分模块")
    
    # 架构建议
    arch = analysis["architecture_patterns"]
    if arch["service_classes"] < 3:
        suggestions.append("🏗️ 建议增加更多服务层类，提升代码分层")
    
    if arch["analyzer_classes"] > arch["service_classes"]:
        suggestions.append("🏗️ 分析器类过多，建议整合到统一的分析服务中")
    
    # 依赖建议
    deps = analysis["dependency_analysis"]["external_dependencies"]
    if deps["async_processing"] < 5:
        suggestions.append("⚡ 异步处理使用较少，建议增加异步操作提升性能")
    
    if deps["database"] > 10:
        suggestions.append("🗄️ 数据库操作较多，建议添加连接池和缓存优化")
    
    return suggestions

def analyze_business_logic_patterns(project_path: str) -> Dict[str, Any]:
    """分析业务逻辑模式"""
    
    project_path = Path(project_path)
    
    patterns = {
        "roi_calculation_patterns": [],
        "data_collection_patterns": [], 
        "analysis_patterns": [],
        "api_patterns": []
    }
    
    # 分析ROI计算模式
    roi_files = list(project_path.rglob("*roi*.py")) + list(project_path.rglob("*investment*.py"))
    for roi_file in roi_files:
        try:
            with open(roi_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            if "calculate" in content.lower():
                patterns["roi_calculation_patterns"].append({
                    "file": str(roi_file.relative_to(project_path)),
                    "calculation_methods": content.lower().count("def calculate"),
                    "financial_indicators": [
                        indicator for indicator in ["npv", "irr", "roi", "payback"]
                        if indicator in content.lower()
                    ]
                })
        except:
            continue
    
    # 分析数据采集模式
    collector_files = list(project_path.rglob("*collector*.py")) + list(project_path.rglob("*crawl*.py"))
    for collector_file in collector_files:
        try:
            with open(collector_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            patterns["data_collection_patterns"].append({
                "file": str(collector_file.relative_to(project_path)),
                "async_methods": content.count("async def"),
                "api_calls": content.lower().count("requests.") + content.lower().count("aiohttp"),
                "data_sources": [
                    source for source in ["ctrip", "meituan", "gaode", "baidu"]
                    if source in content.lower()
                ]
            })
        except:
            continue
    
    return patterns

def main():
    """主函数"""
    
    project_path = "/Users/jx/Downloads/酒店分析工具"
    
    print("🔍 开始深度代码分析 (模拟Serena MCP功能)")
    print("=" * 60)
    
    # 项目结构分析
    print("📊 分析项目结构...")
    structure_analysis = analyze_project_structure(project_path)
    
    # 业务逻辑分析
    print("🏗️ 分析业务逻辑模式...")
    business_analysis = analyze_business_logic_patterns(project_path)
    
    # 综合报告
    comprehensive_report = {
        "analysis_timestamp": "2025-07-29T23:40:00Z",
        "project_structure": structure_analysis,
        "business_patterns": business_analysis,
        "recommendations": {
            "immediate_actions": structure_analysis["improvement_suggestions"][:3],
            "architectural_improvements": structure_analysis["improvement_suggestions"][3:],
            "performance_optimizations": [
                "增加异步处理能力",
                "实现数据库连接池",
                "添加缓存层"
            ]
        }
    }
    
    # 打印报告
    print_analysis_report(comprehensive_report)
    
    # 保存详细报告
    with open("manual_code_analysis_report.json", "w", encoding="utf-8") as f:
        json.dump(comprehensive_report, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 详细分析报告已保存到: manual_code_analysis_report.json")

def print_analysis_report(report: Dict):
    """打印分析报告"""
    
    print("\n" + "="*60)
    print("🏨 酒店分析工具 - 深度代码分析报告")
    print("="*60)
    
    # 项目概览
    overview = report["project_structure"]["project_overview"]
    print(f"\n📊 项目概览:")
    print(f"   📄 Python文件数: {overview['total_python_files']}")
    print(f"   📝 代码总行数: {overview['total_lines_of_code']:,}")
    print(f"   🏗️ 类总数: {overview['total_classes']}")
    print(f"   ⚙️ 函数总数: {overview['total_functions']}")
    
    # 架构模式
    arch = report["project_structure"]["architecture_patterns"]
    print(f"\n🏗️ 架构模式分析:")
    print(f"   🔧 核心业务类: {arch['core_business_classes']}")
    print(f"   🛠️ 服务类: {arch['service_classes']}")
    print(f"   📈 分析器类: {arch['analyzer_classes']}")
    print(f"   📊 模型类: {arch['model_classes']}")
    
    # 代码质量
    quality = report["project_structure"]["code_metrics"]
    print(f"\n📈 代码质量评估:")
    print(f"   🎯 可维护性评分: {quality['maintainability_score']:.1f}/10")
    print(f"   ⚠️ 大型类数量: {quality['complexity_indicators']['large_classes']}")
    print(f"   ⚠️ 复杂函数数量: {quality['complexity_indicators']['long_functions']}")
    
    # 改进建议
    suggestions = report["project_structure"]["improvement_suggestions"]
    if suggestions:
        print(f"\n💡 改进建议:")
        for i, suggestion in enumerate(suggestions[:5], 1):
            print(f"   {i}. {suggestion}")
    
    # ROI计算分析
    roi_patterns = report["business_patterns"]["roi_calculation_patterns"]
    if roi_patterns:
        print(f"\n💰 ROI计算模块分析:")
        for pattern in roi_patterns[:2]:
            print(f"   📁 {pattern['file']}")
            print(f"      计算方法数: {pattern['calculation_methods']}")
            print(f"      财务指标: {', '.join(pattern['financial_indicators'])}")

if __name__ == "__main__":
    main()