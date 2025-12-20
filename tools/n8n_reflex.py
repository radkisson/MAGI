"""
n8n Reflex Tool for Open WebUI

This tool creates the "Synaptic Bridge" between the Cortex (Open WebUI) and 
the Reflex Arc (n8n), allowing the brain to trigger autonomous workflows.

Use Cases:
- "RIN, research this company and email me the report"
- "RIN, monitor this RSS feed and notify me of updates"
- "RIN, schedule a daily summary of my starred repositories"
"""

import requests
from typing import Callable, Any


class Tools:
    """Open WebUI Tool: Trigger n8n Workflows (Synaptic Bridge)"""
    
    def __init__(self):
        # Internal Docker DNS for n8n
        self.n8n_url = "http://rin-reflex-automation:5678/webhook"
    
    def trigger_workflow(
        self,
        workflow_id: str,
        payload: str,
        __user__: dict = {},
        __event_emitter__: Callable[[dict], Any] = None,
    ) -> str:
        """
        Triggers an autonomous workflow in the Nervous System (n8n).
        
        This creates a "synaptic bridge" allowing the Cortex (brain) to control
        the Reflex Arc (autonomous actions). When you ask RIN to perform a task
        that requires automation or external integrations, this tool triggers
        the appropriate n8n workflow.
        
        Args:
            workflow_id: The ID of the workflow to run (e.g., 'research-agent', 'email-report')
            payload: The data to send to the workflow (e.g., company name, report content)
            __user__: User context (provided by Open WebUI)
            __event_emitter__: Event emitter for streaming results (provided by Open WebUI)
            
        Returns:
            Status message indicating whether the reflex was triggered successfully
            
        Examples:
            workflow_id: "research-agent"
            payload: "Tesla Inc"
            
            workflow_id: "email-report"
            payload: '{"to": "boss@company.com", "subject": "Weekly Report", "body": "..."}'
        """
        
        if __event_emitter__:
            __event_emitter__(
                {
                    "type": "status",
                    "data": {
                        "description": f"Triggering reflex workflow: {workflow_id}",
                        "done": False,
                    },
                }
            )
        
        url = f"{self.n8n_url}/{workflow_id}"
        headers = {"Content-Type": "application/json"}
        
        # Parse payload if it's a string that looks like JSON
        try:
            import json
            if payload.startswith('{') or payload.startswith('['):
                data = {"data": json.loads(payload)}
            else:
                data = {"data": payload}
        except:
            data = {"data": payload}
        
        try:
            response = requests.post(url, json=data, headers=headers, timeout=10)
            
            if __event_emitter__:
                __event_emitter__(
                    {
                        "type": "status",
                        "data": {
                            "description": f"Reflex triggered successfully",
                            "done": True,
                        },
                    }
                )
            
            if response.status_code == 200:
                return f"✅ Reflex Arc activated. Workflow '{workflow_id}' is now running autonomously.\n\nResponse: {response.status_code}\n\nThe Nervous System is processing your request in the background."
            else:
                return f"⚠️ Reflex response code: {response.status_code}\n\nWorkflow may not have triggered correctly. Check n8n at http://localhost:5678 for details."
                
        except requests.exceptions.Timeout:
            return f"⏱️ Reflex timeout: Workflow triggered but taking longer than expected. It may still be running.\n\nCheck n8n dashboard at http://localhost:5678"
            
        except requests.exceptions.ConnectionError:
            return f"❌ Nervous System Failure: Cannot reach n8n at {url}\n\nIs the n8n container running? Try: docker ps | grep rin-reflex-automation"
            
        except Exception as e:
            return f"❌ Synaptic Bridge Error: {str(e)}\n\nThe connection between Cortex and Reflex failed."
    
    def list_workflows(
        self,
        __user__: dict = {},
        __event_emitter__: Callable[[dict], Any] = None,
    ) -> str:
        """
        Lists available n8n workflows that can be triggered.
        
        This allows RIN to discover what autonomous capabilities are available
        in the Reflex Arc (n8n).
        
        Args:
            __user__: User context (provided by Open WebUI)
            __event_emitter__: Event emitter for streaming results (provided by Open WebUI)
            
        Returns:
            A list of available workflows and their webhook IDs
        """
        
        # Note: This would require n8n API access. For now, we'll return documentation.
        workflows = """
Available n8n Workflows (Reflex Arc Capabilities):

📋 Pre-configured Workflows:
   - morning_briefing: Autonomous 8 AM news summary (scheduled, no trigger needed)

🔧 To Create Custom Workflows:
   1. Access n8n at http://localhost:5678
   2. Create a workflow with a Webhook trigger
   3. Set webhook name (e.g., 'research-agent', 'email-report')
   4. Use trigger_workflow() with that webhook name

🧠 Synaptic Bridge Pattern:
   Cortex (You) → trigger_workflow() → Reflex Arc (n8n) → External Actions

Example:
   trigger_workflow("email-report", '{"to": "boss@example.com", "body": "..."}')
"""
        return workflows
