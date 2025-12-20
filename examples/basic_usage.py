"""
Basic usage example for RIN
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from rin import Agent
from rin.sensors import SensorManager
from rin.memory import MemoryManager
from rin.reflexes import ReflexEngine
from rin.utils import setup_logging


def main():
    """Main example demonstrating RIN capabilities"""
    
    # Setup logging
    setup_logging("INFO")
    
    print("=" * 70)
    print("Rhyzomic Intelligence Node (RIN) - Basic Example")
    print("=" * 70)
    print()
    
    # Example 1: Basic Agent
    print("1. Basic Agent Usage")
    print("-" * 70)
    agent = Agent()
    print(f"Agent initialized: {agent}")
    print(f"Status: {agent.get_status()}")
    print()
    
    # Example 2: Sensors
    print("2. Using Sensors")
    print("-" * 70)
    sensors = SensorManager()
    print(f"Available sensors: {sensors.get_available_sensors()}")
    
    # Simulate web browsing
    web_result = sensors.perceive("web_browser", "https://example.com")
    print(f"Web browsing result: {web_result['status']}")
    
    # Simulate API connection
    api_result = sensors.perceive("api_connector", "https://api.example.com")
    print(f"API connection result: {api_result['status']}")
    print()
    
    # Example 3: Memory
    print("3. Using Memory")
    print("-" * 70)
    memory = MemoryManager()
    
    # Store some memories
    mem1 = memory.remember("Python is a programming language")
    mem2 = memory.remember("RIN is a sovereign AI agent")
    mem3 = memory.remember("Machine learning uses algorithms to learn patterns")
    print(f"Stored {memory.get_stats()['total']} memories")
    
    # Recall information
    results = memory.recall("programming", use_vector=False)
    print(f"Recalled {len(results)} memories about 'programming'")
    print()
    
    # Example 4: Reflexes
    print("4. Using Reflexes")
    print("-" * 70)
    reflexes = ReflexEngine()
    print(f"Available actions: {reflexes.get_available_actions()}")
    
    # Execute an action
    log_result = reflexes.execute_action("log", message="Hello from RIN!")
    print(f"Log action status: {log_result['status']}")
    
    # Create and execute a workflow
    workflow = reflexes.create_workflow(
        "demo_workflow",
        ["log", "store"],
        "Demo workflow"
    )
    workflow_result = reflexes.execute_workflow(
        "demo_workflow",
        message="Workflow started",
        data="demo_data",
        key="demo_key"
    )
    print(f"Workflow status: {workflow_result['status']}")
    print()
    
    # Example 5: Full Integration
    print("5. Full Agent Integration")
    print("-" * 70)
    
    # Query the agent
    response = agent.query("Demonstrate RIN capabilities")
    print(f"Agent response: {response}")
    
    # Execute a task
    task_result = agent.execute_task("Monitor AI news sources")
    print(f"Task: {task_result['task']}")
    print(f"Status: {task_result['status']}")
    print()
    
    print("=" * 70)
    print("Example completed successfully!")
    print("RIN is ready for sovereign AI operations.")
    print("=" * 70)


if __name__ == "__main__":
    main()
