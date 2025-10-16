#!/usr/bin/env python3
"""
Script to create Devin knowledge items from all markdown files in a directory.
Recursively searches subdirectories for .md files.
"""
import os
import httpx
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def find_markdown_files(directory):
    """Recursively find all markdown files in a directory.
    
    Args:
        directory: Root directory to search
        
    Returns:
        List of Path objects for all .md files found
    """
    directory_path = Path(directory)
    
    if not directory_path.exists():
        raise ValueError(f"Directory does not exist: {directory}")
    
    if not directory_path.is_dir():
        raise ValueError(f"Path is not a directory: {directory}")
    
    # Find all .md and .markdown files recursively
    markdown_files = []
    markdown_files.extend(directory_path.rglob("*.md"))
    markdown_files.extend(directory_path.rglob("*.markdown"))
    
    return sorted(markdown_files)

def create_knowledge_item(name, body, trigger_description=None, parent_folder_id=None, pinned_repo=None):
    """Create a knowledge item in Devin.
    
    Args:
        name: Display name for the knowledge item
        body: The content of the knowledge
        trigger_description: When this knowledge should be used (optional)
        parent_folder_id: Folder ID to organize knowledge (optional)
        pinned_repo: Repository pinning - None, "all", or "owner/repo" (optional)
        
    Returns:
        API response with created knowledge item details
    """
    api_key = os.getenv("DEVIN_API_KEY")
    
    if not api_key:
        raise ValueError("DEVIN_API_KEY not found in .env file")
    
    url = "https://api.devin.ai/v1/knowledge"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Build request body with required fields
    data = {
        "name": name,
        "body": body
    }
    
    # Add optional fields if provided
    if trigger_description:
        data["trigger_description"] = trigger_description
    if parent_folder_id:
        data["parent_folder_id"] = parent_folder_id
    if pinned_repo:
        data["pinned_repo"] = pinned_repo
    
    with httpx.Client() as client:
        response = client.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()

def create_knowledge_from_markdown_files(
    directory, 
    trigger_prefix="When working with",
    parent_folder_id=None,
    pinned_repo=None,
    dry_run=False
):
    """Create knowledge items for all markdown files in a directory.
    
    Args:
        directory: Directory to search for markdown files
        trigger_prefix: Prefix for auto-generated trigger descriptions
        parent_folder_id: Optional folder ID to organize all knowledge items
        pinned_repo: Optional repository pinning ("all" or "owner/repo")
        dry_run: If True, only show what would be created without actually creating
        
    Returns:
        List of created knowledge items
    """
    print(f"🔍 Searching for markdown files in: {directory}")
    markdown_files = find_markdown_files(directory)
    
    if not markdown_files:
        print("❌ No markdown files found")
        return []
    
    print(f"✅ Found {len(markdown_files)} markdown file(s)\n")
    
    created_items = []
    
    for idx, file_path in enumerate(markdown_files, 1):
        print(f"{'='*60}")
        print(f"📄 Processing {idx}/{len(markdown_files)}: {file_path.name}")
        print(f"   Path: {file_path.relative_to(directory)}")
        
        # Read file content
        try:
            content = file_path.read_text(encoding='utf-8')
        except Exception as e:
            print(f"   ❌ Error reading file: {e}")
            continue
        
        # Generate name from filename (remove extension)
        # Include parent directory name if file is in a subdirectory
        relative_path = file_path.relative_to(directory)
        if len(relative_path.parts) > 1:
            # File is in a subdirectory, include parent directory name
            parent_dir = relative_path.parent.name
            name = f"{parent_dir}-{file_path.stem}"
        else:
            # File is in root directory, use just the filename
            name = file_path.stem
        
        # Generate trigger description from filename
        trigger_description = f"{trigger_prefix} {name.replace('-', ' ').replace('_', ' ')}"
        
        print(f"   Name: {name}")
        print(f"   Trigger: {trigger_description}")
        print(f"   Size: {len(content)} characters")
        
        if dry_run:
            print(f"   🔸 DRY RUN - Would create knowledge item")
            created_items.append({
                "name": name,
                "file_path": str(file_path),
                "dry_run": True
            })
        else:
            # Create knowledge item
            result = create_knowledge_item(
                name=name,
                body=content,
                trigger_description=trigger_description,
                parent_folder_id=parent_folder_id,
                pinned_repo=pinned_repo
            )
            
            print(f"   ✅ Created knowledge item")
            print(f"   ID: {result.get('id')}")
            print(f"   Created at: {result.get('created_at')}")
            
            created_items.append(result)
        
        print()
    
    # Summary
    print(f"{'='*60}")
    if dry_run:
        print(f"🔸 DRY RUN COMPLETE - Would create {len(created_items)} knowledge items")
    else:
        print(f"✅ Successfully created {len(created_items)} knowledge items")
    
    return created_items

if __name__ == "__main__":
    # ===== CONFIGURATION =====
    # Specify the directory to search for markdown files
    target_directory = "."  # Change this to your desired directory path
    
    # Set to True to preview without creating knowledge items
    dry_run = True
    
    # Optional: Customize the trigger description prefix
    trigger_prefix = "When working with"
    
    # Optional: Specify a parent folder ID to organize knowledge items
    parent_folder_id = None  # e.g., "folder-xxx"
    
    # Optional: Pin knowledge to repositories ("all", "owner/repo", or None)
    pinned_repo = None
    # =========================
    
    if dry_run:
        print("🔸 Running in DRY RUN mode - no knowledge items will be created\n")
    
    # Create knowledge items from markdown files
    create_knowledge_from_markdown_files(
        directory=target_directory,
        trigger_prefix=trigger_prefix,
        parent_folder_id=parent_folder_id,
        pinned_repo=pinned_repo,
        dry_run=dry_run
    )
