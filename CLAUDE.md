# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

CC-DingHook is a global DingTalk notification tool for Claude Code. It automatically sends DingTalk notifications after each Claude Code response completes, allowing users to stay informed without constantly switching windows.

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

# Build TypeScript definitions (if modified)
npm run build

# Run tests
npm test
```

### Utility Scripts
```bash
# Extract messages from transcript
python3 src/extract_messages.py <transcript_path>

# Calculate duration from transcript
python3 src/calc_duration.py <transcript_path>
```

## Architecture

### Hook System
The tool integrates with Claude Code via the Stop Hook mechanism:

1. **Hook Location**: `~/.claude/hooks/stop`
2. **Trigger**: After each Claude Code response completes
3. **Input**: JSON via stdin containing `cwd` and `transcript_path`
4. **Flow**:
   - Extract user prompt and AI response from transcript using `extract_messages.py`
   - Calculate execution duration using `calc_duration.py`
   - Send notification via `cc-hook send`

### Configuration System
- **Location**: `~/.cc-hook-config.json`
- **Managed by**: `cc-hook config` command
- **Key settings**:
  - `access_token`: DingTalk webhook token
  - `secret`: HMAC-SHA256 signing key (optional but recommended)
  - `enabled`: Master switch for notifications
  - `message_template`: Customize notification content
  - `notifications`: Filter by success/failure/error

### Message Extraction
The `src/extract_messages.py` script parses Claude Code's transcript JSONL format:
- Extracts the last user message (max 300 chars)
- Extracts the last 2 tool outputs as AI response summary (max 200 chars each)
- Output format: `prompt|assistant` (pipe-delimited)

### DingTalk Integration
- **API**: DingTalk Custom Webhook
- **Message Type**: Markdown
- **Security**: Supports HMAC-SHA256 signature verification
- **Fallback**: Gracefully handles network errors and missing configuration

### Dual-Language Architecture
- **Python**: Core functionality (main script, hook handlers, utilities)
- **TypeScript**: Type definitions for future Node.js integration
- The two codebases share the same data structures (see `src/types.ts`)

## Important Implementation Details

1. **Transcript Parsing**: The transcript file contains JSONL (one JSON object per line). Messages have `type` field (`user`, `tool_result`, etc.)

2. **Stop Hook Data**: Claude Code passes JSON via stdin with `cwd` and `transcript_path` fields. The hook script must read from stdin.

3. **Duration Calculation**: The `calc_duration.py` script has a bug in line 19 (`for line in f:` should be `for line in lines:`). It returns a default of 5.0 seconds on error.

4. **Security**: Configuration files should have 600 permissions. The script supports backward compatibility with legacy `webhook_url` config.

5. **Hook Installation**: The `install` command copies utility scripts to `~/.claude/hooks/` and creates the main stop hook script.

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
