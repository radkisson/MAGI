"""
Reflexes Module

Provides automation and action execution capabilities.
This is RIN's motor system - its ability to act in the world.
"""

import logging
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime
from enum import Enum


class ActionStatus(Enum):
    """Status of an action execution"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Action:
    """
    Represents a single executable action
    """

    def __init__(self, name: str, handler: Callable, description: str = ""):
        self.name = name
        self.handler = handler
        self.description = description
        self.logger = logging.getLogger(__name__)

    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Execute the action

        Args:
            **kwargs: Parameters for the action

        Returns:
            Execution results
        """
        try:
            self.logger.info(f"Executing action: {self.name}")
            result = self.handler(**kwargs)
            return {
                "status": ActionStatus.COMPLETED.value,
                "result": result,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Action {self.name} failed: {e}")
            return {
                "status": ActionStatus.FAILED.value,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }


class Workflow:
    """
    Represents a sequence of actions to execute
    """

    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.actions: List[Action] = []
        self.logger = logging.getLogger(__name__)

    def add_action(self, action: Action) -> None:
        """Add an action to the workflow"""
        self.actions.append(action)
        self.logger.info(f"Added action '{action.name}' to workflow '{self.name}'")

    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Execute all actions in the workflow

        Args:
            **kwargs: Parameters to pass to actions

        Returns:
            Workflow execution results
        """
        self.logger.info(f"Executing workflow: {self.name}")
        results = []

        for action in self.actions:
            result = action.execute(**kwargs)
            results.append({
                "action": action.name,
                "result": result
            })

            # Stop if an action fails
            if result["status"] == ActionStatus.FAILED.value:
                self.logger.error(f"Workflow {self.name} stopped due to failure")
                break

        return {
            "workflow": self.name,
            "status": "completed" if all(
                r["result"]["status"] == ActionStatus.COMPLETED.value
                for r in results
            ) else "failed",
            "actions": results,
            "timestamp": datetime.now().isoformat()
        }


class ReflexEngine:
    """
    Core automation engine for RIN

    Manages actions, workflows, and autonomous task execution.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)

        # Registry of available actions
        self.actions: Dict[str, Action] = {}

        # Registry of workflows
        self.workflows: Dict[str, Workflow] = {}

        # Initialize built-in actions
        self._register_builtin_actions()

        self.logger.info("ReflexEngine initialized")

    def _register_builtin_actions(self) -> None:
        """Register built-in actions"""

        def log_action(message: str) -> str:
            """Simple logging action"""
            self.logger.info(f"Log action: {message}")
            return f"Logged: {message}"

        def store_data(data: Any, key: str) -> Dict[str, Any]:
            """Store data action"""
            return {"stored": True, "key": key, "data": data}

        # Register built-in actions
        self.register_action("log", log_action, "Log a message")
        self.register_action("store", store_data, "Store data")

    def register_action(self, name: str, handler: Callable,
                        description: str = "") -> None:
        """
        Register a new action

        Args:
            name: Action name
            handler: Function to execute
            description: Action description
        """
        action = Action(name, handler, description)
        self.actions[name] = action
        self.logger.info(f"Registered action: {name}")

    def execute_action(self, action_name: str, **kwargs) -> Dict[str, Any]:
        """
        Execute a registered action

        Args:
            action_name: Name of the action to execute
            **kwargs: Parameters for the action

        Returns:
            Execution results
        """
        if action_name not in self.actions:
            return {
                "status": ActionStatus.FAILED.value,
                "error": f"Unknown action: {action_name}",
                "timestamp": datetime.now().isoformat()
            }

        return self.actions[action_name].execute(**kwargs)

    def create_workflow(self, name: str, action_names: List[str],
                        description: str = "") -> Workflow:
        """
        Create a new workflow

        Args:
            name: Workflow name
            action_names: List of action names to include
            description: Workflow description

        Returns:
            Created workflow
        """
        workflow = Workflow(name, description)

        for action_name in action_names:
            if action_name in self.actions:
                workflow.add_action(self.actions[action_name])

        self.workflows[name] = workflow
        self.logger.info(f"Created workflow: {name}")
        return workflow

    def execute_workflow(self, workflow_name: str, **kwargs) -> Dict[str, Any]:
        """
        Execute a registered workflow

        Args:
            workflow_name: Name of the workflow
            **kwargs: Parameters to pass to the workflow

        Returns:
            Execution results
        """
        if workflow_name not in self.workflows:
            return {
                "status": "failed",
                "error": f"Unknown workflow: {workflow_name}",
                "timestamp": datetime.now().isoformat()
            }

        return self.workflows[workflow_name].execute(**kwargs)

    def get_available_actions(self) -> List[str]:
        """Get list of registered actions"""
        return list(self.actions.keys())

    def get_available_workflows(self) -> List[str]:
        """Get list of registered workflows"""
        return list(self.workflows.keys())
