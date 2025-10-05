#!/usr/bin/env python3
"""
Script to update the Devin playbook via API.
Reads the playbook markdown file and updates it in Devin settings.
"""

import os
import sys
import json
import requests
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def list_playbooks(api_key: str) -> list:
    """List all playbooks for the organization."""
    
    print("📋 Fetching playbooks...")
    
    url = "https://api.devin.ai/v1/playbooks"
    headers = {
        "Authorization": f"Bearer {api_key}"
    }
    
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    
    playbooks = response.json()
    print(f"✅ Found {len(playbooks)} playbook(s)")
    
    return playbooks


def find_playbook_by_macro(playbooks: list, macro: str) -> dict:
    """Find a playbook by its macro name."""
    
    for playbook in playbooks:
        if playbook.get("macro") == macro:
            return playbook
    
    return None


def update_playbook(
    api_key: str,
    playbook_id: str,
    title: str,
    body: str,
    macro: str
) -> dict:
    """Update an existing playbook."""
    
    print(f"🔄 Updating playbook {playbook_id}...")
    
    url = f"https://api.devin.ai/v1/playbooks/{playbook_id}"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "title": title,
        "body": body,
        "macro": macro
    }
    
    response = requests.put(url, headers=headers, json=data)
    response.raise_for_status()
    
    result = response.json()
    print(f"✅ Playbook updated successfully!")
    
    return result


def load_playbook_file(file_path: str) -> str:
    """Load the playbook content from a markdown file."""
    
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Playbook file not found: {file_path}")
    
    with open(path, 'r') as f:
        content = f.read()
    
    print(f"📄 Loaded playbook from: {file_path}")
    print(f"   Size: {len(content)} characters")
    
    return content


def main(
    macro: str = "!get_java_deps",
    title: str = "Java Dependency Discovery",
    playbook_file: str = None
):
    """
    Main function to update a playbook.
    
    Args:
        macro: The playbook macro to find and update (e.g., "!get_java_deps")
        title: The title for the playbook
        playbook_file: Path to the markdown file (if None, uses default)
    """
    
    print("="*80)
    print("DEVIN PLAYBOOK UPDATER".center(80))
    print("="*80)
    
    # Get API key
    api_key = os.environ.get("DEVIN_API_KEY")
    if not api_key:
        print("❌ Error: DEVIN_API_KEY not found in environment")
        sys.exit(1)
    
    print("🔑 API key loaded")
    
    # Default playbook file
    if playbook_file is None:
        script_dir = Path(__file__).parent
        playbook_file = script_dir / "find-java-deps-playbook.md"
    
    # Load playbook content
    try:
        body = load_playbook_file(playbook_file)
    except FileNotFoundError as e:
        print(f"❌ {e}")
        sys.exit(1)
    
    # List playbooks
    try:
        playbooks = list_playbooks(api_key)
    except Exception as e:
        print(f"❌ Error listing playbooks: {e}")
        sys.exit(1)
    
    # Display available playbooks
    if playbooks:
        print("\n📚 Available playbooks:")
        for pb in playbooks:
            pb_macro = pb.get("macro", "N/A")
            pb_title = pb.get("title", "N/A")
            pb_id = pb.get("playbook_id", "N/A")
            print(f"   • {pb_macro} - {pb_title} (ID: {pb_id})")
    
    # Find the specific playbook
    print(f"\n🔍 Looking for playbook with macro: {macro}")
    playbook = find_playbook_by_macro(playbooks, macro)
    
    if not playbook:
        print(f"❌ Playbook with macro '{macro}' not found!")
        print(f"   Please create it first in Devin settings or check the macro name.")
        sys.exit(1)
    
    playbook_id = playbook["playbook_id"]
    print(f"✅ Found playbook: {playbook['title']} (ID: {playbook_id})")
    
    # Update the playbook
    try:
        result = update_playbook(
            api_key=api_key,
            playbook_id=playbook_id,
            title=title,
            body=body,
            macro=macro
        )
        
        print("\n" + "="*80)
        print("SUCCESS".center(80))
        print("="*80)
        print(f"\n✅ Playbook '{macro}' has been updated!")
        print(f"   Title: {title}")
        print(f"   Content: {len(body)} characters")
        
    except Exception as e:
        print(f"\n❌ Error updating playbook: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # ========================================
    # CONFIGURE THESE PARAMETERS
    # ========================================
    
    MACRO = "!get_java_deps"  # The playbook macro to update
    TITLE = "Java Dependency Discovery"  # The playbook title
    PLAYBOOK_FILE = None  # Path to markdown file (None = use default)
    
    # ========================================
    
    main(macro=MACRO, title=TITLE, playbook_file=PLAYBOOK_FILE)
