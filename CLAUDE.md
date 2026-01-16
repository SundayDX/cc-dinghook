# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

CC-DingHook is a global DingTalk notification tool for Claude Code. It automatically sends DingTalk notifications after each Claude Code response completes via the Stop Hook mechanism.

## Key Commands

### Installation and Setup
```bash
# One-line installation (production)
curl -fsSL https://raw.githubusercontent.com/SundayDX/cc-dinghook/master/install.sh | bash

# Manual installation
python3 cc-hook.py install

# Configure DingTalk webhook
cc-hook config --access-token "YOUR_TOKEN"
cc-hook config --secret "YOUR_SECRET"  # optional, for signed webhooks

# Test notification
cc-hook config --test

# View current configuration
cc-hook config --show
```

### Development
```bash
# Run the hook script directly
python3 cc-hook.py --help
```

## Architecture

### Stop Hook Integration
The tool integrates with Claude Code via the Stop Hook mechanism:

1. **Hook Location**: `~/.claude/hooks/stop` (configured in `~/.claude/settings.json`)
2. **Trigger**: After each Claude Code response completes
3. **Input**: JSON via stdin containing `cwd` and `transcript_path`
4. **Output**: Sends notification via `cc-hook send` command

### Hook Script Flow
The Stop hook script (`~/.claude/hooks/stop`) is a bash script that:
1. Reads JSON from stdin with `cwd` and `transcript_path`
2. Calls `extract_messages.py` to parse the transcript (outputs `prompt|response`)
3. Calls `calc_duration.py` to calculate execution time
4. Invokes `cc-hook send` with extracted data

### Configuration System
- **Location**: `~/.cc-hook-config.json`
- **Managed by**: `cc-hook config` command
- **Default config**: Merges user config with `DEFAULT_CONFIG` in `cc-hook.py`
- **Backward compatibility**: Supports legacy `webhook_url` format (extracts token from URL)

### Message Extraction
The `extract_messages.py` script (embedded in `cc-hook.py:setup_hook()`) parses Claude Code's transcript JSONL format:
- Extracts the last user message (max 300 chars)
- Extracts up to 2 tool outputs as AI response summary (max 200 chars each)
- Output format: `prompt|assistant` (pipe-delimited)
- Uses `chr(10)` for newlines to avoid shell escaping issues

### Duration Calculation
The `calc_duration.py` script (embedded in `cc-hook.py:setup_hook()`):
- Parses ISO 8601 timestamps from transcript `timestamp` fields
- Calculates: `last_timestamp - first_timestamp`
- Falls back to `5.0` seconds on error

### DingTalk Integration
- **API**: DingTalk Custom Webhook (`https://oapi.dingtalk.com/robot/send`)
- **Message Type**: Markdown
- **Security**: Supports HMAC-SHA256 signature verification (timestamp + sign)
- **Message formatting**: `format_message()` builds markdown with status icons, user input, AI response summary

## Important Implementation Details

### Script Embedding Pattern
The `install` command embeds helper scripts directly into the generated hook files to avoid external dependencies:
- `extract_messages.py` content is embedded as a heredoc in `setup_hook()`
- `calc_duration.py` content is embedded as a heredoc in `setup_hook()`
- These are written to `~/.claude/hooks/extract_messages.py` and `calc_duration.py` during installation

### Transcript Format
Claude Code's transcript file is JSONL (one JSON object per line):
- Each line has a `type` field: `user`, `tool_result`, etc.
- User messages: `type: "user"` with `content` field
- Tool results: `type: "tool_result"` with `tool_name` and `tool_output` fields
- `tool_output` can be a dict (with `output` key) or string

### Settings.json Integration
The `install` command automatically updates `~/.claude/settings.json`:
```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "/home/user/.claude/hooks/stop",
            "timeout": 10
          }
        ]
      }
    ]
  }
}
```

## Configuration Structure

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

## Testing Notifications

Always test after configuration changes:
```bash
cc-hook config --test
```

This sends a test notification without requiring a Claude Code execution.
