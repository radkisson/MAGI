# API Documentation

## RIN Core API

### Agent Class

The main entry point for interacting with RIN.

```python
from rin import Agent

agent = Agent(config=None)
```

#### Methods

##### `query(prompt: str) -> str`

Process a query through the agent's systems.

**Parameters:**
- `prompt` (str): The input query or task

**Returns:**
- str: The agent's response

**Example:**
```python
response = agent.query("What are the latest AI developments?")
```

##### `execute_task(task: str) -> Dict[str, Any]`

Execute an autonomous task.

**Parameters:**
- `task` (str): Description of the task to execute

**Returns:**
- dict: Task execution status and results

**Example:**
```python
result = agent.execute_task("Monitor tech news")
```

##### `get_status() -> Dict[str, Any]`

Get the current status of the agent.

**Returns:**
- dict: Status information including version, subsystem states

**Example:**
```python
status = agent.get_status()
print(status["version"])
```

---

## Sensors Module

### SensorManager Class

Manages all sensor instances and coordinates perception.

```python
from rin.sensors import SensorManager

manager = SensorManager(config=None)
```

#### Methods

##### `perceive(sensor_type: str, target: str) -> Dict[str, Any]`

Use a specific sensor to perceive a target.

**Parameters:**
- `sensor_type` (str): Type of sensor ("web_browser", "api_connector")
- `target` (str): Target to perceive (URL, endpoint, etc.)

**Returns:**
- dict: Perception results

**Example:**
```python
result = manager.perceive("web_browser", "https://example.com")
```

##### `get_available_sensors() -> List[str]`

Get list of available sensor types.

**Returns:**
- list: Available sensor names

---

### WebBrowser Sensor

Web browsing sensor for real-time information gathering.

```python
from rin.sensors import WebBrowser

browser = WebBrowser(config=None)
```

#### Methods

##### `perceive(target: str) -> Dict[str, Any]`

Browse a web page and extract content.

**Parameters:**
- `target` (str): URL to browse

**Returns:**
- dict: Extracted content and metadata

---

### APIConnector Sensor

API connector sensor for external data sources.

```python
from rin.sensors import APIConnector

connector = APIConnector(config=None)
```

#### Methods

##### `perceive(target: str) -> Dict[str, Any]`

Connect to an API endpoint.

**Parameters:**
- `target` (str): API endpoint URL

**Returns:**
- dict: API response data

---

## Memory Module

### MemoryManager Class

Manages all memory systems for RIN.

```python
from rin.memory import MemoryManager

memory = MemoryManager(config=None)
```

#### Methods

##### `remember(content: str, memory_type: str = "vector", metadata: Dict = None) -> str`

Store a memory.

**Parameters:**
- `content` (str): Content to remember
- `memory_type` (str): Type of memory storage ("vector" or "simple")
- `metadata` (dict, optional): Optional metadata

**Returns:**
- str: Memory ID

**Example:**
```python
mem_id = memory.remember("Python is a programming language")
```

##### `recall(query: str, use_vector: bool = True) -> List[Dict[str, Any]]`

Recall memories based on a query.

**Parameters:**
- `query` (str): What to recall
- `use_vector` (bool): Whether to use vector similarity search

**Returns:**
- list: Relevant memories

**Example:**
```python
results = memory.recall("programming")
```

##### `get_stats() -> Dict[str, Any]`

Get memory system statistics.

**Returns:**
- dict: Memory statistics

---

### MemoryStore Class

Base memory storage system.

```python
from rin.memory import MemoryStore

store = MemoryStore(config=None)
```

#### Methods

##### `store(key: str, value: Any, metadata: Dict = None) -> bool`

Store a value in memory.

##### `retrieve(key: str) -> Optional[Any]`

Retrieve a value from memory.

##### `search(query: str) -> List[Dict[str, Any]]`

Search memories by query.

---

### VectorMemory Class

Vector-based memory system for semantic search.

```python
from rin.memory import VectorMemory

vector_mem = VectorMemory(config=None)
```

#### Methods

##### `embed(text: str) -> List[float]`

Generate embedding for text.

##### `store_vector(text: str, metadata: Dict = None) -> str`

Store text with its vector embedding.

##### `similarity_search(query: str, top_k: int = 5) -> List[Dict[str, Any]]`

Search for similar vectors.

---

## Reflexes Module

### ReflexEngine Class

Core automation engine for RIN.

```python
from rin.reflexes import ReflexEngine

engine = ReflexEngine(config=None)
```

#### Methods

##### `register_action(name: str, handler: Callable, description: str = "") -> None`

Register a new action.

**Parameters:**
- `name` (str): Action name
- `handler` (callable): Function to execute
- `description` (str): Action description

**Example:**
```python
def custom_action(param):
    return f"Result: {param}"

engine.register_action("custom", custom_action, "My custom action")
```

##### `execute_action(action_name: str, **kwargs) -> Dict[str, Any]`

Execute a registered action.

**Parameters:**
- `action_name` (str): Name of action to execute
- `**kwargs`: Parameters for the action

**Returns:**
- dict: Execution results

##### `create_workflow(name: str, action_names: List[str], description: str = "") -> Workflow`

Create a new workflow.

**Parameters:**
- `name` (str): Workflow name
- `action_names` (list): List of action names
- `description` (str): Workflow description

**Returns:**
- Workflow: Created workflow

##### `execute_workflow(workflow_name: str, **kwargs) -> Dict[str, Any]`

Execute a registered workflow.

##### `get_available_actions() -> List[str]`

Get list of registered actions.

##### `get_available_workflows() -> List[str]`

Get list of registered workflows.

---

### Action Class

Represents a single executable action.

```python
from rin.reflexes import Action

action = Action(name, handler, description="")
```

---

### Workflow Class

Represents a sequence of actions to execute.

```python
from rin.reflexes import Workflow

workflow = Workflow(name, description="")
```

#### Methods

##### `add_action(action: Action) -> None`

Add an action to the workflow.

##### `execute(**kwargs) -> Dict[str, Any]`

Execute all actions in the workflow.

---

## Utilities

### Setup Logging

```python
from rin.utils import setup_logging

setup_logging(level="INFO")
```

### Load Configuration

```python
from rin.utils import load_config

config = load_config("config/config.yaml")
```

### Save Configuration

```python
from rin.utils import save_config

save_config(config, "config/config.yaml")
```

---

## Constants and Enums

### ActionStatus

```python
from rin.reflexes import ActionStatus

ActionStatus.PENDING
ActionStatus.RUNNING
ActionStatus.COMPLETED
ActionStatus.FAILED
ActionStatus.CANCELLED
```

---

## Version Information

```python
import rin

print(rin.__version__)  # "1.2.0"
```

---

For more examples, see the [examples/](../examples/) directory.
