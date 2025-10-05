#!/usr/bin/env python3
"""
List recent Devin sessions.
"""

import os
import sys
import json
import requests
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()


def list_sessions(api_key: str, limit: int = 10):
    """List recent Devin sessions."""
    
    print("="*80)
    print("RECENT DEVIN SESSIONS".center(80))
    print("="*80)
    
    url = "https://api.devin.ai/v1/sessions"
    headers = {
        "Authorization": f"Bearer {api_key}"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        # Handle different response formats
        if isinstance(data, dict):
            sessions = data.get('sessions', [])
        elif isinstance(data, list):
            sessions = data
        else:
            print(f"❌ Unexpected response format: {type(data)}")
            print(f"Response: {data}")
            return []
            
    except Exception as e:
        print(f"❌ Error fetching sessions: {e}")
        import traceback
        traceback.print_exc()
        return []
    
    if not sessions:
        print("\nNo sessions found.")
        return []
    
    # Sort by creation time (most recent first)
    sessions = sorted(sessions, key=lambda x: x.get('created_at', '') if isinstance(x, dict) else '', reverse=True)[:limit]
    
    print(f"\n📋 Found {len(sessions)} recent session(s):\n")
    
    for i, session in enumerate(sessions, 1):
        session_id = session.get('session_id', 'N/A')
        title = session.get('title', 'Untitled')
        status = session.get('status_enum', 'unknown')
        created = session.get('created_at', 'N/A')
        
        # Parse timestamp
        if created != 'N/A':
            try:
                dt = datetime.fromisoformat(created.replace('Z', '+00:00'))
                created_str = dt.strftime('%Y-%m-%d %H:%M:%S')
            except:
                created_str = created
        else:
            created_str = 'N/A'
        
        # Status emoji
        status_emoji = {
            'working': '🔄',
            'blocked': '⏸️',
            'finished': '✅',
            'expired': '❌'
        }.get(status, '❓')
        
        print(f"{i}. {status_emoji} {title}")
        print(f"   ID: {session_id}")
        print(f"   Status: {status}")
        print(f"   Created: {created_str}")
        print(f"   URL: https://app.devin.ai/sessions/{session_id.replace('devin-', '')}")
        
        # Check for structured output
        structured_output = session.get('structured_output')
        if structured_output:
            print(f"   📊 Has structured output!")
        
        print()
    
    return sessions


if __name__ == "__main__":
    api_key = os.environ.get("DEVIN_API_KEY")
    if not api_key:
        print("❌ DEVIN_API_KEY not found")
        sys.exit(1)
    
    sessions = list_sessions(api_key, limit=15)
    
    print("="*80)
    print(f"\nTo inspect a session, run:")
    print(f"  python api_example_scripts/inspect_session.py <session_id>")
