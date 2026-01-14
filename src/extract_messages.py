#!/usr/bin/env python3
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
                    output = msg.get('tool_output', {})
                    tool_name = msg.get('tool_name', '')
                    if isinstance(output, dict):
                        output_text = output.get('output', '')
                        if tool_name and output_text:
                            summary = output_text[:200] + '...' if len(output_text) > 200 else output_text
                            tool_summaries.append(f"[{tool_name}] {summary}")
                            if len(tool_summaries) >= 2:
                                break
            except:
                pass

        last_assistant = '\n'.join(tool_summaries) if tool_summaries else "无"

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
