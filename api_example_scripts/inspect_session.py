#!/usr/bin/env python3
"""
Quick script to inspect a Devin session and see what data is available.
"""

import os
import sys
import json
import requests
from dotenv import load_dotenv

load_dotenv()


def inspect_session(api_key: str, session_id: str):
    """Inspect a session and show all available data."""
    
    print("="*80)
    print(f"INSPECTING SESSION: {session_id}".center(80))
    print("="*80)
    
    url = f"https://api.devin.ai/v1/sessions/{session_id}"
    headers = {
        "Authorization": f"Bearer {api_key}"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        details = response.json()
    except Exception as e:
        print(f"❌ Error fetching session: {e}")
        return None
    
    # Print key info
    print(f"\n📋 Session Info:")
    print(f"   Title: {details.get('title', 'N/A')}")
    print(f"   Status: {details.get('status_enum', 'N/A')}")
    print(f"   Created: {details.get('created_at', 'N/A')}")
    print(f"   Updated: {details.get('updated_at', 'N/A')}")
    print(f"   URL: https://app.devin.ai/sessions/{session_id.replace('devin-', '')}")
    
    # Check for structured output
    print(f"\n📊 Structured Output:")
    structured_output = details.get("structured_output")
    if structured_output:
        print(f"   ✅ FOUND! ({len(json.dumps(structured_output))} chars)")
        print(f"\n   Content:")
        print(json.dumps(structured_output, indent=6))
    else:
        print(f"   ❌ Not available (type: {type(structured_output)})")
    
    # Check messages
    print(f"\n💬 Recent Messages:")
    messages = details.get("messages", [])
    print(f"   Total messages: {len(messages)}")
    
    if messages:
        print(f"\n   Last 5 messages:")
        for msg in messages[-5:]:
            msg_type = msg.get("type", "unknown")
            timestamp = msg.get("timestamp", "N/A")[:19]
            content = msg.get("message", "")[:150]
            print(f"\n   [{timestamp}] {msg_type}:")
            print(f"   {content}...")
    
    # Check for any files or artifacts
    print(f"\n📁 Top-level keys in response:")
    for key in details.keys():
        value = details[key]
        if isinstance(value, (list, dict)):
            size = len(value)
            print(f"   • {key}: {type(value).__name__} (size: {size})")
        else:
            print(f"   • {key}: {value}")
    
    # Save full details
    output_file = f"session_inspect_{session_id.replace('devin-', '')}.json"
    with open(output_file, 'w') as f:
        json.dump(details, f, indent=2)
    
    print(f"\n💾 Full details saved to: {output_file}")
    
    return details


if __name__ == "__main__":
    api_key = os.environ.get("DEVIN_API_KEY")
    if not api_key:
        print("❌ DEVIN_API_KEY not found")
        sys.exit(1)
    
    if len(sys.argv) < 2:
        print("Usage: python inspect_session.py <session_id>")
        print("\nOr set SESSION_ID below in the script")
        
        # You can hardcode a session ID here for testing
        SESSION_ID = None  # e.g., "devin-abc123..."
        
        if SESSION_ID:
            inspect_session(api_key, SESSION_ID)
        else:
            sys.exit(1)
    else:
        session_id = sys.argv[1]
        inspect_session(api_key, session_id)
