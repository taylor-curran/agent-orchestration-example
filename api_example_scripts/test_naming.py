#!/usr/bin/env python3
"""
Test script to verify the naming logic without requiring httpx.
"""
import os
from pathlib import Path

def find_markdown_files(directory):
    """Recursively find all markdown files in a directory."""
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

def test_naming_logic(directory, trigger_prefix="When working with"):
    """Test the naming logic for knowledge items."""
    print(f"🔍 Testing naming logic for markdown files in: {directory}")
    markdown_files = find_markdown_files(directory)
    
    if not markdown_files:
        print("❌ No markdown files found")
        return
    
    print(f"✅ Found {len(markdown_files)} markdown file(s)\n")
    
    for idx, file_path in enumerate(markdown_files, 1):
        print(f"{'='*60}")
        print(f"📄 Processing {idx}/{len(markdown_files)}: {file_path.name}")
        print(f"   Path: {file_path.relative_to(directory)}")
        
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
        
        print(f"   📝 Knowledge Item Name: {name}")
        print(f"   🎯 Trigger: {trigger_description}")
        print()

if __name__ == "__main__":
    test_naming_logic(".")
