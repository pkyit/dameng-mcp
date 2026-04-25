# 达梦数据库 MCP 服务器 (DM-MCP)

一个基于 FastMCP 的达梦数据库 Model Context Protocol 服务器，提供安全的数据库查询和表结构获取功能。

## 功能特性

- 🔒 **安全查询**: 仅支持 SELECT 语句，防止数据修改操作
- 📊 **表结构查询**: 获取数据库表结构信息
- 🔧 **环境变量配置**: 通过环境变量动态配置数据库连接
- 🚀 **MCP 协议**: 基于 Model Context Protocol 标准

## 安装

### 从 PyPI 安装（推荐）

```bash
pip install dm-mcp
```

### 从源码安装

```bash
git clone https://github.com/yourusername/dm-mcp.git
cd dm-mcp
pip install -e .
```

## 环境变量配置

设置以下环境变量来配置数据库连接：

```bash
# 数据库服务器地址
export DM_SERVER=localhost

# 数据库端口 (默认: 5236)
export DM_PORT=5236

# 数据库用户名
export DM_USER=SYSDBA

# 数据库密码
export DM_PASSWORD=your_password

# 数据库 Schema (可选，默认使用用户名)
export DM_SCHEMA=PRODUCTION
```

## MCP 客户端配置

### Claude Desktop 配置

在 Claude Desktop 的配置文件中添加以下配置：

**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "dm-mcp": {
      "command": "dm-mcp",
      "env": {
        "DM_SERVER": "localhost",
        "DM_PORT": "5236",
        "DM_USER": "SYSDBA",
        "DM_PASSWORD": "your_password",
        "DM_SCHEMA": "PRODUCTION"
      }
    }
  }
}
```

### 其他 MCP 客户端

对于其他支持 MCP 的客户端，请参考相应的配置文件格式。

## 运行服务器

### 直接运行

```bash
# 使用环境变量运行
dm-mcp

# 或者直接设置环境变量运行
DM_SERVER=localhost DM_PORT=5236 DM_USER=SYSDBA DM_PASSWORD=your_password DM_SCHEMA=PRODUCTION dm-mcp
```

### 开发模式

```bash
# 从源码运行
python -m dm_mcp
```

## 可用工具

### 1. query_db(sql: str)
执行 SQL 查询语句。

**参数:**
- `sql`: SELECT 查询语句

**示例:**
```sql
-- 简单查询
SELECT * FROM RESOURCES.EMPLOYEE WHERE ROWNUM <= 5;

-- 聚合查询
SELECT TITLE, COUNT(*) as 人数, AVG(SALARY) as 平均工资 
FROM RESOURCES.EMPLOYEE 
GROUP BY TITLE 
ORDER BY 平均工资 DESC;

-- 多表关联查询
SELECT PC.NAME as 主分类, PSC.NAME as 子分类, COUNT(P.PRODUCTID) as 产品数量 
FROM PRODUCTION.PRODUCT_CATEGORY PC 
JOIN PRODUCTION.PRODUCT_SUBCATEGORY PSC ON PC.PRODUCT_CATEGORYID = PSC.PRODUCT_CATEGORYID 
LEFT JOIN PRODUCTION.PRODUCT P ON PSC.PRODUCT_SUBCATEGORYID = P.PRODUCT_SUBCATEGORYID 
GROUP BY PC.NAME, PSC.NAME 
ORDER BY PC.NAME, PSC.NAME;
```

**返回:** 查询结果的格式化字符串，包含列名和数据行。

**⚠️ 重要提示:**
- 达梦数据库需要使用 Schema 前缀（如 `RESOURCES.EMPLOYEE`、`PRODUCTION.PRODUCT`）
- 如果不确定表所在的 Schema，可以先查询：`SELECT OWNER, TABLE_NAME FROM ALL_TABLES WHERE TABLE_NAME = '表名'`
- 支持复杂的 SQL 查询，包括聚合函数、分组、排序、多表关联等

### 2. get_table_structure(table_name: str)
获取指定表的结构信息。

**参数:**
- `table_name`: 表名（不区分大小写，会自动转换为大写）

**示例:**
```python
# 获取 EMPLOYEE 表结构
get_table_structure("EMPLOYEE")

# 获取 PRODUCT 表结构
get_table_structure("PRODUCT")
```

**返回:** 表的列信息，包括列名、数据类型和长度。

**⚠️ 重要提示:**
- 表名不需要加 Schema 前缀，工具会自动在当前 Schema 中查找
- 如果表不存在或无权访问，会返回相应的错误信息

## 项目结构

```
dm-mcp/
├── dm_mcp/
│   ├── __init__.py      # MCP 服务器核心代码
│   └── __main__.py      # 程序入口
├── pyproject.toml       # 项目配置
├── mcp-config.json      # MCP 客户端配置示例
├── requirements.txt     # Python 依赖
├── README.md           # 项目文档
└── LICENSE            # Apache 许可证
```

## 开发说明

### 代码结构

- `__init__.py`: 包含 MCP 服务器初始化、数据库连接函数和工具定义
- `__main__.py`: 程序入口，启动 MCP 服务器

### 安全考虑

- 仅允许 SELECT 查询，防止数据修改
- 通过环境变量配置敏感信息
- 连接失败时返回错误信息而不是抛出异常
- Schema 名称和表名经过严格验证，防止 SQL 注入

### 使用示例

#### 示例 1：查询员工信息

```python
# 查询前5条员工记录
query_db("SELECT EMPLOYEEID, LOGINID, TITLE, SALARY FROM RESOURCES.EMPLOYEE WHERE ROWNUM <= 5")

# 输出：
# 查询成功 (共5条):
# EMPLOYEEID | LOGINID | TITLE | SALARY
# --------------------------------------------------
# 1 | L1 | 总经理 | 40000.0
# 2 | L2 | 销售经理 | 26000.0
# ...
```

#### 示例 2：统计产品分类

```python
# 查询产品分类统计
query_db("""
    SELECT PC.NAME as 主分类, 
           COUNT(PSC.PRODUCT_SUBCATEGORYID) as 子分类数量 
    FROM PRODUCTION.PRODUCT_CATEGORY PC 
    LEFT JOIN PRODUCTION.PRODUCT_SUBCATEGORY PSC 
        ON PC.PRODUCT_CATEGORYID = PSC.PRODUCT_CATEGORYID 
    GROUP BY PC.NAME 
    ORDER BY PC.NAME
""")

# 输出：
# 查询成功 (共7条):
# 主分类 | 子分类数量
# --------------------------------------------------
# 小说 | 6
# 文学 | 7
# 计算机 | 8
# ...
```

#### 示例 3：获取表结构

```python
# 获取 EMPLOYEE 表结构
get_table_structure("EMPLOYEE")

# 输出：
# 表结构 [EMPLOYEE]:
# 列名 | 类型 | 长度
# ------------------------------
# EMPLOYEEID | INT | 4
# NATIONALNO | VARCHAR | 18
# PERSONID | INT | 4
# ...
```

## 发布

### 构建发布包

```bash
# 安装构建工具
pip install build

# 构建发布包
python -m build
```

### 上传到 PyPI

```bash
# 安装上传工具
pip install twine

# 上传到 PyPI
twine upload dist/*
```

## 许可证

本项目采用 Apache License 2.0 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 贡献

欢迎提交 Issue 和 Pull Request 来改进这个项目！

## 联系方式

如有问题或建议，请通过 GitHub Issues 联系我们。
