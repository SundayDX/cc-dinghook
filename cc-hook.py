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
    "webhook_url": "https://oapi.dingtalk.com/robot/send?access_token=59be108cccd12f84ece4d422956ca8c5843f5a09fde8fc293fb9c5de6d765b53",
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
    
    webhook_url = config.get("webhook_url", "")
    if not webhook_url:
        return False, "未配置钉钉 webhook URL"
    
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
    
    lines = [
        f"# {template.get('title', 'Claude Code 响应完成')}",
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
    
    return "\n".join(lines)


def setup_hook():
    hook_dir = Path.home() / ".claude" / "hooks"
    hook_dir.mkdir(parents=True, exist_ok=True)
    
    hook_script = hook_dir / "post-response"
    
    script_content = f'''#!/bin/bash
PROMPT="$1"
RESPONSE="$2"
DURATION="$3"
WORKING_DIR="$PWD"

export PROMPT="$PROMPT"
export RESPONSE="$RESPONSE" 
export WORKING_DIR="$WORKING_DIR"
export DURATION="$DURATION"

exec python3 "{Path(__file__).parent}/cc-hook.py" send --command "$PROMPT" --response "$RESPONSE" --working-dir "$WORKING_DIR" --duration "$DURATION"
'''
    
    try:
        with open(hook_script, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        hook_script.chmod(0o755)
        
        print(f"✅ Hook 已安装到: {hook_script}")
        print("📝 请确保在 Claude Code 配置中启用 post-response hook")
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
        print("\n⚠️  请在 Claude Code 设置中启用 post-response hook")
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
        print("\n⚠️  请在 Claude Code 设置中启用 post-response hook")
        return True
    else:
        return False


def config_command(args):
    config = load_config()
    
    if args.show:
        print(json.dumps(config, indent=2, ensure_ascii=False))
        return
    
    if args.webhook:
        config["webhook_url"] = args.webhook
        print(f"✅ 设置 webhook URL: {args.webhook}")
    
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
  
  # 配置 webhook URL
  python3 cc-hook.py config --webhook "https://oapi.dingtalk.com/robot/send?access_token=YOUR_TOKEN"
  
  # 测试通知
  python3 cc-hook.py config --test
  
  # 查看当前配置
  python3 cc-hook.py config --show
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    install_parser = subparsers.add_parser('install', help='安装 Claude Code post-response hook')
    
    config_parser = subparsers.add_parser('config', help='配置钉钉通知')
    config_parser.add_argument('--webhook', help='设置钉钉 webhook URL')
    config_parser.add_argument('--secret', help='设置安全密钥')
    config_parser.add_argument('--enable', action=argparse.BooleanOptionalAction, help='启用/禁用通知')
    config_parser.add_argument('--test', action='store_true', help='发送测试消息')
    config_parser.add_argument('--show', action='store_true', help='显示当前配置')
    
    send_parser = subparsers.add_parser('send', help='直接发送通知')
    send_parser.add_argument('--command', help='用户输入的 prompt')
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
            args.command or "", 
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