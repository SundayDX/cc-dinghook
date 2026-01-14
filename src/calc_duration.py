#!/usr/bin/env python3
"""
Calculate duration from transcript timestamps
"""

import json
import sys


def calc_duration(transcript_path: str):
    """
    Calculate duration from transcript file
    """
    try:
        with open(transcript_path, 'r') as f:
            lines = f.readlines()

        timestamps = []
        for line in f:
            try:
                msg = json.loads(line)
                ts = msg.get('timestamp', 0)
                if ts:
                    timestamps.append(ts)
            except:
                pass

        if len(timestamps) >= 2:
            first_time = timestamps[0]
            last_time = timestamps[-1]
            if first_time < last_time:
                duration = (last_time - first_time) / 1000
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
