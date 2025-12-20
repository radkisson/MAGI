# Project Design Document: Rhyzomic Intelligence Node (RIN)

**Version**: 1.2.0 (Stable)  
**Status**: Active Development  
**Classification**: Sovereign AI Infrastructure  
**Architect**: CTO (Acting)

## Overview

Rhyzomic Intelligence Node (RIN) is an autonomous, self-hosted AI agent system designed to operate independently of centralized commercial control. It is not merely a chatbot, but a sovereign organism equipped with:

- **The Cortex** (cognition)
- **The Sensorium** (perception)
- **The Memory** (recall)
- **The Nervous System** (reflex)

## Philosophy

Commercial AI models (ChatGPT, Claude) are "Brains in a Jar"—intelligent but disconnected, censored, and reliant on their creators for input. RIN is a sovereign, self-hosted entity. It treats commercial APIs merely as "compute," while retaining its own memory, eyes, and agency on your infrastructure.

## System Architecture

The RIN is composed of five biological subsystems that function as a single organism via Docker orchestration.

### A. The Cortex (Cognition)

The brain of RIN, responsible for reasoning and human interaction.

**Components:**

- **Open WebUI**: The unified interface for human-agent interaction. It manages chat history, user authentication, and tool invocation. This is the primary interface where users interact with RIN.

- **LiteLLM (The Router)**: An API Gateway that sits between the Cortex and the Models. It allows RIN to route "thoughts" to the most appropriate provider (e.g., GPT-4o for logic, Claude 3.5 for coding, local Llama 3 for privacy) without changing the frontend code. This provides flexibility and independence from any single AI provider.

**Key Functions:**
- Human-agent interaction and conversation management
- Intelligent routing to appropriate LLM providers
- Multi-model orchestration
- User authentication and session management
- Tool invocation and coordination

### B. The Sensorium (Perception)

The sensory organs of RIN, enabling it to perceive and gather information from the external world.

**Components:**

- **SearXNG (Vision)**: A privacy-respecting metasearch engine. It aggregates results from Google/Bing without passing your IP or tracking data to them, allowing RIN to "see" the web anonymously. This provides sovereign web search capabilities without sacrificing privacy.

- **FireCrawl (Digestion)**: A specialized scraping array that uses headless browsers to navigate complex JavaScript-heavy sites (like dynamic dashboards) and converts them into clean Markdown. This "nutrient" format is optimized for LLM consumption.

**Key Functions:**
- Privacy-preserving web search
- Complex web page scraping and extraction
- Content transformation to LLM-friendly formats
- JavaScript-rendered content handling
- Anonymous information gathering

### C. The Memory (Recall)

The knowledge storage and retrieval system, enabling RIN to remember and learn from past interactions.

**Components:**

- **Qdrant**: A Vector Database that stores the semantic meaning of every interaction and scraped document. This enables RAG (Retrieval Augmented Generation), allowing RIN to recall facts from months ago rather than hallucinating. Qdrant provides fast, scalable vector similarity search.

**Key Functions:**
- Semantic storage of conversations and documents
- Vector similarity search
- RAG (Retrieval Augmented Generation)
- Long-term memory across sessions
- Context preservation and recall
- Knowledge graph construction

### D. The Nervous System (Reflex)

The coordination and messaging system that enables asynchronous task execution and inter-component communication.

**Components:**

- **Redis**: The high-speed message bus that coordinates the Sensorium's asynchronous tasks (e.g., queuing a scrape job for FireCrawl). Redis provides fast, reliable inter-process communication and task queuing.

**Key Functions:**
- Asynchronous task queuing
- Inter-component messaging
- Job coordination and scheduling
- Caching for performance
- Real-time event coordination

## Technical Stack

### Core Technologies:
- **Cortex**: Open WebUI + LiteLLM (API routing)
- **Sensorium**: SearXNG (metasearch) + FireCrawl (web scraping)
- **Memory**: Qdrant (vector database)
- **Nervous System**: Redis (message bus)
- **Orchestration**: Docker Compose
- **Language**: Python 3.9+ for custom integrations
- **LLM Providers**: GPT-4o, Claude 3.5, Llama 3 (configurable via LiteLLM)

## Deployment Model

### Docker Orchestration:
All five subsystems run as separate Docker containers, orchestrated via Docker Compose:

```yaml
services:
  - open-webui (Cortex)
  - litellm (Cortex Router)
  - searxng (Sensorium)
  - firecrawl (Sensorium)
  - qdrant (Memory)
  - redis (Nervous System)
```

### Self-Hosted Infrastructure:
1. **Local Deployment**: Run on personal hardware with Docker
2. **Private Cloud**: Deploy on VPS or private cloud
3. **Network Isolation**: Components communicate via Docker network
4. **API Gateway**: LiteLLM provides unified API interface

### Security Considerations:
- API key management via environment variables
- Network isolation between components
- Privacy-preserving search via SearXNG
- Data encryption at rest (Qdrant)
- No external data leakage
- User authentication in Open WebUI

## Development Roadmap

### Phase 1: Foundation (v1.0) - Complete
- [x] Project structure
- [x] Architecture design
- [x] Basic Python framework

### Phase 2: The Cortex (v1.1)
- [ ] Open WebUI integration
- [ ] LiteLLM deployment and configuration
- [ ] Multi-model routing setup
- [ ] User authentication

### Phase 3: The Sensorium (v1.2) - Current
- [ ] SearXNG deployment
- [ ] FireCrawl integration
- [ ] Web scraping pipeline
- [ ] Content extraction to Markdown

### Phase 4: The Memory (v1.3)
- [ ] Qdrant vector database setup
- [ ] Embedding generation pipeline
- [ ] RAG implementation
- [ ] Conversation history storage

### Phase 5: The Nervous System (v1.4)
- [ ] Redis message bus deployment
- [ ] Asynchronous task queuing
- [ ] Inter-component communication
- [ ] Job scheduling and coordination

### Phase 6: Integration (v2.0)
- [ ] Full system integration via Docker Compose
- [ ] End-to-end workflows
- [ ] Performance optimization
- [ ] Production hardening

## Data Flow

### Typical Interaction Flow:

1. **User Input** → Open WebUI (Cortex)
2. **Query Analysis** → LiteLLM routes to appropriate model
3. **Information Gathering** → SearXNG searches web anonymously
4. **Content Extraction** → FireCrawl scrapes and formats pages
5. **Memory Retrieval** → Qdrant provides relevant context via RAG
6. **Response Generation** → LLM synthesizes answer with context
7. **Memory Storage** → Conversation stored in Qdrant for future recall
8. **Async Tasks** → Redis coordinates background scraping/processing

### Communication Patterns:

- **Synchronous**: User ↔ Open WebUI ↔ LiteLLM ↔ LLM Providers
- **Asynchronous**: FireCrawl jobs queued via Redis
- **Storage**: All interactions → Qdrant for semantic search
- **Search**: Open WebUI → SearXNG for privacy-preserving queries

## Usage Philosophy

RIN is designed as a **biological organism**:
- **Sovereign**: You control the entire organism and its data
- **Organic**: Components work together like biological systems
- **Transparent**: Open architecture with clear data flows
- **Private**: All "sensory" input is anonymized (SearXNG)
- **Flexible**: Adaptable cognition via multi-model routing (LiteLLM)
- **Persistent**: Long-term memory via vector storage (Qdrant)
- **Coordinated**: Asynchronous reflexes via message bus (Redis)

## Component Integration

### Docker Compose Architecture:

```yaml
networks:
  rin-network:
    driver: bridge

volumes:
  qdrant-storage:
  redis-data:
  searxng-config:

services:
  open-webui:
    image: ghcr.io/open-webui/open-webui
    depends_on: [litellm]
    
  litellm:
    image: ghcr.io/berriai/litellm
    environment:
      - OPENAI_API_KEY
      - ANTHROPIC_API_KEY
    
  searxng:
    image: searxng/searxng
    
  firecrawl:
    image: mendableai/firecrawl
    
  qdrant:
    image: qdrant/qdrant
    volumes: [qdrant-storage:/qdrant/storage]
    
  redis:
    image: redis:alpine
    volumes: [redis-data:/data]
```

## Contributing

This is an open-source project. Contributions are welcome in:
- Component integration and orchestration
- Docker Compose configurations
- Custom tools and plugins for Open WebUI
- LiteLLM routing strategies
- Qdrant schema optimization
- Documentation and examples
- Testing and validation

## License

See LICENSE file for details.
