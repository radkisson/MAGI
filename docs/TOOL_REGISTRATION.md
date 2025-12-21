# Tool Registration & Management in Open WebUI

This guide explains how tools work in RIN and Open WebUI, and how to properly register and manage them.

## Overview

Open WebUI uses a **database-driven architecture** for tools. This means:

1. **Placing files** in `/app/backend/data/tools/` makes them *available*
2. **Importing via UI** *registers* them in the database
3. **Only registered tools** are available to the LLM

This is a security feature that prevents arbitrary code execution.

## Why Manual Registration?

| Reason | Explanation |
|--------|-------------|
| **Security** | Prevents arbitrary Python code from auto-executing |
| **Access Control** | Allows per-user tool permissions |
| **Configuration** | Enables tool-specific settings (Valves) |
| **Validation** | Ensures tools have proper structure before activation |

## Registration Methods

### Method 1: UI Import (Recommended)

1. Open WebUI: http://localhost:3000
2. Navigate to: **Workspace** → **Tools**
3. Click **"+"** or **"Import Tool"**
4. Select tools from the list
5. Toggle each tool **ON** to enable

### Method 2: API Import (Advanced)

```bash
# Get auth token (replace with your credentials)
TOKEN=$(curl -s -X POST http://localhost:3000/api/v1/auths/signin \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"yourpassword"}' \
  | jq -r '.token')

# List available tools
curl -s http://localhost:3000/api/v1/tools/ \
  -H "Authorization: Bearer $TOKEN"
```

## How Tools Load in Open WebUI

```
┌─────────────────────────────────────────┐
│          Volume Mount                   │
│  ./tools → /app/backend/data/tools      │
└────────────────┬────────────────────────┘
                 │
                 │ Files available
                 ▼
┌─────────────────────────────────────────┐
│     User clicks "Import Tool" in UI     │
└────────────────┬────────────────────────┘
                 │
                 │ UI reads file, validates
                 ▼
┌─────────────────────────────────────────┐
│     Backend API validates structure     │
│  - Checks for Tools class               │
│  - Extracts function metadata           │
│  - Validates Valves configuration       │
└────────────────┬────────────────────────┘
                 │
                 │ Stores in database
                 ▼
┌─────────────────────────────────────────┐
│    SQLite Database (webui.db)           │
│  Table: tools                           │
│  - id, name, meta, content, created_at  │
└────────────────┬────────────────────────┘
                 │
                 │ Tool now registered
                 ▼
┌─────────────────────────────────────────┐
│   LLM Function Calling Engine           │
│  - Tool appears in model context        │
│  - LLM can invoke tool functions        │
└─────────────────────────────────────────┘
```

## Common Issues & Solutions

### "Tools folder is empty in container"

**Cause**: Volume mount not configured correctly

**Solution**:
```bash
# Check docker-compose.yml has:
volumes:
  - ./tools:/app/backend/data/tools

# Verify mount
docker exec rin-cortex ls /app/backend/data/tools/
```

### "Tool import fails with syntax error"

**Cause**: Invalid Python in tool file

**Solution**:
```bash
# Check syntax locally
python3 -m py_compile tools/your_tool.py

# Fix any reported errors
```

### "Tool shows but doesn't work"

**Cause**: Missing API keys or configuration

**Solution**:
1. Check `.env` has required keys (e.g., `FIRECRAWL_API_KEY`)
2. In Open WebUI: Tools → [Tool Name] → Valves
3. Verify API key is populated

### "Tool disappears after restart"

**Cause**: This shouldn't happen - tools persist in database

**Solution**:
```bash
# Check database exists and persists
ls -la data/open-webui/webui.db

# Ensure volume is mounted
docker-compose config | grep -A5 "open-webui"
```

## Tool Development

### Required Structure

```python
from pydantic import BaseModel, Field

class Valves(BaseModel):
    """Configuration for this tool"""
    API_KEY: str = Field(
        default_factory=lambda: os.getenv("MY_API_KEY", ""),
        description="API key (auto-loaded from .env)"
    )

class Tools:
    """Tool description shown in UI"""
    
    def __init__(self):
        self.valves = Valves()
    
    def my_function(
        self,
        param: str,
        __user__: dict = {},
        __event_emitter__: Callable[[dict], Any] = None,
    ) -> str:
        """
        Function description shown in UI.
        
        Args:
            param: Parameter description
            
        Returns:
            Result description
        """
        # Your implementation
        return "result"
```

### Best Practices

1. **Use Valves for configuration** - Auto-loads from environment variables
2. **Document functions thoroughly** - Docstrings shown in UI
3. **Use event emitters** - Provide status updates during execution
4. **Handle errors gracefully** - Return helpful error messages

## References

- [Open WebUI Tools Documentation](https://docs.openwebui.com/features/plugin/tools)
- [RIN Tools README](../tools/README.md)
- [Tool Examples](../tools/)
