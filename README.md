# CC-DingHook

🔔 **Claude Code 全局钉钉通知工具** - 在每次 Claude Code 执行完成后自动发送钉钉通知

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Install](https://img.shields.io/badge/Install-One%20Command-orange.svg)](#-快速安装)

## ✨ 特性

- 🌍 **全局安装** - 一次安装，所有项目生效
- ⚡ **即开即用** - 免编译，直接下载使用
- 🔧 **灵活配置** - 支持自定义消息模板和通知条件
- 🔒 **安全可靠** - 支持钉钉安全签名
- 📱 **美观通知** - Markdown 格式的精美消息
- 🎯 **智能过滤** - 可配置成功/失败/错误通知
- 📊 **响应统计** - 包含响应时长、内容摘要等信息

## 🚀 快速安装

### 方法一：一键安装（推荐）

```bash
curl -fsSL https://raw.githubusercontent.com/SundayDX/cc-dinghook/master/install.sh | bash
```

### 方法二：手动安装

```bash
# 下载脚本
mkdir -p ~/.local/bin
curl -fsSL https://raw.githubusercontent.com/SundayDX/cc-dinghook/master/cc-hook.py -o ~/.local/bin/cc-hook
chmod +x ~/.local/bin/cc-hook

# 安装 hook
~/.local/bin/cc-hook install

# 添加到 PATH（如果需要）
echo 'export PATH="$PATH:~/.local/bin"' >> ~/.bashrc
source ~/.bashrc
```

### 方法三：使用 Git 克隆

```bash
git clone https://github.com/SundayDX/cc-dinghook.git
cd cc-dinghook
python3 cc-hook.py install
cp cc-hook.py ~/.local/bin/cc-hook
chmod +x ~/.local/bin/cc-hook
```

## 📋 使用方法

### 基本命令

```bash
# 查看帮助
cc-hook --help

# 查看当前配置
cc-hook config --show

# 测试通知
cc-hook config --test

# 启用/禁用通知
cc-hook config --enable true
cc-hook config --enable false
```

### 配置钉钉

1. **创建钉钉机器人**
   - 在钉钉群中点击"群设置" → "智能群助手" → "添加机器人"
   - 选择"自定义机器人"
   - 设置机器人名称和头像
   - 选择安全设置（推荐使用"加签"）
   - 获取 Webhook URL 和密钥

2. **配置 Webhook**
   ```bash
   # 使用您的 access token
   cc-hook config --access-token "YOUR_TOKEN"
   
   # 设置安全密钥（如果使用加签）
   cc-hook config --secret "YOUR_SECRET"
   ```

3. **测试配置**
   ```bash
   cc-hook config --test
   ```

### 启用 Claude Code Hook

1. 打开 Claude Code 设置
2. 找到 "Hooks" 配置项
3. 启用 "Post-response hook"
4. 设置 hook 路径为：`~/.claude/hooks/post-response`

现在每次 Claude Code 完成对用户 prompt 的响应后，都会自动发送钉钉通知，提醒您可以进行下一次的 prompt！

## ⚙️ 配置选项

配置文件位置：`~/.cc-hook-config.json`

### 完整配置示例

```json
{
  "access_token": "YOUR_TOKEN",
  "secret": "YOUR_SECRET_KEY",
  "enabled": true,
  "message_template": {
    "title": "Claude Code 执行完成",
    "include_duration": true,
    "include_exit_code": true,
    "include_working_dir": true
  },
  "notifications": {
    "on_success": true,
    "on_failure": true,
    "on_error": true
  }
}
```

### 配置说明

| 选项 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `access_token` | string | - | 钉钉机器人 Access Token |
| `secret` | string | "" | 安全密钥（可选） |
| `enabled` | boolean | true | 是否启用通知 |
| `message_template.title` | string | "Claude Code 执行完成" | 消息标题 |
| `message_template.include_duration` | boolean | true | 是否包含执行时长 |
| `message_template.include_exit_code` | boolean | true | 是否包含退出码 |
| `message_template.include_working_dir` | boolean | true | 是否包含工作目录 |
| `notifications.on_success` | boolean | true | 成功时是否通知 |
| `notifications.on_failure` | boolean | true | 失败时是否通知 |
| `notifications.on_error` | boolean | true | 错误时是否通知 |

## 📱 消息格式

工具会发送如下格式的钉钉消息：

```markdown
# Claude Code 执行完成

✅ **执行状态**: 成功
📝 **执行的命令**: `npm run build`
🔢 **退出码**: 0
⏱️ **执行时长**: 3.45秒
📁 **工作目录**: `/home/user/my-project`
🕐 **完成时间**: 2024-01-13 10:30:45
```

## 🔧 高级用法

### 直接发送通知

```bash
cc-hook send \
  --command "npm run test" \
  --exit-code 0 \
  --duration 5.2 \
  --working-dir "/home/user/project"
```

### 自定义消息模板

编辑 `~/.cc-hook-config.json`：

```json
{
  "message_template": {
    "title": "🤖 Claude Code 任务完成",
    "include_duration": true,
    "include_exit_code": false,
    "include_working_dir": false
  }
}
```

### 批量配置

```bash
# 一次性设置所有配置
cc-hook config \
  --access-token "YOUR_TOKEN" \
  --secret "YOUR_SECRET" \
  --enable true
```

## 🛡️ 安全说明

- 🔐 **推荐使用安全密钥** - 在钉钉机器人设置中启用"加签"
- 🔒 **保护 Webhook URL** - 不要在公开场所分享
- 🚫 **定期轮换密钥** - 建议定期更换安全密钥
- 📊 **控制通知频率** - 可通过配置禁用某些类型的通知

## 🔍 故障排除

### 常见问题

#### 1. 通知未发送

**症状**：执行后没有收到钉钉消息

**解决方案**：
```bash
# 检查配置
cc-hook config --show

# 检查网络连接
curl -I "https://oapi.dingtalk.com"

# 测试 webhook
cc-hook config --test
```

#### 2. Hook 未执行

**症状**：Claude Code 完成响应但没有触发通知

**解决方案**：
```bash
# 检查 hook 文件权限
ls -la ~/.claude/hooks/post-response

# 设置执行权限
chmod +x ~/.claude/hooks/post-response

# 验证 Python 3
python3 --version
```

#### 3. 权限错误

**解决方案**：
```bash
# 修复文件权限
chmod 755 ~/.claude/hooks/post-response
chmod 600 ~/.cc-hook-config.json

# 检查目录权限
ls -ld ~/.claude/
```

#### 4. 配置文件错误

**解决方案**：
```bash
# 验证 JSON 格式
python3 -m json.tool ~/.cc-hook-config.json

# 重置配置
rm ~/.cc-hook-config.json
cc-hook config --show  # 会重新创建
```

### 调试模式

```bash
# 启用详细日志
export CC_HOOK_DEBUG=true
cc-hook config --test

# 手动执行 hook
~/.claude/hooks/post-response "test-prompt" "test-response" 1.5
```

## 📦 卸载

```bash
# 删除脚本
rm -f ~/.local/bin/cc-hook

# 删除 hook
rm -f ~/.claude/hooks/post-response

# 删除配置
rm -f ~/.cc-hook-config.json

# 清理环境变量
sed -i '/cc-hook/d' ~/.bashrc ~/.zshrc 2>/dev/null || true
```

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

### 开发环境设置

```bash
git clone https://github.com/SundayDX/cc-dinghook.git
cd cc-dinghook

# 创建虚拟环境（可选）
python3 -m venv venv
source venv/bin/activate

# 测试
python3 cc-hook.py --help
```

### 提交规范

- 🐛 Bug 修复：`fix: 修复权限错误`
- ✨ 新功能：`feat: 添加自定义模板支持`
- 📝 文档：`docs: 更新安装说明`
- 🔧 配置：`chore: 更新依赖版本`

## 📄 许可证

本项目采用 [MIT License](LICENSE) 开源协议。

## 🙏 致谢

- [Claude Code](https://claude.ai/code) - 强大的 AI 编程助手
- [DingTalk](https://open.dingtalk.com) - 钉钉开放平台
- 所有贡献者和使用者

## 📞 联系

- 📧 Email: [your-email@example.com]
- 🐛 Issues: [GitHub Issues](https://github.com/SundayDX/cc-dinghook/issues)
- 💬 讨论: [GitHub Discussions](https://github.com/SundayDX/cc-dinghook/discussions)

---

⭐ 如果这个工具对您有帮助，请给个 Star！