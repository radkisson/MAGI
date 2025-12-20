# RIN Examples

This directory contains examples demonstrating various capabilities of the Rhyzomic Intelligence Node.

## Basic Examples

### Example 1: Simple Query

```python
from rin import Agent

# Initialize agent
agent = Agent()

# Ask a question
response = agent.query("What is artificial intelligence?")
print(response)
```

### Example 2: Using Sensors

```python
from rin.sensors import SensorManager

# Initialize sensor manager
sensors = SensorManager()

# Browse a website
result = sensors.perceive("web_browser", "https://example.com")
print(result)

# Connect to an API
api_result = sensors.perceive("api_connector", "https://api.example.com/data")
print(api_result)
```

### Example 3: Using Memory

```python
from rin.memory import MemoryManager

# Initialize memory manager
memory = MemoryManager()

# Store a memory
mem_id = memory.remember("Python is a programming language", memory_type="vector")
print(f"Stored memory: {mem_id}")

# Recall information
results = memory.recall("programming language")
for result in results:
    print(result)

# Get memory statistics
stats = memory.get_stats()
print(f"Total memories: {stats['total']}")
```

### Example 4: Using Reflexes

```python
from rin.reflexes import ReflexEngine

# Initialize reflex engine
reflexes = ReflexEngine()

# Register a custom action
def greet(name):
    return f"Hello, {name}!"

reflexes.register_action("greet", greet, "Greet someone")

# Execute the action
result = reflexes.execute_action("greet", name="World")
print(result)

# Create and execute a workflow
workflow = reflexes.create_workflow(
    "greeting_workflow",
    ["log", "greet"],
    "Workflow for greeting"
)

workflow_result = reflexes.execute_workflow(
    "greeting_workflow",
    message="Starting greeting",
    name="RIN User"
)
print(workflow_result)
```

### Example 5: Full Agent with All Components

```python
from rin import Agent
from rin.sensors import SensorManager
from rin.memory import MemoryManager
from rin.reflexes import ReflexEngine

class FullRINAgent(Agent):
    """Extended RIN agent with all components initialized"""
    
    def __init__(self, config=None):
        super().__init__(config)
        
        # Initialize all subsystems
        self._sensors = SensorManager(config)
        self._memory = MemoryManager(config)
        self._reflexes = ReflexEngine(config)
        
        self.logger.info("Full RIN agent initialized with all components")
    
    def autonomous_research(self, topic):
        """Perform autonomous research on a topic"""
        # Use sensors to gather information
        self.logger.info(f"Researching topic: {topic}")
        
        # Store findings in memory
        self._memory.remember(f"Researching: {topic}")
        
        # Execute reflexes to organize findings
        self._reflexes.execute_action("log", message=f"Completed research on {topic}")
        
        return {
            "topic": topic,
            "status": "completed",
            "memory_stats": self._memory.get_stats()
        }

# Use the full agent
agent = FullRINAgent()
result = agent.autonomous_research("Quantum Computing")
print(result)
```

## Advanced Examples

### Example 6: Automated Monitoring

```python
from rin import Agent
import time

agent = Agent()

def monitor_source(url, interval=60):
    """Monitor a source periodically"""
    while True:
        result = agent.execute_task(f"Check {url} for updates")
        print(f"Monitoring result: {result}")
        time.sleep(interval)

# Start monitoring (in a separate thread/process in production)
# monitor_source("https://news.ycombinator.com", interval=300)
```

### Example 7: Custom Sensor Implementation

```python
from rin.sensors.browser import BaseSensor
from datetime import datetime

class CustomAPISensor(BaseSensor):
    """Custom sensor for a specific API"""
    
    def perceive(self, target):
        # Your custom logic here
        return {
            "source": "custom_api",
            "target": target,
            "timestamp": datetime.now().isoformat(),
            "data": "Custom sensor data"
        }

# Use the custom sensor
custom_sensor = CustomAPISensor()
result = custom_sensor.perceive("custom_endpoint")
print(result)
```

## Running Examples

Each example can be run independently:

```bash
# Copy an example to a Python file
# For example, copy Example 1 to test.py

python test.py
```

Or use them in an interactive Python session:

```bash
python
>>> from rin import Agent
>>> agent = Agent()
>>> agent.query("Hello RIN!")
```

## Contributing Examples

Have a cool use case? Contribute your examples:

1. Create a new file in `examples/`
2. Add documentation
3. Submit a pull request

## More Resources

- [API Documentation](API.md)
- [Architecture Guide](../DESIGN.md)
- [Getting Started](GETTING_STARTED.md)
