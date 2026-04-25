# 更新日志

## [1.0.2] - 2026-04-26

### 新增
- 添加详细的使用示例文档，包括：
  - 简单查询示例（员工信息查询）
  - 聚合查询示例（按职位统计薪资）
  - 多表关联查询示例（产品分类统计）
  - 表结构查询示例
- 在 README.md 中添加重要提示章节，说明 Schema 前缀的使用规范
- 添加 SQL 查询最佳实践和注意事项

### 改进
- 优化 `query_db` 工具的文档，增加更多实际使用场景
- 优化 `get_table_structure` 工具的文档，明确表名处理规则
- 完善安全考虑章节，补充 SQL 注入防护说明

### 修复
- 修正文档中的示例代码，使用正确的 Schema 前缀格式
- 统一文档中的代码示例风格

### 技术要点
- **Schema 前缀要求**: 达梦数据库查询时必须使用 Schema 前缀（如 `RESOURCES.EMPLOYEE`、`PRODUCTION.PRODUCT`）
- **Schema 查询方法**: 可通过 `SELECT OWNER, TABLE_NAME FROM ALL_TABLES WHERE TABLE_NAME = '表名'` 查询表所在的 Schema
- **工具差异**: 
  - `query_db`: 需要在 SQL 中显式指定 Schema 前缀
  - `get_table_structure`: 自动在当前 Schema 中查找，无需指定前缀

---

## [1.0.1] - 2026-04-25

### 新增
- 初始版本发布
- 支持基本的 SQL 查询功能（仅 SELECT）
- 支持表结构查询功能
- 环境变量配置支持
- MCP 协议集成

### 安全特性
- SQL 注入防护
- 仅允许 SELECT 查询
- Schema 名称和表名验证
