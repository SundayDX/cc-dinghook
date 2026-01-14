#!/usr/bin/env python3
"""
Claude Code Hook Tool - 全局钉钉通知工具
在每次 Claude Code 执行完成后发送钉钉通知

使用方法：
  curl -sSL https://your-repo/cc-hook | python3 -
  # 或
  wget -qO- https://your-repo/cc-hook | python3 -

配置文件位置：~/.cc-hook-config.json
"""

import json
import os
import sys
import time
import subprocess
import argparse
from pathlib import Path
from datetime import datetime
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
from urllib.parse import urlencode
import hashlib
import hmac
import base64

DEFAULT_CONFIG = {
    "access_token": "",
    "secret": "",
    "enabled": True,
    "message_template": {
        "title": "Claude Code 执行完成",
        "include_duration": True,
        "include_exit_code": True,
        "include_working_dir": True
    },
    "notifications": {
        "on_success": True,
        "on_failure": True,
        "on_error": True
    }
}

CONFIG_PATH = Path.home() / ".cc-hook-config.json"


def load_config():
    if CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
                config = json.load(f)
            merged_config = DEFAULT_CONFIG.copy()
            merged_config.update(config)
            return merged_config
        except Exception as e:
            print(f"配置文件读取失败: {e}")
            return DEFAULT_CONFIG
    else:
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG


def save_config(config):
    try:
        with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"配置文件保存失败: {e}")
        return False


def generate_sign(timestamp, secret):
    secret_enc = secret.encode('utf-8')
    string_to_sign = f'{timestamp}\n{secret}'
    string_to_sign_enc = string_to_sign.encode('utf-8')
    hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
    sign = base64.b64encode(hmac_code).decode('utf-8')
    return sign


def send_dingtalk_message(config, title, content):
    if not config.get("enabled", True):
        return False, "通知已禁用"
    
    access_token = config.get("access_token", "")
    
    # 向后兼容：如果没有 access_token，尝试从 webhook_url 中提取
    if not access_token:
        webhook_url = config.get("webhook_url", "")
        if webhook_url and "access_token=" in webhook_url:
            access_token = webhook_url.split("access_token=")[1].split("&")[0]
    
    if not access_token:
        return False, "未配置钉钉 access token 或 webhook_url"
    
    webhook_url = f"https://oapi.dingtalk.com/robot/send?access_token={access_token}"
    
    message = {
        "msgtype": "markdown",
        "markdown": {
            "title": title,
            "text": content
        }
    }
    
    if config.get("secret"):
        timestamp = str(round(time.time() * 1000))
        sign = generate_sign(timestamp, config["secret"])
        webhook_url += f"&timestamp={timestamp}&sign={sign}"
    
    try:
        data = json.dumps(message).encode('utf-8')
        req = Request(
            webhook_url,
            data=data,
            headers={'Content-Type': 'application/json'}
        )
        
        with urlopen(req, timeout=10) as response:
            result = json.loads(response.read().decode('utf-8'))
            
        if result.get('errcode') == 0:
            return True, "消息发送成功"
        else:
            return False, f"钉钉API错误: {result.get('errmsg', '未知错误')}"
            
    except Exception as e:
        return False, f"发送失败: {e}"


def format_message(config, command="", response="", duration=0.0, working_dir=""):
    template = config.get("message_template", {})
    
    status_icon = "✅"
    status_text = "响应完成"
    title = template.get('title', 'Claude Code 响应完成')
    
    lines = [
        f"# {title}",
        "",
        f"{status_icon} **状态**: {status_text}",
    ]
    
    if command:
        lines.append(f"👤 **用户输入**: `{command[:100]}{'...' if len(command) > 100 else ''}`")
    
    if response:
        lines.append(f"🤖 **AI响应**: `{response[:150]}{'...' if len(response) > 150 else ''}`")
    
    if template.get("include_duration", True) and duration > 0:
        lines.append(f"⏱️ **响应时长**: {duration:.2f}秒")
    
    if template.get("include_working_dir", True) and working_dir:
        lines.append(f"📁 **工作目录**: `{working_dir}`")
    
    lines.extend([
        "",
        f"🕐 **完成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "💡 **可以进行下一次 prompt 了**"
    ])
    
    content = "\n".join(lines)
    return title, content


def setup_hook():
    hook_dir = Path.home() / ".claude" / "hooks"
    hook_dir.mkdir(parents=True, exist_ok=True)
    
    hook_script = hook_dir / "stop"
    
    # 创建 Stop hook 脚本
    script_content = f'''#!/bin/bash
# Claude Code Stop Hook - 在每次 Claude Code 完成响应后发送钉钉通知

# 从标准输入读取 Stop hook 的 JSON 数据
input_data=$(cat)

# 提取基本信息
working_dir=$(echo "$input_data" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    print(data.get('cwd', ''))
except:
    print('')
")

# 设置默认的通知信息
prompt_text="Claude Code 响应完成"
response_text="AI 任务已完成"
duration="5.0"

# 导出环境变量并调用通知脚本
export PROMPT="$prompt_text"
export RESPONSE="$response_text"
export WORKING_DIR="$working_dir"
export DURATION="$duration"

exec python3 "$HOME/.local/bin/cc-hook" send --prompt "$PROMPT" --response "$RESPONSE" --working-dir "$WORKING_DIR" --duration "$DURATION"
'''
    
    try:
        with open(hook_script, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        hook_script.chmod(0o755)

        # 在 settings.json 中添加 hooks 配置
        settings_file = Path.home() / ".claude" / "settings.json"
        try:
            # 读取现有的 settings.json
            if settings_file.exists():
                with open(settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
            else:
                settings = {}

            # 添加 hooks 配置
            if 'hooks' not in settings:
                settings['hooks'] = {}

            settings['hooks']['Stop'] = [
                {
                    "hooks": [
                        {
                            "type": "command",
                            "command": str(hook_script),
                            "timeout": 10
                        }
                    ]
                }
            ]

            # 保存 settings.json
            with open(settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
            print(f"✅ 已在 settings.json 中配置 hooks: {settings_file}")
        except Exception as e:
            print(f"⚠️  配置 settings.json 失败: {e}")
            print("请手动在 ~/.claude/settings.json 中添加 hooks 配置")

        print(f"✅ Hook 已安装到: {hook_script}")
        print("📝 已自动配置全局 hooks，请重启 Claude Code")
        return True
        
    except Exception as e:
        print(f"❌ Hook 安装失败: {e}")
        return False


def install_command():
    print("🚀 开始安装 Claude Code Hook 工具...")
    
    try:
        import json
        import hmac
        import hashlib
        print("✅ Python 依赖检查通过")
    except ImportError as e:
        print(f"❌ Python 依赖检查失败: {e}")
        return False
    
    config = load_config()
    print(f"✅ 配置文件已创建: {CONFIG_PATH}")
    
    if setup_hook():
        print("\n🎉 安装完成！")
        print(f"📋 配置文件位置: {CONFIG_PATH}")
        print("🔧 您可以编辑配置文件来自定义通知内容")
        print("\n⚠️  请在 Claude Code 设置中启用 Stop hook")
        return True
    else:
        return False
    
    # 创建配置文件
    config = load_config()
    print(f"✅ 配置文件已创建: {CONFIG_PATH}")
    
    # 安装 hook
    if setup_hook():
        print("\n🎉 安装完成！")
        print(f"📋 配置文件位置: {CONFIG_PATH}")
        print("🔧 您可以编辑配置文件来自定义通知内容")
        print("\n⚠️  请在 Claude Code 设置中启用 Stop hook")
        return True
    else:
        return False


def config_command(args):
    config = load_config()
    
    if args.show:
        print(json.dumps(config, indent=2, ensure_ascii=False))
        return
    
    if args.access_token:
        config["access_token"] = args.access_token
        print(f"✅ 设置 access token: {args.access_token[:20]}...")
    
    if args.secret:
        config["secret"] = args.secret
        print("✅ 设置安全密钥")
    
    if args.enable is not None:
        config["enabled"] = args.enable
        print(f"✅ {'启用' if args.enable else '禁用'}通知")
    
    if args.test:
        title, content = format_message(config, "test-command", "这是测试响应", 1.5, "/test/dir")
        success, message = send_dingtalk_message(config, title, content)
        if success:
            print("✅ 测试消息发送成功")
        else:
            print(f"❌ 测试消息发送失败: {message}")
        return
    
    save_config(config)


def main():
    parser = argparse.ArgumentParser(
        description="Claude Code Hook Tool - 全局钉钉通知工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 安装 hook 工具
  python3 cc-hook.py install
  
  # 配置 access token
  python3 cc-hook.py config --access-token "YOUR_TOKEN"
  
  # 测试通知
  python3 cc-hook.py config --test
  
  # 查看当前配置
  python3 cc-hook.py config --show
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    install_parser = subparsers.add_parser('install', help='安装 Claude Code Stop hook')
    
    config_parser = subparsers.add_parser('config', help='配置钉钉通知')
    config_parser.add_argument('--access-token', help='设置钉钉 access token')
    config_parser.add_argument('--secret', help='设置安全密钥')
    config_parser.add_argument('--enable', action=argparse.BooleanOptionalAction, help='启用/禁用通知')
    config_parser.add_argument('--test', action='store_true', help='发送测试消息')
    config_parser.add_argument('--show', action='store_true', help='显示当前配置')
    
    send_parser = subparsers.add_parser('send', help='直接发送通知')
    send_parser.add_argument('--prompt', help='用户输入的 prompt')
    send_parser.add_argument('--response', help='Claude Code 的响应')
    send_parser.add_argument('--duration', type=float, default=0, help='响应时长（秒）')
    send_parser.add_argument('--working-dir', help='工作目录')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    if args.command == 'install':
        install_command()
    elif args.command == 'config':
        config_command(args)
    elif args.command == 'send':
        config = load_config()
        title, content = format_message(
            config, 
            args.prompt or "", 
            args.response or "", 
            args.duration, 
            args.working_dir or ""
        )
        success, message = send_dingtalk_message(config, title, content)
        if success:
            print("✅ 通知发送成功")
        else:
            print(f"❌ 通知发送失败: {message}")


if __name__ == "__main__":
    main()