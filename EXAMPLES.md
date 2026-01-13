# 使用示例

本文档提供了 CC-DingHook 的详细使用示例和最佳实践。

## 🚀 快速开始示例

### 基础使用

```bash
# 1. 一键安装
curl -fsSL https://raw.githubusercontent.com/SundayDX/cc-dinghook/main/install.sh | bash

# 2. 配置钉钉（使用默认 URL 已预置）
cc-hook config --test

# 3. 启用 Claude Code hook
# 在 Claude Code 设置中启用 post-response hook
# 路径: ~/.claude/hooks/post-response
```

## 📋 配置示例

### 1. 基础配置

```bash
# 查看当前配置
cc-hook config --show

# 设置 access token
cc-hook config --access-token "YOUR_TOKEN"

# 设置安全密钥
cc-hook config --secret "YOUR_SECRET_KEY"

# 启用通知
cc-hook config --enable true
```

### 2. 高级配置

```bash
# 批量设置配置
cc-hook config \
  --access-token "YOUR_TOKEN" \
  --secret "YOUR_SECRET" \
  --enable true

# 测试通知
cc-hook config --test

# 禁用通知
cc-hook config --enable false
```

## 📱 消息模板示例

### 默认消息模板

```json
{
  "message_template": {
    "title": "Claude Code 执行完成",
    "include_duration": true,
    "include_exit_code": true,
    "include_working_dir": true
  }
}
```

**生成的消息**：
```markdown
# Claude Code 执行完成

✅ **执行状态**: 成功
📝 **执行的命令**: `npm run build`
🔢 **退出码**: 0
⏱️ **执行时长**: 3.45秒
📁 **工作目录**: `/home/user/my-project`
🕐 **完成时间**: 2024-01-13 10:30:45
```

### 简化消息模板

```json
{
  "message_template": {
    "title": "🤖 任务完成",
    "include_duration": false,
    "include_exit_code": false,
    "include_working_dir": false
  }
}
```

**生成的消息**：
```markdown
# 🤖 任务完成

✅ **执行状态**: 成功
📝 **执行的命令**: `npm run build`
🕐 **完成时间**: 2024-01-13 10:30:45
```

### 详细信息模板

```json
{
  "message_template": {
    "title": "🔧 Claude Code 执行报告",
    "include_duration": true,
    "include_exit_code": true,
    "include_working_dir": true
  }
}
```

## 🎯 通知控制示例

### 仅失败通知

```json
{
  "notifications": {
    "on_success": false,
    "on_failure": true,
    "on_error": true
  }
}
```

### 仅成功通知

```json
{
  "notifications": {
    "on_success": true,
    "on_failure": false,
    "on_error": false
  }
}
```

### 全部通知

```json
{
  "notifications": {
    "on_success": true,
    "on_failure": true,
    "on_error": true
  }
}
```

## 🔧 实际使用场景

### 场景1：前端开发

```bash
# 配置仅通知构建结果
cc-hook config --access-token "BUILD_WEBHOOK_TOKEN"

# 手动测试构建通知
cc-hook send \
  --command "npm run build" \
  --exit-code 0 \
  --duration 12.5 \
  --working-dir "/home/user/frontend-project"
```

### 场景2：后端开发

```bash
# 配置测试通知
cc-hook config --access-token "TEST_WEBHOOK_TOKEN"

# 手动测试通知
cc-hook send \
  --command "npm run test:unit" \
  --exit-code 1 \
  --duration 8.3 \
  --working-dir "/home/user/backend-project"
```

### 场景3：DevOps 部署

```bash
# 配置部署通知
cc-hook config --access-token "DEPLOY_WEBHOOK_TOKEN"

# 模拟部署成功
cc-hook send \
  --command "deploy.sh production" \
  --exit-code 0 \
  --duration 45.7 \
  --working-dir "/home/user/devops"
```

## 🛠️ 高级配置示例

### 1. 多环境配置

为不同环境创建不同的 access token：

```bash
# 开发环境
cc-hook config --access-token "DEV_WEBHOOK_TOKEN"
cp ~/.cc-hook-config.json ~/.cc-hook-config.dev.json

# 测试环境
cc-hook config --access-token "TEST_WEBHOOK_TOKEN"
cp ~/.cc-hook-config.json ~/.cc-hook-config.test.json

# 生产环境
cc-hook config --access-token "PROD_WEBHOOK_TOKEN"
cp ~/.cc-hook-config.json ~/.cc-hook-config.prod.json

# 切换环境
alias cc-hook-dev='cp ~/.cc-hook-config.dev.json ~/.cc-hook-config.json && cc-hook'
alias cc-hook-test='cp ~/.cc-hook-config.test.json ~/.cc-hook-config.json && cc-hook'
alias cc-hook-prod='cp ~/.cc-hook-config.prod.json ~/.cc-hook-config.json && cc-hook'
```

### 2. 团队配置

创建团队共享配置：

```json
{
  "access_token": "TEAM_TOKEN",
  "secret": "TEAM_SECRET",
  "enabled": true,
  "message_template": {
    "title": "👥 团队构建通知",
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

## 🔍 调试示例

### 1. 测试消息发送

```bash
# 测试成功消息
cc-hook send --command "echo success" --exit-code 0 --duration 0.5

# 测试失败消息
cc-hook send --command "false" --exit-code 1 --duration 0.1

# 测试长执行时间
cc-hook send --command "sleep 10" --exit-code 0 --duration 10.0
```

### 2. 手动执行 Hook

```bash
# 模拟 Claude Code 执行
~/.claude/hooks/post-exec "npm run test" 0 5.2 "/home/user/project"

# 测试失败场景
~/.claude/hooks/post-exec "npm run build" 1 8.7 "/home/user/project"

# 测试错误场景
~/.claude/hooks/post-exec "invalid-command" 127 0.1 "/home/user/project"
```

### 3. 配置验证

```bash
# 验证 JSON 配置格式
python3 -m json.tool ~/.cc-hook-config.json

# 检查 hook 文件权限
ls -la ~/.claude/hooks/post-exec

# 验证 Python 环境
python3 --version
which python3
```

## 📊 性能监控示例

### 监控执行时间

```bash
# 创建监控脚本
cat > monitor-execution.sh << 'EOF'
#!/bin/bash
START_TIME=$(date +%s.%N)
COMMAND="$*"

# 执行命令
$COMMAND
EXIT_CODE=$?

END_TIME=$(date +%s.%N)
DURATION=$(echo "$END_TIME - $START_TIME" | bc)

# 发送通知
cc-hook send \
  --command "$COMMAND" \
  --exit-code $EXIT_CODE \
  --duration $DURATION \
  --working-dir "$PWD"
EOF

chmod +x monitor-execution.sh

# 使用监控脚本
./monitor-execution.sh npm run build
```

## 🚨 故障排除示例

### 问题1：通知未发送

```bash
# 检查配置
cc-hook config --show

# 测试网络连接
curl -I "https://oapi.dingtalk.com"

# 手动测试 webhook
curl -X POST "YOUR_WEBHOOK_URL" \
  -H "Content-Type: application/json" \
  -d '{"msgtype":"text","text":{"content":"Test"}}'
```

### 问题2：Hook 未执行

```bash
# 检查 hook 文件
cat ~/.claude/hooks/post-exec

# 手动测试 hook
~/.claude/hooks/post-exec "test" 0 1.0 "/tmp"

# 检查权限
ls -la ~/.claude/hooks/
```

### 问题3：权限错误

```bash
# 修复权限
chmod 755 ~/.claude/hooks/post-exec
chmod 600 ~/.cc-hook-config.json

# 检查目录权限
ls -ld ~/.claude/
```

## 🎨 自定义示例

### 自定义消息标题

```bash
# 编辑配置文件
vim ~/.cc-hook-config.json

# 修改 title
{
  "message_template": {
    "title": "🚀 我的构建通知"
  }
}
```

### 条件通知

```bash
# 创建智能通知脚本
cat > smart-notify.sh << 'EOF'
#!/bin/bash
COMMAND="$1"
EXIT_CODE="$2"
DURATION="$3"
WORKING_DIR="$4"

# 根据命令类型决定是否通知
if [[ "$COMMAND" == *"test"* ]]; then
  # 测试命令仅在失败时通知
  if [ "$EXIT_CODE" -eq 0 ]; then
    exit 0
  fi
fi

# 执行通知
cc-hook send --command "$COMMAND" --exit-code "$EXIT_CODE" --duration "$DURATION" --working-dir "$WORKING_DIR"
EOF

chmod +x smart-notify.sh
```

## 📚 最佳实践

1. **定期更新**：保持工具为最新版本
2. **安全密钥**：使用钉钉安全签名
3. **通知控制**：合理配置通知条件避免噪音
4. **配置备份**：重要配置进行备份
5. **测试验证**：定期测试通知功能

## 🆘 获取帮助

```bash
# 查看帮助
cc-hook --help
cc-hook config --help
cc-hook send --help

# 查看配置
cc-hook config --show

# 测试功能
cc-hook config --test
```

---

更多示例和最佳实践欢迎在 [GitHub Discussions](https://github.com/SundayDX/cc-dinghook/discussions) 中分享！