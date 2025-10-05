#!/usr/bin/env python3
"""
Standalone script to read and display dependency data from JSON files.
Works with output files from list_dependencies_simple.py or direct session reads.
Completely decoupled from the data generation scripts.
"""

import os
import sys
import json
import re
import requests
from typing import Optional, Dict, Any, Union
from pathlib import Path
import pandas as pd
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def read_json_file(filepath: str) -> Optional[Dict[str, Any]]:
    """Read a JSON file and return its contents."""
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ File not found: {filepath}")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in file: {e}")
        return None
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return None


def parse_session_id(session_id_or_url: str) -> Optional[str]:
    """Extract session ID from various formats."""
    # If it's a URL
    if session_id_or_url.startswith('http'):
        match = re.search(r'sessions/([a-f0-9\-]+)', session_id_or_url)
        if match:
            return f"devin-{match.group(1)}"
        return None
    
    # If it's already a session ID
    session_id = session_id_or_url
    if not session_id.startswith('devin-'):
        session_id = f"devin-{session_id}"
    return session_id


def get_session_data_from_api(session_id: str, api_key: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Retrieve session data directly from Devin API."""
    if api_key is None:
        api_key = os.environ.get("DEVIN_API_KEY")
        if not api_key:
            print("❌ DEVIN_API_KEY not found in environment")
            return None
    
    url = f"https://api.devin.ai/v1/sessions/{session_id}"
    headers = {"Authorization": f"Bearer {api_key}"}
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        details = response.json()
        
        # Check for structured_output
        if details.get("structured_output"):
            return details["structured_output"]
        
        # Check for attachments in messages
        messages = details.get("messages", [])
        for msg in reversed(messages[-5:]):
            msg_text = msg.get("message", "")
            pattern = r'https://app\.devin\.ai/attachments/([a-f0-9\-]+)/([^"]+)'
            match = re.search(pattern, msg_text)
            
            if match:
                uuid, filename = match.group(1), match.group(2)
                attachment_url = f"https://api.devin.ai/v1/attachments/{uuid}/{filename}"
                att_response = requests.get(attachment_url, headers=headers, allow_redirects=True)
                att_response.raise_for_status()
                return att_response.json()
        
        return None
    except Exception as e:
        print(f"❌ Error fetching session data: {e}")
        return None


def format_dependencies_df(deps_data: Union[Dict, list]) -> pd.DataFrame:
    """Convert dependency data to DataFrame format."""
    if not deps_data:
        return pd.DataFrame()
    
    # Handle different structures
    if isinstance(deps_data, dict):
        if 'upload_candidates' in deps_data:
            candidates = deps_data.get('upload_candidates', [])
            if candidates:
                df = pd.DataFrame(candidates)
                # Select and reorder columns for display - prioritize important ones
                priority_cols = ['group', 'artifact', 'name', 'version', 'repository', 'needs_upload']
                available_cols = [col for col in priority_cols if col in df.columns]
                # Add any other columns not in priority list
                other_cols = [col for col in df.columns if col not in priority_cols]
                display_cols = available_cols + other_cols
                if display_cols:
                    df = df[display_cols]
                return df
        elif 'dependencies' in deps_data:
            deps = deps_data.get('dependencies', [])
            if deps:
                return pd.DataFrame(deps)
    
    # If data is a list directly
    if isinstance(deps_data, list) and deps_data:
        df = pd.DataFrame(deps_data)
        # Try to reorder columns if they exist
        priority_cols = ['group', 'artifact', 'name', 'version', 'repository', 'needs_upload']
        available_cols = [col for col in priority_cols if col in df.columns]
        other_cols = [col for col in df.columns if col not in priority_cols]
        if available_cols or other_cols:
            df = df[available_cols + other_cols]
        return df
    
    return pd.DataFrame()


def display_dependencies(data: Dict[str, Any], version_type: str = "both", csv_prefix: Optional[str] = None) -> None:
    """Display dependency data as formatted DataFrames.
    
    Args:
        data: The dependency data to display
        version_type: Which version to display ('current', 'target', or 'both')
        csv_prefix: If provided, save DataFrames to CSV files with this prefix
    """
    
    if not data:
        print("No data to display")
        return
    
    csv_files_saved = []
    
    # Check what structure we have
    if 'results' in data:
        # Dual mode results
        res = data['results']
        
        if version_type in ['current', 'both'] and 'current' in res:
            print("\n📊 Current Version Dependencies:")
            print(f"   Version: {data.get('current_version', 'Unknown')}")
            df = format_dependencies_df(res['current'])
            if not df.empty:
                print("\n" + df.to_string(index=False))
                print(f"\n   Total: {len(df)} dependencies")
                
                # Save to CSV if requested
                if csv_prefix:
                    csv_filename = f"{csv_prefix}_current.csv"
                    df.to_csv(csv_filename, index=False)
                    csv_files_saved.append(csv_filename)
            else:
                print("   No dependencies found")
        
        if version_type in ['target', 'both'] and 'target' in res:
            print("\n📊 Target Version Dependencies:")
            print(f"   Version: {data.get('target_version', 'Unknown')}")
            df = format_dependencies_df(res['target'])
            if not df.empty:
                print("\n" + df.to_string(index=False))
                print(f"\n   Total: {len(df)} dependencies")
                
                # Save to CSV if requested
                if csv_prefix:
                    csv_filename = f"{csv_prefix}_target.csv"
                    df.to_csv(csv_filename, index=False)
                    csv_files_saved.append(csv_filename)
            else:
                print("   No dependencies found")
    else:
        # Single version results or direct dependency list
        print("\n📊 Dependencies:")
        df = format_dependencies_df(data)
        if not df.empty:
            print("\n" + df.to_string(index=False))
            print(f"\n   Total: {len(df)} dependencies")
            
            # Save to CSV if requested
            if csv_prefix:
                csv_filename = f"{csv_prefix}.csv"
                df.to_csv(csv_filename, index=False)
                csv_files_saved.append(csv_filename)
        else:
            print("   No dependencies found")
    
    # Print summary statistics if available
    if 'stats' in data:
        stats = data['stats']
        print("\n📈 Summary Statistics:")
        for key, value in stats.items():
            print(f"   {key.replace('_', ' ').title()}: {value}")
    
    # Print any notes or errors
    if 'notes' in data:
        print("\n📝 Notes:")
        for note in data.get('notes', []):
            print(f"   • {note}")
    
    if 'errors' in data and data['errors']:
        print("\n⚠️  Errors:")
        for error in data.get('errors', []):
            print(f"   • {error}")
    
    # Print CSV save status
    if csv_files_saved:
        print("\n💾 CSV files saved:")
        for filename in csv_files_saved:
            print(f"   • {filename}")


def main(input_source: str, version_type: str = "both", csv_prefix: Optional[str] = None):
    """
    Main function to read and display dependency data.
    
    Args:
        input_source: Can be a file path, session ID, or session URL
        version_type: 'current', 'target', or 'both'
        csv_prefix: If provided, save DataFrames to CSV files with this prefix
    """
    
    # First, try to read as a file
    if os.path.exists(input_source):
        print(f"📖 Reading from file: {input_source}")
        data = read_json_file(input_source)
        if data:
            display_dependencies(data, version_type, csv_prefix)
            return
    
    # If not a file, try as a session ID/URL
    print(f"🔍 Attempting to read as session ID/URL: {input_source}")
    session_id = parse_session_id(input_source)
    if session_id:
        print(f"📋 Reading session: {session_id}")
        data = get_session_data_from_api(session_id)
        if data:
            display_dependencies(data, version_type, csv_prefix)
            return
    
    print(f"❌ Could not read data from: {input_source}")


def list_available_files(pattern: str = "dependencies_*.json") -> list:
    """List available dependency JSON files in current directory."""
    from glob import glob
    files = glob(pattern)
    if files:
        print("\n📁 Available dependency files:")
        for i, f in enumerate(sorted(files), 1):
            size = os.path.getsize(f) / 1024  # KB
            print(f"   {i}. {f} ({size:.1f} KB)")
        return sorted(files)
    return []


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Display dependency data from JSON files or Devin sessions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Display from a JSON file
    %(prog)s dependencies_20251005_124044.json
    
    # Display from a session ID
    %(prog)s devin-092bcaf1c5544fa59f99ec0095eac782
    
    # Display from a session URL
    %(prog)s https://app.devin.ai/sessions/092bcaf1c5544fa59f99ec0095eac782
    
    # Display only current version
    %(prog)s dependencies_20251005_124044.json --version current
    
    # Display only target version
    %(prog)s dependencies_20251005_124044.json --version target
    
    # Save to CSV files
    %(prog)s dependencies_20251005_124044.json --csv deps_output
    
    # Save only current version to CSV
    %(prog)s dependencies_20251005_124044.json --version current --csv current_deps
    
    # List available files
    %(prog)s --list
        """
    )
    
    parser.add_argument(
        'input',
        nargs='?',
        help='JSON file path, session ID, or session URL'
    )
    
    parser.add_argument(
        '--version',
        choices=['current', 'target', 'both'],
        default='both',
        help='Which version dependencies to display (default: both)'
    )
    
    parser.add_argument(
        '--list',
        action='store_true',
        help='List available dependency JSON files'
    )
    
    parser.add_argument(
        '--csv',
        metavar='PREFIX',
        help='Save DataFrames to CSV files with the given prefix (e.g., --csv output will create output.csv or output_current.csv and output_target.csv)'
    )
    
    args = parser.parse_args()
    
    if args.list:
        files = list_available_files()
        if not files:
            print("No dependency JSON files found in current directory")
        sys.exit(0)
    
    if not args.input:
        # If no input provided, list available files and prompt
        files = list_available_files()
        if files:
            print("\nPlease specify an input source or use --list to see available files")
        else:
            print("Usage: display_dependencies.py <file/session> [--version current|target|both]")
        sys.exit(1)
    
    main(args.input, args.version, args.csv)
