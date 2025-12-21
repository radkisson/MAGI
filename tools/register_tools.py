#!/usr/bin/env python3
"""
Auto-register RIN tools into Open WebUI database.

This script directly inserts tools into Open WebUI's SQLite database,
bypassing the need for manual UI registration.

Usage:
    docker exec rin-cortex python3 /app/backend/data/tools/register_tools.py

Or from host:
    docker cp scripts/register_tools.py rin-cortex:/tmp/
    docker exec rin-cortex python3 /tmp/register_tools.py
"""

import sqlite3
import json
import time
import os
import sys
import importlib.util
import inspect
from pathlib import Path


def get_tool_specs(tools_instance):
    """Extract function specs from a Tools class instance."""
    specs = []
    
    for method_name in dir(tools_instance):
        # Skip private methods and non-callables
        if method_name.startswith('_'):
            continue
        
        method = getattr(tools_instance, method_name)
        if not callable(method):
            continue
        
        # Skip if it's a class attribute, not a method
        if not inspect.ismethod(method):
            continue
        
        # Get function signature
        sig = inspect.signature(method)
        docstring = inspect.getdoc(method) or f"Function: {method_name}"
        
        # Build parameters
        properties = {}
        required = []
        
        for param_name, param in sig.parameters.items():
            # Skip special parameters
            if param_name in ('self', '__user__', '__event_emitter__'):
                continue
            
            # Determine type
            param_type = "string"
            if param.annotation != inspect.Parameter.empty:
                if param.annotation == int:
                    param_type = "integer"
                elif param.annotation == float:
                    param_type = "number"
                elif param.annotation == bool:
                    param_type = "boolean"
            
            properties[param_name] = {
                "type": param_type,
                "description": f"Parameter: {param_name}"
            }
            
            # Check if required (no default value)
            if param.default == inspect.Parameter.empty:
                required.append(param_name)
        
        spec = {
            "name": method_name,
            "description": docstring.split('\n')[0],  # First line of docstring
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required
            }
        }
        specs.append(spec)
    
    return specs


def load_tool_module(tool_path: Path):
    """Load a tool module from file path."""
    spec = importlib.util.spec_from_file_location(tool_path.stem, tool_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[tool_path.stem] = module
    spec.loader.exec_module(module)
    return module


def register_tool(db_path: str, tool_id: str, tool_path: Path, user_id: str):
    """Register a single tool in the database."""
    
    # Read tool content
    with open(tool_path, 'r') as f:
        content = f.read()
    
    # Load and inspect the module
    try:
        module = load_tool_module(tool_path)
        
        if not hasattr(module, 'Tools'):
            print(f"  ⚠️  {tool_id}: No 'Tools' class found, skipping")
            return False
        
        tools_class = getattr(module, 'Tools')
        tools_instance = tools_class()
        
        # Get specs
        specs = get_tool_specs(tools_instance)
        
        if not specs:
            print(f"  ⚠️  {tool_id}: No functions found, skipping")
            return False
        
        # Extract description from docstring
        description = ""
        if tools_class.__doc__:
            description = tools_class.__doc__.strip()
        elif module.__doc__:
            description = module.__doc__.strip().split('\n')[0]
        
        # Prepare meta
        meta = {
            "description": description,
            "manifest": {}
        }
        
        # Current timestamp
        now = int(time.time())
        
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if tool already exists
        cursor.execute("SELECT id FROM tool WHERE id = ?", (tool_id,))
        if cursor.fetchone():
            print(f"  ℹ️  {tool_id}: Already registered, skipping")
            conn.close()
            return True
        
        # Insert tool
        cursor.execute("""
            INSERT INTO tool (id, user_id, name, content, specs, meta, valves, access_control, updated_at, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            tool_id,
            user_id,
            tool_id.replace('_', ' ').title(),  # Human-readable name
            content,
            json.dumps(specs),
            json.dumps(meta),
            json.dumps({}),  # Empty valves (will use defaults from Valves class)
            None,  # Public access
            now,
            now
        ))
        
        conn.commit()
        conn.close()
        
        print(f"  ✅ {tool_id}: Registered with {len(specs)} function(s)")
        return True
        
    except Exception as e:
        print(f"  ❌ {tool_id}: Error - {str(e)}")
        return False


def get_admin_user_id(db_path: str) -> str:
    """Get the first admin user ID from the database."""
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        
        # Try to find an admin user
        cursor.execute("SELECT id FROM user WHERE role = 'admin' LIMIT 1")
        row = cursor.fetchone()
        
        if row:
            user_id = row[0]
            return user_id
        
        # If no admin, get any user
        cursor.execute("SELECT id FROM user LIMIT 1")
        row = cursor.fetchone()
        
        if row:
            user_id = row[0]
            return user_id
        
        return "system"


def main():
    # Paths
    db_path = "/app/backend/data/webui.db"
    tools_dir = Path("/app/backend/data/tools")
    
    # Check if running inside container
    if not os.path.exists(db_path):
        print("❌ Database not found at", db_path)
        print("   This script must run inside the rin-cortex container")
        print("")
        print("   Usage:")
        print("   docker exec rin-cortex python3 /app/backend/data/tools/register_tools.py")
        sys.exit(1)
    
    if not tools_dir.exists():
        print("❌ Tools directory not found at", tools_dir)
        sys.exit(1)
    
    # Get admin user ID
    user_id = get_admin_user_id(db_path)
    print(f"📋 Using user ID: {user_id}")
    print("")
    
    # Find all tool files
    tool_files = [f for f in tools_dir.glob("*.py") 
                  if not f.name.startswith('_') 
                  and f.name != 'register_tools.py'
                  and f.name != 'check_tools.sh']
    
    if not tool_files:
        print("❌ No tool files found in", tools_dir)
        sys.exit(1)
    
    print(f"🔧 Found {len(tool_files)} tool(s) to register:")
    print("")
    
    success_count = 0
    for tool_path in sorted(tool_files):
        tool_id = tool_path.stem
        if register_tool(db_path, tool_id, tool_path, user_id):
            success_count += 1
    
    print("")
    print(f"✅ Registered {success_count}/{len(tool_files)} tools")
    print("")
    print("🔄 Restart Open WebUI to apply changes:")
    print("   docker restart rin-cortex")
    print("")
    print("📍 Or refresh the browser and go to Workspace → Tools")


if __name__ == "__main__":
    main()
