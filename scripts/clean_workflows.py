#!/usr/bin/env python3
"""
Fix n8n workflow JSON files by removing tag references that cause import failures.
This script cleans workflow files to ensure they can be imported into n8n without errors.
"""

import json
import os
import sys
from pathlib import Path

def clean_workflow(workflow_data):
    """Remove problematic tag references from workflow data."""
    # Remove tags array if present
    if 'tags' in workflow_data:
        del workflow_data['tags']

    # Ensure all required fields are present
    if 'active' not in workflow_data:
        workflow_data['active'] = False

    return workflow_data

def process_workflow_file(file_path):
    """Process a single workflow file."""
    try:
        with open(file_path, 'r') as f:
            workflow_data = json.load(f)

        # Clean the workflow
        cleaned_data = clean_workflow(workflow_data)

        # Write back to file
        with open(file_path, 'w') as f:
            json.dump(cleaned_data, f, indent=2)

        print(f"✅ Cleaned: {file_path.name}")
        return True
    except Exception as e:
        print(f"❌ Error processing {file_path.name}: {e}")
        return False

def main():
    """Main function to process all workflow files."""
    workflows_dir = Path("/workflows")

    if not workflows_dir.exists():
        workflows_dir = Path("workflows")

    if not workflows_dir.exists():
        print("❌ Workflows directory not found")
        sys.exit(1)

    workflow_files = list(workflows_dir.glob("*.json"))

    if not workflow_files:
        print("❌ No workflow JSON files found")
        sys.exit(1)

    print(f"📋 Found {len(workflow_files)} workflow files")
    print()

    success_count = 0
    for workflow_file in workflow_files:
        if process_workflow_file(workflow_file):
            success_count += 1

    print()
    print(f"✅ Successfully cleaned {success_count}/{len(workflow_files)} workflows")

    return 0 if success_count == len(workflow_files) else 1

if __name__ == "__main__":
    sys.exit(main())
