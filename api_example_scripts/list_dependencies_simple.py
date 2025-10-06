#!/usr/bin/env python3
"""
Simplified script to run Java dependency analysis using Devin API.
Handles both structured_output and attachment-based results.
"""

import os
import sys
import time
import json
import requests
import re
from typing import Optional, Dict, Any
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def create_session(api_key: str, repo_name: str, target_version: Optional[str] = None) -> str:
    """Create a Devin session for dependency analysis."""
    
    print(f"Creating session for {repo_name}...")
    
    # Build prompt based on whether target_version is provided
    if target_version:
        prompt = f"""!get_java_deps

Repository: {repo_name}
Target Version: {target_version}
Dual Mode: True

Please analyze the dependencies for this repository and provide the results as JSON.

You can provide the results either by:
1. Populating the structured_output API field, OR  
2. Creating a JSON file attachment (e.g., output.json)

Both methods work fine - use whichever is more convenient.

For target version analysis, just temporarily modify gradle.properties to change orchestraFrameworkVersion to {target_version}, run the dependency analysis, then revert the change. Don't use complex init scripts.

If any Gradle commands hang for more than 2 minutes without output, kill them and try a simpler approach or report what you found so far.

When complete, either change your status to finished or blocked (both are fine).

"""
    else:
        # Current version only
        prompt = f"""!get_java_deps

Repository: {repo_name}
Dual Mode: False

Please analyze the dependencies for the CURRENT version only of this repository and provide the results as JSON.

You can provide the results either by:
1. Populating the structured_output API field, OR  
2. Creating a JSON file attachment (e.g., output.json)

Both methods work fine - use whichever is more convenient.

Do NOT analyze any target version - only analyze the current version as declared in the repository.

If any Gradle commands hang for more than 2 minutes without output, kill them and try a simpler approach or report what you found so far.

When complete, either change your status to finished or blocked (both are fine).

"""
    
    url = "https://api.devin.ai/v1/sessions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "prompt": prompt,
        "title": f"Java Deps: {repo_name}",
        "idempotent": False  # Set to False to allow multiple sessions
    }
    
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    
    result = response.json()
    session_id = result['session_id']
    
    print(f"✅ Session created: {session_id}")
    print(f"   View at: {result['url']}")
    
    return session_id


def get_session_details(api_key: str, session_id: str) -> Dict[str, Any]:
    """Get current session details."""
    
    url = f"https://api.devin.ai/v1/sessions/{session_id}"
    headers = {"Authorization": f"Bearer {api_key}"}
    
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    
    return response.json()


def extract_attachment_info(message_text: str) -> Optional[tuple[str, str]]:
    """Extract attachment UUID and filename from a message.
    
    Returns:
        Tuple of (uuid, filename) or None if no attachment found
    """
    # Look for attachment pattern
    pattern = r'https://app\.devin\.ai/attachments/([a-f0-9\-]+)/([^"]+)'
    match = re.search(pattern, message_text)
    
    if match:
        return match.group(1), match.group(2)
    
    return None


def download_attachment(api_key: str, uuid: str, filename: str) -> Dict[str, Any]:
    """Download an attachment from Devin."""
    
    print(f"Downloading attachment: {filename}...")
    
    url = f"https://api.devin.ai/v1/attachments/{uuid}/{filename}"
    headers = {"Authorization": f"Bearer {api_key}"}
    
    # Use -L equivalent (follow redirects)
    response = requests.get(url, headers=headers, allow_redirects=True)
    response.raise_for_status()
    
    # Parse JSON content
    try:
        return response.json()
    except json.JSONDecodeError:
        print("⚠️  Attachment is not valid JSON")
        return {"raw_content": response.text}


def wait_for_results(
    api_key: str, 
    session_id: str,
    max_wait_minutes: int = 30,
    poll_interval_seconds: int = 10
) -> Dict[str, Any]:
    """
    Wait for session to complete and retrieve results.
    
    Returns results from either structured_output or attachment.
    """
    
    print(f"Waiting for results (max {max_wait_minutes} minutes)...")
    
    start_time = time.time()
    max_wait_seconds = max_wait_minutes * 60
    
    while True:
        elapsed = time.time() - start_time
        
        if elapsed > max_wait_seconds:
            print(f"❌ Timeout after {max_wait_minutes} minutes")
            return None
        
        # Get current session state
        details = get_session_details(api_key, session_id)
        status = details.get("status_enum")
        
        # Print status update
        elapsed_mins = int(elapsed // 60)
        elapsed_secs = int(elapsed % 60)
        print(f"   Status: {status} (elapsed: {elapsed_mins}m {elapsed_secs}s)")
        
        # Check for completion states
        if status in ["finished", "expired", "blocked"]:
            
            # First check structured_output
            structured_output = details.get("structured_output")
            if structured_output:
                print("✅ Found results in structured_output")
                return structured_output
            
            # If blocked or finished without structured_output, check for attachments
            if status in ["blocked", "finished"]:
                print("   Checking for attachments...")
                
                messages = details.get("messages", [])
                if messages:
                    # Check last few messages for attachments
                    for msg in reversed(messages[-5:]):
                        msg_text = msg.get("message", "")
                        attachment_info = extract_attachment_info(msg_text)
                        
                        if attachment_info:
                            uuid, filename = attachment_info
                            print(f"✅ Found attachment: {filename}")
                            
                            # Download and return attachment content
                            try:
                                return download_attachment(api_key, uuid, filename)
                            except Exception as e:
                                print(f"⚠️  Failed to download attachment: {e}")
                
                # If blocked without results, the task is likely complete
                if status == "blocked":
                    print("ℹ️  Session is waiting for instructions (task likely complete)")
                    print("   No structured output or attachments found")
                    print("   Check the session URL for manual results")
                    return None
            
            if status == "expired":
                print("❌ Session expired")
                return None
        
        # Continue polling
        time.sleep(poll_interval_seconds)


def print_summary(results: Dict[str, Any]):
    """Print a simple summary of the results."""
    
    if not results:
        return
    
    print("\n" + "=" * 60)
    print("RESULTS SUMMARY")
    print("=" * 60)
    
    # Handle different result structures
    if "results" in results:
        # Standard structure
        res = results["results"]
        
        if "current" in res:
            current = res["current"]
            candidates = current.get("upload_candidates", [])
            print(f"\nCurrent Version:")
            print(f"  Upload candidates: {len(candidates)}")
            
            # Show first few candidates
            if candidates:
                print(f"  Top candidates:")
                for c in candidates[:3]:
                    artifact = f"{c.get('group', '')}:{c.get('artifact', '')}:{c.get('version', '')}"
                    print(f"    • {artifact}")
        
        if "target" in res:
            target = res["target"]
            candidates = target.get("upload_candidates", [])
            print(f"\nTarget Version:")
            print(f"  Upload candidates: {len(candidates)}")
    
    elif "upload_candidates" in results:
        # Simple list structure
        candidates = results["upload_candidates"]
        print(f"\nFound {len(candidates)} upload candidates")
    
    else:
        # Unknown structure
        print("\nResults retrieved (check output file for details)")


def get_java_dependencies(
    repo_name: str,
    target_version: Optional[str] = None,
    api_key: Optional[str] = None
):
    """Get Java dependencies for a repository.
    
    Args:
        repo_name: Repository to analyze
        target_version: Target Orchestra version (optional, current only if not provided)
        api_key: Devin API key (optional, uses env var if not provided)
    
    Returns:
        Dict with dependency results or None. The structure depends on whether 
        target_version is provided:
        
        Single mode (target_version=None):
        - Returns analysis for current version only
        - Structure: {"results": {"current": {...}}, "stats": {...}, "notes": [...]}
        
        Dual mode (target_version provided):
        - Returns analysis for both current and target versions
        - Structure: {
            "dual_mode": true,
            "current_version": "X.Y.Z",
            "target_version": "3.17",
            "results": {
              "current": {
                "upload_candidates": [...],
                "unresolved": [...],
                "summary": {...}
              },
              "target": {
                "upload_candidates": [...], 
                "unresolved": [...],
                "summary": {...}
              },
              "diff": {
                "added_candidates": [...],
                "removed_candidates": [...],
                "version_changed_candidates": [...]
              }
            },
            "stats": {"current": {...}, "target": {...}},
            "notes": [...]
          }
        
        Each upload_candidates entry contains:
        - group, artifact, version, type, repository_hint, reason, is_transitive, parents
    """
    
    # Get API key
    if api_key is None:
        api_key = os.environ.get("DEVIN_API_KEY")
        if not api_key:
            print("❌ Error: DEVIN_API_KEY not found in environment")
            print("   Set it in .env file or as environment variable")
            sys.exit(1)
    
    # Print configuration
    print(f"\n📋 Configuration:")
    print(f"   Repository: {repo_name}")
    if target_version:
        print(f"   Target Version: {target_version}")
        print(f"   Mode: Dual (current + target)")
    else:
        print(f"   Mode: Current version only")
    
    try:
        # Create session
        session_id = create_session(api_key, repo_name, target_version)
        
        # Wait for results
        results = wait_for_results(api_key, session_id)
        
        if results:
            # Save results
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"dependencies_{timestamp}.json"
            
            with open(output_file, 'w') as f:
                json.dump(results, f, indent=2)
            
            print(f"\n✅ Results saved to: {output_file}")
            
            # Print summary
            print_summary(results)
        else:
            print("\n⚠️  No results retrieved")
            print(f"   Check session manually: https://app.devin.ai/sessions/{session_id}")
            return None
        
        return results
            
    except KeyboardInterrupt:
        print("\n⚠️  Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # Example usage - change these values as needed
    REPO = "wftgitsas-CHIEF-TECH-OFC-NonProd/App-ciwat-FCDEvidenceService-DevinPOC"
    TARGET = "3.17"  # Set to None for current version only
    
    results = get_java_dependencies(REPO, TARGET)
