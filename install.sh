#!/bin/bash

set -e

INSTALL_DIR="$HOME/.local/bin"
CONFIG_DIR="$HOME/.claude"
SCRIPT_NAME="cc-hook"
SCRIPT_URL="https://raw.githubusercontent.com/SundayDX/cc-dinghook/master/cc-hook.py"

echo "🚀 开始安装 Claude Code Hook 工具..."

mkdir -p "$INSTALL_DIR"
mkdir -p "$CONFIG_DIR/hooks"

echo "📥 下载脚本..."
if command -v curl >/dev/null 2>&1; then
    curl -fsSL "$SCRIPT_URL" -o "$INSTALL_DIR/$SCRIPT_NAME"
elif command -v wget >/dev/null 2>&1; then
    wget -q "$SCRIPT_URL" -O "$INSTALL_DIR/$SCRIPT_NAME"
else
    echo "❌ 错误: 需要安装 curl 或 wget"
    exit 1
fi

chmod +x "$INSTALL_DIR/$SCRIPT_NAME"

if ! command -v python3 >/dev/null 2>&1; then
    echo "❌ 错误: 需要安装 Python 3"
    exit 1
fi

echo "🔧 安装 hook..."
"$INSTALL_DIR/$SCRIPT_NAME" install

if [[ ":$PATH:" != *":$INSTALL_DIR:"* ]]; then
    echo "📝 添加 $INSTALL_DIR 到 PATH"
    echo "export PATH=\"\$PATH:$INSTALL_DIR\"" >> "$HOME/.bashrc"
    echo "export PATH=\"\$PATH:$INSTALL_DIR\"" >> "$HOME/.zshrc"
fi

echo ""
echo "🎉 安装完成！"
echo ""
echo "📋 使用方法:"
echo "  cc-hook config --test                    # 测试通知"
echo "  cc-hook config --show                    # 查看配置"
echo "  cc-hook config --access-token YOUR_TOKEN # 设置 access token"
echo ""
echo "⚠️  请在 Claude Code 设置中启用 post-response hook"
echo "   Hook 路径: $CONFIG_DIR/hooks/post-response"