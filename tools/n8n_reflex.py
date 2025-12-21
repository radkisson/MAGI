"""
n8n Reflex Tool for Open WebUI

This tool creates the "Synaptic Bridge" between the Cortex (Open WebUI) and 
the Reflex Arc (n8n), allowing the brain to trigger autonomous workflows.

Two Operational Modes:
- trigger_reflex(): Fire-and-forget actions (email, notifications, start long tasks)
- query_workflow(): Cognitive loop - wait for and return data (research, lookups)

Use Cases:
- "RIN, send an email to my team" → trigger_reflex (fire-and-forget)
- "RIN, research this company and tell me what you find" → query_workflow (wait for data)
"""

import os
import json
import time
import threading
import requests
from typing import Callable, Any
from pydantic import BaseModel, Field


class Valves(BaseModel):
    """Configuration valves for n8n Reflex integration (tunable via UI)"""
    
    N8N_WEBHOOK_URL: str = Field(
        default_factory=lambda: os.getenv("N8N_WEBHOOK_URL", "http://rin-reflex-automation:5678/webhook"),
        description="n8n webhook base URL (default: internal Docker DNS)"
    )
    COGNITIVE_TIMEOUT: int = Field(
        default=300,
        description="Timeout in seconds for cognitive (blocking) workflows (default: 300s = 5 minutes)"
    )
    REFLEX_TIMEOUT: int = Field(
        default=10,
        description="Timeout in seconds for reflex (fire-and-forget) workflows (default: 10s)"
    )
    PULSE_INTERVAL: int = Field(
        default=15,
        description="Interval in seconds between 'waiting' status updates for cognitive workflows"
    )


class Tools:
    """Open WebUI Tool: Synaptic Bridge to n8n Workflow Automation
    
    Provides two distinct modes of operation:
    - trigger_reflex: Fire-and-forget (actions like email, notifications)
    - query_workflow: Cognitive loop (research, data retrieval - waits for response)
    """
    
    def __init__(self):
        self.valves = Valves()
    
    def _validate_workflow_id(self, workflow_id: str) -> tuple[bool, str]:
        """Validate workflow_id to ensure it's safe for URL construction."""
        if not workflow_id:
            return False, "Workflow ID cannot be empty"
        
        # Only allow alphanumeric, hyphens, and underscores
        import re
        if not re.match(r'^[a-zA-Z0-9_-]+$', workflow_id):
            return False, "Workflow ID can only contain letters, numbers, hyphens, and underscores"
        
        return True, ""
    
    def _parse_payload(self, payload: str) -> dict:
        """Parse payload string into structured data."""
        try:
            if payload and (payload.startswith('{') or payload.startswith('[')):
                return {"data": json.loads(payload)}
            else:
                return {"data": payload}
        except (json.JSONDecodeError, AttributeError):
            return {"data": payload}
    
    def _emit_status(self, emitter: Callable, description: str, done: bool = False):
        """Emit a status update to the UI."""
        if emitter:
            emitter({
                "type": "status",
                "data": {
                    "description": description,
                    "done": done,
                },
            })
    
    def trigger_reflex(
        self,
        workflow_id: str,
        payload: str,
        __user__: dict = {},
        __event_emitter__: Callable[[dict], Any] = None,
    ) -> str:
        """
        Fire-and-forget: Triggers an autonomous action in the Nervous System (n8n).
        
        Use this for ACTIONS that don't need to return data to the conversation:
        - Sending emails
        - Posting notifications (Slack, Telegram)
        - Starting long-running background tasks
        - Triggering external integrations
        
        The workflow runs autonomously in the background. This function returns
        immediately after n8n acknowledges the request.
        
        Args:
            workflow_id: The webhook path of the workflow (e.g., 'send-email', 'slack-notify')
            payload: Data to send to the workflow (string or JSON string)
            
        Returns:
            Confirmation that the reflex was triggered
            
        Examples:
            workflow_id: "send-email"
            payload: '{"to": "boss@company.com", "subject": "Report", "body": "..."}'
            
            workflow_id: "slack-notify"
            payload: '{"channel": "#alerts", "message": "Task completed"}'
        """
        
        # Validate workflow_id
        is_valid, error_msg = self._validate_workflow_id(workflow_id)
        if not is_valid:
            self._emit_status(__event_emitter__, f"❌ Invalid workflow ID", done=True)
            return f"❌ Invalid Workflow ID: {error_msg}"
        
        self._emit_status(__event_emitter__, f"⚡ Triggering reflex: {workflow_id}")
        
        url = f"{self.valves.N8N_WEBHOOK_URL}/{workflow_id}"
        data = self._parse_payload(payload)
        
        try:
            response = requests.post(
                url,
                json=data,
                headers={"Content-Type": "application/json"},
                timeout=self.valves.REFLEX_TIMEOUT
            )
            
            self._emit_status(__event_emitter__, "✅ Reflex triggered", done=True)
            
            if response.status_code == 200:
                return (
                    f"✅ Reflex Arc activated.\n\n"
                    f"**Workflow**: `{workflow_id}`\n"
                    f"**Status**: Running autonomously in the Nervous System\n\n"
                    f"The action has been initiated and will complete in the background."
                )
            else:
                return (
                    f"⚠️ Reflex response: {response.status_code}\n\n"
                    f"The workflow may not have triggered correctly.\n"
                    f"Check n8n dashboard: http://localhost:5678"
                )
                
        except requests.exceptions.Timeout:
            self._emit_status(__event_emitter__, "⏱️ Reflex acknowledged (async)", done=True)
            return (
                f"⏱️ Reflex initiated.\n\n"
                f"**Workflow**: `{workflow_id}`\n"
                f"**Status**: Running (did not wait for completion)\n\n"
                f"The workflow is executing. Check n8n for progress."
            )
            
        except requests.exceptions.ConnectionError:
            self._emit_status(__event_emitter__, "❌ Connection failed", done=True)
            return (
                f"❌ Nervous System Failure\n\n"
                f"Cannot reach n8n at `{url}`\n\n"
                f"**Troubleshooting**:\n"
                f"1. Check if n8n is running: `docker ps | grep rin-reflex`\n"
                f"2. Restart n8n: `docker restart rin-reflex-automation`"
            )
            
        except Exception as e:
            self._emit_status(__event_emitter__, "❌ Error", done=True)
            return f"❌ Synaptic Bridge Error: {str(e)}"
    
    def query_workflow(
        self,
        workflow_id: str,
        payload: str,
        __user__: dict = {},
        __event_emitter__: Callable[[dict], Any] = None,
    ) -> str:
        """
        Cognitive Loop: Queries a workflow and waits for the response data.
        
        Use this when you need DATA back from n8n to continue the conversation:
        - Research tasks (search, scrape, synthesize)
        - Data lookups (API queries, database reads)
        - Any workflow where the AI needs the result to answer the user
        
        This function BLOCKS until n8n completes and returns the result.
        The n8n workflow MUST use "Respond to Webhook" node to return data.
        
        Args:
            workflow_id: The webhook path of the workflow (e.g., 'research', 'lookup')
            payload: Query data to send to the workflow (string or JSON string)
            
        Returns:
            Raw JSON response from the workflow (for the LLM to interpret)
            
        Examples:
            workflow_id: "research"
            payload: "Tesla Inc quarterly earnings"
            
            workflow_id: "company-lookup"
            payload: '{"company": "OpenAI", "fields": ["funding", "employees"]}'
        """
        
        # Validate workflow_id
        is_valid, error_msg = self._validate_workflow_id(workflow_id)
        if not is_valid:
            self._emit_status(__event_emitter__, f"❌ Invalid workflow ID", done=True)
            return f"❌ Invalid Workflow ID: {error_msg}"
        
        self._emit_status(__event_emitter__, f"🧠 Initiating cognitive query: {workflow_id}")
        
        url = f"{self.valves.N8N_WEBHOOK_URL}/{workflow_id}"
        data = self._parse_payload(payload)
        
        # Use requests with streaming to allow pulse updates
        start_time = time.time()
        pulse_interval = self.valves.PULSE_INTERVAL
        timeout = self.valves.COGNITIVE_TIMEOUT
        
        try:
            # Start the request with a longer timeout
            self._emit_status(__event_emitter__, "🔄 Waiting for Nervous System response...")
            
            # Thread-safe result storage using Lock
            result_lock = threading.Lock()
            result = {"response": None, "error": None, "done": False}
            
            def make_request():
                with requests.Session() as session:
                    try:
                        response = session.post(
                            url,
                            json=data,
                            headers={"Content-Type": "application/json"},
                            timeout=timeout
                        )
                        with result_lock:
                            result["response"] = response
                    except Exception as e:
                        with result_lock:
                            result["error"] = e
                    finally:
                        with result_lock:
                            result["done"] = True
            
            # Start request in daemon thread (will be cleaned up automatically)
            request_thread = threading.Thread(target=make_request, daemon=True)
            request_thread.start()
            
            # Emit pulse updates while waiting
            pulse_count = 0
            last_pulse_time = start_time
            
            while True:
                time.sleep(1)  # Check every second
                elapsed = time.time() - start_time
                
                # Check if request is done first (before timeout check)
                with result_lock:
                    is_done = result["done"]
                
                if is_done:
                    break
                
                # Check timeout
                if elapsed > timeout:
                    break
                
                # Emit pulse at regular intervals
                if elapsed - (last_pulse_time - start_time) >= pulse_interval:
                    pulse_count += 1
                    last_pulse_time = time.time()
                    self._emit_status(
                        __event_emitter__,
                        f"🔄 Waiting for Nervous System... ({int(elapsed)}s elapsed)"
                    )
            
            # Wait for thread to complete (up to 5 seconds)
            request_thread.join(timeout=5)
            
            # Get final results with lock
            with result_lock:
                final_error = result["error"]
                final_response = result["response"]
                is_done = result["done"]
            
            if final_error:
                raise final_error
            
            if not is_done or final_response is None:
                raise requests.exceptions.Timeout("Request did not complete")
            
            response = final_response
            elapsed_total = time.time() - start_time
            
            self._emit_status(
                __event_emitter__,
                f"✅ Cognitive query complete ({int(elapsed_total)}s)",
                done=True
            )
            
            if response.status_code == 200:
                # Return raw JSON for LLM to interpret
                try:
                    response_data = response.json()
                    return json.dumps(response_data, indent=2)
                except json.JSONDecodeError:
                    return response.text
            else:
                response_text = response.text
                max_len = 500
                display_text = response_text[:max_len]
                if len(response_text) > max_len:
                    display_text += "... [truncated]"
                return (
                    f"⚠️ Workflow returned status {response.status_code}\n\n"
                    f"Response: {display_text}"
                )
                
        except requests.exceptions.Timeout:
            elapsed = time.time() - start_time
            self._emit_status(__event_emitter__, f"⏱️ Timeout after {int(elapsed)}s", done=True)
            return (
                f"⏱️ Cognitive Query Timeout\n\n"
                f"**Workflow**: `{workflow_id}`\n"
                f"**Elapsed**: {int(elapsed)} seconds\n"
                f"**Limit**: {timeout} seconds\n\n"
                f"The workflow is taking longer than expected. It may still be running.\n"
                f"Check n8n dashboard or try again later."
            )
            
        except requests.exceptions.ConnectionError:
            self._emit_status(__event_emitter__, "❌ Connection failed", done=True)
            return (
                f"❌ Nervous System Unreachable\n\n"
                f"Cannot connect to n8n at `{url}`\n\n"
                f"Ensure the n8n container is running."
            )
            
        except Exception as e:
            self._emit_status(__event_emitter__, "❌ Error", done=True)
            return f"❌ Cognitive Query Error: {str(e)}"
    
    def list_workflows(
        self,
        __user__: dict = {},
        __event_emitter__: Callable[[dict], Any] = None,
    ) -> str:
        """
        Lists available n8n workflows and their operational modes.
        
        Returns documentation on available workflows and how to use them
        with either trigger_reflex() or query_workflow().
        """
        
        return """
# Available n8n Workflows (Reflex Arc)

## 🔥 Reflex Workflows (Fire-and-Forget)
Use `trigger_reflex(workflow_id, payload)` for these:

| Workflow | Webhook ID | Purpose |
|----------|------------|---------|
| Send Email | `send-email` | Send emails via SMTP |
| Slack Notify | `slack-notify` | Post to Slack channels |
| Telegram Send | `telegram-send` | Send Telegram messages |

## 🧠 Cognitive Workflows (Wait for Response)
Use `query_workflow(workflow_id, payload)` for these:

| Workflow | Webhook ID | Purpose |
|----------|------------|---------|
| Research Agent | `research` | Deep research with sources |
| OpenWebUI Action | `openwebui-action` | General-purpose router |

## ⏰ Scheduled Workflows (Autonomous)
These run automatically, no trigger needed:

| Workflow | Schedule | Purpose |
|----------|----------|---------|
| Morning Briefing | 8:00 AM daily | Tech news summary |
| RSS Monitor | Every 6 hours | Feed digest |
| Daily Report | 6:00 PM daily | Intelligence report |

## Usage Examples

**Fire-and-forget (email):**
```
trigger_reflex("send-email", '{"to": "user@example.com", "subject": "Hello", "body": "..."}')
```

**Cognitive query (research):**
```
query_workflow("research", "Latest developments in quantum computing")
```

## Configuration

Timeouts can be adjusted in the tool's Valves settings:
- Cognitive Timeout: {cognitive_timeout}s (default: 300s)
- Reflex Timeout: {reflex_timeout}s (default: 10s)
""".format(
            cognitive_timeout=self.valves.COGNITIVE_TIMEOUT,
            reflex_timeout=self.valves.REFLEX_TIMEOUT
        )
