#!/usr/bin/env python3
"""DM-MCP Server Entry Point"""
from . import mcp
import sys

def main():
    """主入口函数"""
    try:
        # 运行 MCP 服务器
        mcp.run(transport="stdio")
    except KeyboardInterrupt:
        print("\n服务器已停止", file=sys.stderr)
        sys.exit(0)
    except Exception as e:
        print(f"\n服务器错误: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
