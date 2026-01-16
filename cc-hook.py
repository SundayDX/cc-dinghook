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

    # 提取项目名称（从工作目录）
    project_name = working_dir.split('/')[-1] if working_dir and '/' in working_dir else working_dir

    status_icon = "✅"
    title = template.get('title', 'Claude Code 响应完成')

    lines = [
        f"# {title}",
        "",
        f"{status_icon} **项目**: `{project_name}`",
    ]

    # 显示用户输入（最多 300 字符）
    if command and command != "Claude Code 响应完成":
        user_display = command[:300] + '...' if len(command) > 300 else command
        lines.append(f"📝 **用户输入**:")
        lines.append(f"> {user_display}")

    # 显示 AI 响应摘要（最多 500 字符）
    if response and response != "AI 任务已完成":
        response_display = response[:500] + '...' if len(response) > 500 else response
        lines.append(f"")
        lines.append(f"🤖 **AI 响应摘要**:")
        lines.append(f"> {response_display}")

    # 可选：显示额外信息
    if template.get("include_duration", True) and duration > 0:
        lines.append(f"")
        lines.append(f"⏱️ 耗时: {duration:.1f}秒")

    if template.get("include_working_dir", True) and working_dir:
        lines.append(f"📁 路径: `{working_dir}`")

    lines.extend([
        "",
        f"🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
    ])

    content = "\n".join(lines)
    return title, content


def setup_hook():
    # 复制脚本到用户目录
    hooks_dir = Path.home() / ".claude" / "hooks"
    hooks_dir.mkdir(parents=True, exist_ok=True)

    # 辅助脚本内容（直接嵌入，避免依赖外部文件）
    extract_messages_script = '''#!/usr/bin/env python3
"""
Extract user prompt and AI response summary from transcript
"""
import json
import sys

def extract_from_transcript(transcript_path: str):
    """
    Extract last user message and AI response summary from transcript
    """
    try:
        with open(transcript_path, 'r') as f:
            lines = f.readlines()

        # Extract last user message (max 300 chars)
        last_user = "无"
        for line in reversed(lines):
            try:
                msg = json.loads(line)
                if msg.get('type') == 'user':
                    content = msg.get('content', '')
                    if content:
                        last_user = content[:300] + '...' if len(content) > 300 else content
                    break
            except:
                pass

        # Extract last 2 tool outputs as AI response summary (max 200 chars each)
        tool_summaries = []
        for line in reversed(lines):
            try:
                msg = json.loads(line)
                if msg.get('type') == 'tool_result':
                    tool_name = msg.get('tool_name', '')
                    # tool_output 可能在不同位置
                    tool_output = msg.get('tool_output', {})
                    output_text = ''

                    if isinstance(tool_output, dict):
                        output_text = tool_output.get('output', '')
                    elif isinstance(tool_output, str):
                        output_text = tool_output

                    if tool_name and output_text:
                        summary = output_text[:200] + '...' if len(output_text) > 200 else output_text
                        tool_summaries.append(f"[{tool_name}] {summary}")
                        if len(tool_summaries) >= 2:
                            break
            except:
                pass

        # 使用 chr(10) 代表换行符
        last_assistant = chr(10).join(tool_summaries) if tool_summaries else "无"

        return last_user, last_assistant

    except Exception as e:
        return "无", "无"


if __name__ == '__main__':
    if len(sys.argv) >= 2:
        transcript_path = sys.argv[1]
        prompt, assistant = extract_from_transcript(transcript_path)
        print(f"{prompt}|{assistant}")
    else:
        print("无|无")
'''

    calc_duration_script = '''#!/usr/bin/env python3
"""
Calculate duration from transcript timestamps
"""
import json
import sys
from datetime import datetime


def calc_duration(transcript_path: str):
    """
    Calculate duration from transcript file
    """
    try:
        with open(transcript_path, 'r') as f:
            lines = f.readlines()

        timestamps = []
        for line in lines:
            try:
                msg = json.loads(line)
                ts = msg.get('timestamp', '')
                if ts:
                    # 尝试解析 ISO 8601 格式的时间戳
                    try:
                        dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
                        timestamps.append(dt.timestamp())
                    except:
                        # 如果不是 ISO 格式，尝试作为数字处理
                        try:
                            ts_float = float(ts)
                            # 如果是毫秒级时间戳（大于 100 亿），转换为秒
                            if ts_float > 10000000000:
                                ts_float = ts_float / 1000.0
                            timestamps.append(ts_float)
                        except:
                            pass
            except:
                pass

        if len(timestamps) >= 2:
            first_time = timestamps[0]
            last_time = timestamps[-1]
            if first_time < last_time:
                duration = (last_time - first_time)
                print(f"{duration:.1f}")
                return

        print("5.0")
        return "5.0"
    except Exception as e:
        print("5.0")
        return "5.0"


if __name__ == '__main__':
    if len(sys.argv) >= 2:
        transcript_path = sys.argv[1]
        calc_duration(transcript_path)
    else:
        print("5.0")
'''

    # 创建辅助脚本文件
    scripts = {
        'extract_messages.py': extract_messages_script,
        'calc_duration.py': calc_duration_script
    }

    for script_name, script_content in scripts.items():
        dest_file = hooks_dir / script_name
        with open(dest_file, 'w', encoding='utf-8') as f:
            f.write(script_content)
        dest_file.chmod(0o755)
        print(f"✅ 已创建 {script_name} 到 {dest_file}")

    # 创建 Stop hook 脚本
    hook_script = hooks_dir / "stop"

    # 创建 Stop hook 脚本
    script_content = f'''#!/bin/bash
# Claude Code Stop Hook - 在每次 Claude Code 完成响应后发送钉钉通知

# 从标准输入读取 Stop hook 的 JSON 数据
input_data=$(cat)

# 提取 cwd 和 transcript_path
cwd=$(echo "$input_data" | python3 -c "import json, sys; data = json.load(sys.stdin); print(data.get('cwd', ''))")
transcript_path=$(echo "$input_data" | python3 -c "import json, sys; data = json.load(sys.stdin); print(data.get('transcript_path', ''))")

# 提取用户 prompt 和 AI 响应摘要
if [ -n "$transcript_path" ] && [ -f "$transcript_path" ]; then
    # 使用单独的 Python 脚本提取信息
    prompt_text=$(~/.claude/hooks/extract_messages.py "$transcript_path" | cut -d'|' -f1)
    response_text=$(~/.claude/hooks/extract_messages.py "$transcript_path" | cut -d'|' -f2)
else
    prompt_text="Claude Code 响应完成"
    response_text="AI 任务已完成"
fi

# 计算 duration
if [ -n "$transcript_path" ] && [ -f "$transcript_path" ]; then
    duration=$(~/.claude/hooks/calc_duration.py "$transcript_path")
else
    duration="5.0"
fi

# 导出环境变量并调用通知脚本
export PROMPT="$prompt_text"
export RESPONSE="$response_text"
export WORKING_DIR="$cwd"
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