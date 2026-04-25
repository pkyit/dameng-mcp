import os
import re
import logging
from fastmcp import FastMCP
import dmPython

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("dm-mcp")

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


def validate_schema_name(schema_name: str) -> bool:
    """
    验证 Schema 名称是否合法（防止 SQL 注入）
    只允许字母、数字、下划线，且必须以字母或下划线开头
    """
    if not schema_name:
        return False
    # 正则表达式：以字母或下划线开头，后续可以是字母、数字、下划线
    pattern = r'^[a-zA-Z_][a-zA-Z0-9_]*$'
    return bool(re.match(pattern, schema_name))


def validate_table_name(table_name: str) -> bool:
    """
    验证表名是否合法（防止 SQL 注入）
    """
    if not table_name:
        return False
    pattern = r'^[a-zA-Z_][a-zA-Z0-9_]*$'
    return bool(re.match(pattern, table_name))


def get_connection():
    """
    动态建立连接
    依赖环境变量: DM_SERVER, DM_PORT, DM_USER, DM_PASSWORD
    """
    try:
        logger.info(f"正在连接达梦数据库: {DM_SERVER}:{DM_PORT} 用户: {DM_USER}")

        conn = dmPython.connect(
            dsn=f"{DM_SERVER}:{DM_PORT}",
            user=DM_USER,
            password=DM_PASSWORD,
        )

        # 如果指定了 Schema，切换当前会话的 Schema
        if DM_SCHEMA:
            # 验证 Schema 名称安全性
            if not validate_schema_name(DM_SCHEMA):
                logger.error(f"无效的 Schema 名称: {DM_SCHEMA}")
                raise ValueError(f"无效的 Schema 名称: {DM_SCHEMA}")
            
            cursor = conn.cursor()
            try:
                # 使用参数化方式设置 Schema（达梦不支持参数化 SET SCHEMA，所以需要严格验证）
                cursor.execute(f"SET SCHEMA {DM_SCHEMA}")
                logger.info(f"成功切换到 Schema: {DM_SCHEMA}")
            finally:
                cursor.close()

        logger.info("数据库连接成功")
        return conn
    except ValueError as e:
        logger.error(f"验证错误: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"连接失败: {str(e)}")
        raise ConnectionError(f"数据库连接失败: {str(e)}")


# 3. 定义工具：查询数据
@mcp.tool()
def query_db(sql: str) -> str:
    """
    执行 SQL 查询。
    注意：仅允许 SELECT 语句，禁止危险操作。
    """
    # 清理和验证 SQL
    sql = sql.strip()
    if not sql:
        return "错误：SQL 语句不能为空。"
    
    # 检查是否为 SELECT 语句
    sql_upper = sql.upper()
    if not sql_upper.startswith("SELECT"):
        logger.warning(f"尝试执行非 SELECT 语句: {sql[:50]}...")
        return "错误：为了安全，仅支持 SELECT 查询。"
    
    # 检查危险关键字（防止 UNION SELECT、子查询注入等）
    dangerous_patterns = [
        'DROP ', 'DELETE ', 'UPDATE ', 'INSERT ', 'ALTER ', 
        'CREATE ', 'TRUNCATE ', 'EXEC ', 'EXECUTE '
    ]
    for pattern in dangerous_patterns:
        if pattern in sql_upper:
            logger.warning(f"检测到危险操作: {pattern}")
            return f"错误：检测到危险操作 '{pattern.strip()}'，已被阻止。"
    
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(sql)
            
            # 获取列名
            if cursor.description:
                columns = [desc[0] for desc in cursor.description]
                # 获取数据
                rows = cursor.fetchall()
                
                result = f"查询成功 (共{len(rows)}条):\n"
                result += " | ".join(columns) + "\n"
                result += "-" * 50 + "\n"
                for row in rows:
                    result += " | ".join([str(item) if item is not None else 'NULL' for item in row]) + "\n"
                
                logger.info(f"查询执行成功，返回 {len(rows)} 条记录")
                return result
            else:
                return "查询执行成功，但没有返回数据。"
        finally:
            cursor.close()
    except ConnectionError as e:
        logger.error(f"连接错误: {str(e)}")
        return str(e)
    except Exception as e:
        logger.error(f"查询执行错误: {str(e)}")
        return f"执行错误: {str(e)}"
    finally:
        if conn:
            try:
                conn.close()
            except:
                pass


# 4. 定义工具：获取表结构
@mcp.tool()
def get_table_structure(table_name: str) -> str:
    """
    获取表结构信息
    """
    # 验证表名
    if not table_name or not table_name.strip():
        return "错误：表名不能为空。"
    
    table_name = table_name.strip()
    
    # 验证表名合法性（防止 SQL 注入）
    if not validate_table_name(table_name):
        logger.warning(f"无效的表名格式: {table_name}")
        return f"错误：表名 '{table_name}' 包含非法字符。只允许字母、数字和下划线。"
    
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        try:
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
                logger.info(f"表 '{table_name}' 不存在或无权访问")
                return f"表 '{table_name}' 不存在或无权访问。"

            result = f"表结构 [{table_name}]:\n"
            result += "列名 | 类型 | 长度\n"
            result += "-" * 30 + "\n"
            for row in rows:
                length_str = str(row[2]) if row[2] is not None else 'N/A'
                result += f"{row[0]} | {row[1]} | {length_str}\n"

            logger.info(f"成功获取表 '{table_name}' 的结构，共 {len(rows)} 个字段")
            return result
        finally:
            cursor.close()
    except ConnectionError as e:
        logger.error(f"连接错误: {str(e)}")
        return str(e)
    except Exception as e:
        logger.error(f"获取表结构错误: {str(e)}")
        return f"获取结构错误: {str(e)}"
    finally:
        if conn:
            try:
                conn.close()
            except:
                pass