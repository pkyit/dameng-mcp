# 发布检查清单

## ✅ 已完成的项目文件
- [x] `pyproject.toml` - 项目配置和元数据
- [x] `README.md` - 详细的使用文档
- [x] `LICENSE` - Apache 2.0 许可证
- [x] `MANIFEST.in` - 发布文件清单
- [x] `mcp-config.json` - MCP 客户端配置示例
- [x] `requirements.txt` - 依赖列表
- [x] `dm_mcp/__init__.py` - 核心服务器代码
- [x] `dm_mcp/__main__.py` - 命令行入口

## 🔧 发布步骤

### 1. 更新版本号
在 `pyproject.toml` 中更新版本号：
```toml
version = "1.0.0"
```

### 2. 更新作者信息
在 `pyproject.toml` 中更新您的信息：
```toml
authors = [
    {name = "Your Name", email = "your.email@example.com"},
]
```

### 3. 更新仓库地址
在 `pyproject.toml` 中更新 GitHub 仓库地址：
```toml
[project.urls]
Homepage = "https://github.com/yourusername/dm-mcp"
Repository = "https://github.com/yourusername/dm-mcp"
```

### 4. 构建发布包
```bash
pip install build
python -m build
```

### 5. 测试发布包
```bash
pip install dist/dm_mcp-1.0.0.tar.gz
dm-mcp --help  # 测试安装
```

### 6. 上传到 PyPI
```bash
pip install twine
twine upload dist/*
```

## 📦 发布后验证

### 安装测试
```bash
pip install dm-mcp
dm-mcp  # 应该能启动服务器
```

### MCP 客户端配置测试
确保 `mcp-config.json` 中的配置在 Claude Desktop 或其他 MCP 客户端中工作正常。

## 🏷️ 版本管理

- **1.0.0**: 初始发布版本
- 遵循 [语义化版本](https://semver.org/) 规范

## 📋 注意事项

1. **敏感信息**: 确保不在代码中硬编码数据库密码
2. **测试**: 在发布前在测试环境中充分测试
3. **文档**: 保持 README.md 文档的准确性和完整性
4. **许可证**: 确认 Apache 2.0 许可证适合您的使用场景
