#!/usr/bin/env python3
"""
DM-MCP 诊断工具
用于检查安装和配置是否正确
"""
import sys
import os

def check_installation():
    """检查 dm-mcp 是否正确安装"""
    print("=" * 60)
    print("DM-MCP 安装诊断")
    print("=" * 60)
    
    # 1. 检查 Python 版本
    print(f"\n1. Python 版本: {sys.version}")
    print(f"   Python 路径: {sys.executable}")
    
    # 2. 检查 dm_mcp 是否可导入
    try:
        import dm_mcp
        print(f"\n2. ✓ dm_mcp 模块已安装")
        print(f"   模块路径: {dm_mcp.__file__}")
    except ImportError as e:
        print(f"\n2. ✗ dm_mcp 模块未安装: {e}")
        return False
    
    # 3. 检查依赖
    print("\n3. 检查依赖:")
    dependencies = ['fastmcp', 'mcp', 'dmPython']
    for dep in dependencies:
        try:
            module = __import__(dep)
            version = getattr(module, '__version__', 'unknown')
            print(f"   ✓ {dep}: {version}")
        except ImportError:
            print(f"   ✗ {dep}: 未安装")
    
    # 4. 检查环境变量
    print("\n4. 环境变量检查:")
    env_vars = ['DM_SERVER', 'DM_PORT', 'DM_USER', 'DM_PASSWORD', 'DM_SCHEMA']
    for var in env_vars:
        value = os.getenv(var, '未设置')
        if var == 'DM_PASSWORD' and value != '未设置':
            value = '***'  # 隐藏密码
        status = "✓" if value != '未设置' else "✗"
        print(f"   {status} {var}: {value}")
    
    # 5. 检查入口点
    print("\n5. 检查入口点:")
    try:
        from dm_mcp.__main__ import main
        print(f"   ✓ 入口函数存在: {main}")
    except Exception as e:
        print(f"   ✗ 入口函数错误: {e}")
        return False
    
    # 6. 检查 MCP 实例
    print("\n6. 检查 MCP 实例:")
    try:
        from dm_mcp import mcp
        print(f"   ✓ MCP 实例: {mcp}")
        print(f"   服务器名称: {mcp.name}")
    except Exception as e:
        print(f"   ✗ MCP 实例错误: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("诊断完成！")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    success = check_installation()
    sys.exit(0 if success else 1)
