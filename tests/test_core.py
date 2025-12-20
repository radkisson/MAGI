"""
Test suite for RIN Core Agent
"""

import pytest
from rin import Agent


def test_agent_initialization():
    """Test that agent initializes correctly"""
    agent = Agent()
    assert agent is not None
    assert agent.version == "1.2.0"
    assert agent.status == "Active Development"


def test_agent_status():
    """Test agent status reporting"""
    agent = Agent()
    status = agent.get_status()
    
    assert "version" in status
    assert "status" in status
    assert "classification" in status
    assert status["version"] == "1.2.0"
    assert status["classification"] == "Sovereign AI Infrastructure"


def test_agent_query():
    """Test agent query processing"""
    agent = Agent()
    response = agent.query("Test query")
    
    assert response is not None
    assert isinstance(response, str)
    assert "RIN Agent" in response


def test_agent_execute_task():
    """Test agent task execution"""
    agent = Agent()
    result = agent.execute_task("Test task")
    
    assert result is not None
    assert "status" in result
    assert "task" in result
    assert result["task"] == "Test task"


def test_agent_with_config():
    """Test agent initialization with config"""
    config = {"test_key": "test_value"}
    agent = Agent(config=config)
    
    assert agent.config == config
    assert agent.config["test_key"] == "test_value"


def test_agent_repr():
    """Test agent string representation"""
    agent = Agent()
    repr_str = repr(agent)
    
    assert "RIN Agent" in repr_str
    assert "1.2.0" in repr_str


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
