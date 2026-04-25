from . import mcp

def main():
    """主入口函数"""
    # 运行 MCP 服务器
    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()
