# 贡献指南

感谢您对 CC-DingHook 项目的关注！我们欢迎各种形式的贡献。

## 🤝 如何贡献

### 报告问题

如果您发现了 bug 或有功能建议，请：

1. 先搜索 [已有的 Issues](https://github.com/SundayDX/cc-dinghook/issues)
2. 如果没有相关问题，请创建新的 Issue
3. 使用以下模板：

#### Bug 报告模板

```markdown
## 问题描述
简要描述遇到的问题

## 复现步骤
1. 执行命令 `...`
2. 点击 `...`
3. 看到错误 `...`

## 期望行为
描述您期望发生的情况

## 实际行为
描述实际发生的情况

## 环境信息
- OS: [例如 macOS 13.0]
- Python 版本: [例如 3.9.0]
- Claude Code 版本: [例如 1.0.0]

## 其他信息
任何其他有助于解决问题的信息
```

#### 功能请求模板

```markdown
## 功能描述
简要描述您希望添加的功能

## 使用场景
描述这个功能的使用场景和价值

## 解决方案
描述您期望的实现方案（可选）

## 替代方案
描述您考虑过的其他解决方案（可选）
```

### 提交代码

1. **Fork 项目**
   ```bash
   git clone https://github.com/YOUR_USERNAME/cc-dinghook.git
   cd cc-dinghook
   ```

2. **创建功能分支**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **进行开发**
   - 遵循现有的代码风格
   - 添加必要的注释和文档
   - 确保测试通过

4. **提交代码**
   ```bash
   git add .
   git commit -m "feat: 添加新功能描述"
   ```

5. **推送并创建 PR**
   ```bash
   git push origin feature/your-feature-name
   ```

## 📝 开发规范

### 代码风格

- 使用 4 个空格缩进
- 行长度不超过 100 字符
- 函数和类使用 snake_case
- 常量使用 UPPER_CASE

### 提交信息规范

使用 [Conventional Commits](https://www.conventionalcommits.org/) 规范：

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

#### 类型说明

- `feat`: 新功能
- `fix`: 修复 bug
- `docs`: 文档更新
- `style`: 代码格式调整（不影响功能）
- `refactor`: 重构代码
- `test`: 添加或修改测试
- `chore`: 构建过程或辅助工具的变动

#### 示例

```bash
feat: 支持自定义消息模板
fix: 修复权限错误导致 hook 无法执行的问题
docs: 更新 README 安装说明
test: 添加发送消息的单元测试
```

### 测试

在提交前请确保：

1. 代码能正常运行
2. 所有功能都经过测试
3. 没有引入新的 bug

```bash
# 基本功能测试
python3 cc-hook.py --help
python3 cc-hook.py config --show

# 测试 hook 安装
python3 cc-hook.py install
```

## 🎯 贡献方向

我们欢迎以下方向的贡献：

### 功能增强

- [ ] 支持更多通知平台（企业微信、Slack 等）
- [ ] 添加消息模板编辑器
- [ ] 支持批量配置管理
- [ ] 添加 Web UI 配置界面
- [ ] 支持条件通知（基于命令类型、执行时长等）

### 开发体验

- [ ] 添加单元测试
- [ ] 添加集成测试
- [ ] 改进错误处理和日志
- [ ] 添加类型提示
- [ ] 性能优化

### 文档和示例

- [ ] 添加更多使用场景示例
- [ ] 创建视频教程
- [ ] 翻译文档到英文
- [ ] 添加 FAQ
- [ ] 创建最佳实践指南

## 📧 联系方式

如果您有任何问题或建议，欢迎通过以下方式联系：

- 📧 Email: [your-email@example.com]
- 💬 GitHub Issues: [创建 Issue](https://github.com/SundayDX/cc-dinghook/issues/new)
- 🔄 GitHub Discussions: [参与讨论](https://github.com/SundayDX/cc-dinghook/discussions)

## 🏆 贡献者

感谢所有为项目做出贡献的开发者！

<!-- 这里会自动显示贡献者列表 -->

## 📄 许可证

通过贡献代码，您同意您的贡献将在 [MIT License](LICENSE) 下发布。

---

再次感谢您的贡献！🙏