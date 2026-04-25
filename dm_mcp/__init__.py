import os
from fastmcp import FastMCP
import dmPython

# 1. 初始化 MCP 实例
mcp = FastMCP("dm-mcp")

# 2. 动态获取配置 (核心修改)
# 优先读取环境变量，如果没有则使用默认值 (仅作为测试用)
DM_SERVER = os.getenv("DM_SERVER", "localhost")
DM_PORT = int(os.getenv("DM_PORT", "5236"))
DM_USER = os.getenv("DM_USER", "SYSDBA")
DM_PASSWORD = os.getenv("DM_PASSWORD", "SYSDBA")
# 达梦连接后默认Schema通常是用户名，也可以通过 SQL 切换
DM_SCHEMA = os.getenv("DM_SCHEMA", DM_USER)


def get_connection():
    """
    动态建立连接
    依赖环境变量: DM_SERVER, DM_PORT, DM_USER, DM_PASSWORD
    """
    try:
        # 打印调试信息（实际生产环境可去掉）
        # print(f"正在连接: {DM_SERVER}:{DM_PORT} 用户: {DM_USER}")

        conn = dmPython.connect(
            dsn=f"{DM_SERVER}:{DM_PORT}",
            user=DM_USER,
            password=DM_PASSWORD,
            # 如果指定了 schema，可以在连接后设置，或者在 dsn 中处理
        )

        # 如果指定了 Schema，切换当前会话的 Schema
        if DM_SCHEMA:
            cursor = conn.cursor()
            cursor.execute(f"SET SCHEMA {DM_SCHEMA}")
            cursor.close()

        return conn
    except Exception as e:
        return f"连接失败: {str(e)}"


# 3. 定义工具：查询数据
@mcp.tool()
def query_db(sql: str) -> str:
    """
    执行 SQL 查询。
    注意：仅允许 SELECT 语句。
    """
    if not sql.strip().lower().startswith("select"):
        return "错误：为了安全，仅支持 SELECT 查询。"

    conn = get_connection()
    if isinstance(conn, str):
        return conn

    try:
        cursor = conn.cursor()
        cursor.execute(sql)

        # 获取列名
        columns = [desc[0] for desc in cursor.description]
        # 获取数据
        rows = cursor.fetchall()

        result = f"查询成功 (共{len(rows)}条):\n"
        result += " | ".join(columns) + "\n"
        result += "-" * 50 + "\n"
        for row in rows:
            result += " | ".join([str(item) for item in row]) + "\n"

        return result
    except Exception as e:
        return f"执行错误: {str(e)}"
    finally:
        conn.close()


# 4. 定义工具：获取表结构
@mcp.tool()
def get_table_structure(table_name: str) -> str:
    """
    获取表结构信息
    """
    conn = get_connection()
    if isinstance(conn, str):
        return conn

    try:
        cursor = conn.cursor()
        # 达梦查询表结构 - 使用参数化查询防止 SQL 注入
        sql = """
        SELECT COLUMN_NAME, DATA_TYPE, DATA_LENGTH 
        FROM USER_TAB_COLUMNS 
        WHERE TABLE_NAME = ?
        ORDER BY COLUMN_ID
        """
        cursor.execute(sql, (table_name.upper(),))
        rows = cursor.fetchall()

        if not rows:
            return f"表 '{table_name}' 不存在或无权访问。"

        result = f"表结构 [{table_name}]:\n"
        result += "列名 | 类型 | 长度\n"
        result += "-" * 30 + "\n"
        for row in rows:
            result += f"{row[0]} | {row[1]} | {row[2]}\n"

        return result
    except Exception as e:
        return f"获取结构错误: {str(e)}"
    finally:
        conn.close()