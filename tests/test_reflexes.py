"""
Test suite for RIN Reflexes
"""

import pytest
from rin.reflexes import ReflexEngine, Action, Workflow, ActionStatus


def test_action_creation():
    """Test creating an action"""
    def test_handler(**kwargs):
        return "test_result"
    
    action = Action("test_action", test_handler, "Test description")
    assert action.name == "test_action"
    assert action.description == "Test description"


def test_action_execution():
    """Test executing an action"""
    def test_handler(value):
        return f"processed: {value}"
    
    action = Action("test", test_handler)
    result = action.execute(value="test")
    
    assert result["status"] == ActionStatus.COMPLETED.value
    assert "processed: test" in result["result"]


def test_workflow_creation():
    """Test creating a workflow"""
    workflow = Workflow("test_workflow", "Test description")
    assert workflow.name == "test_workflow"
    assert workflow.description == "Test description"


def test_workflow_add_action():
    """Test adding action to workflow"""
    workflow = Workflow("test")
    
    def test_handler():
        return "result"
    
    action = Action("test_action", test_handler)
    workflow.add_action(action)
    
    assert len(workflow.actions) == 1


def test_reflex_engine_initialization():
    """Test ReflexEngine initialization"""
    engine = ReflexEngine()
    assert engine is not None


def test_reflex_engine_builtin_actions():
    """Test that built-in actions are registered"""
    engine = ReflexEngine()
    actions = engine.get_available_actions()
    
    assert "log" in actions
    assert "store" in actions


def test_reflex_engine_register_action():
    """Test registering a new action"""
    engine = ReflexEngine()
    
    def custom_action(value):
        return f"custom: {value}"
    
    engine.register_action("custom", custom_action, "Custom action")
    
    assert "custom" in engine.get_available_actions()


def test_reflex_engine_execute_action():
    """Test executing an action"""
    engine = ReflexEngine()
    result = engine.execute_action("log", message="test message")
    
    assert result["status"] == ActionStatus.COMPLETED.value


def test_reflex_engine_execute_invalid_action():
    """Test executing invalid action"""
    engine = ReflexEngine()
    result = engine.execute_action("nonexistent")
    
    assert result["status"] == ActionStatus.FAILED.value


def test_reflex_engine_create_workflow():
    """Test creating a workflow"""
    engine = ReflexEngine()
    
    workflow = engine.create_workflow(
        "test_workflow",
        ["log", "store"],
        "Test workflow"
    )
    
    assert workflow.name == "test_workflow"
    assert len(workflow.actions) == 2


def test_reflex_engine_execute_workflow():
    """Test executing a workflow"""
    engine = ReflexEngine()
    
    engine.create_workflow("test_workflow", ["log"], "Test")
    result = engine.execute_workflow("test_workflow", message="test")
    
    assert result["workflow"] == "test_workflow"


def test_reflex_engine_execute_invalid_workflow():
    """Test executing invalid workflow"""
    engine = ReflexEngine()
    result = engine.execute_workflow("nonexistent")
    
    assert result["status"] == "failed"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
