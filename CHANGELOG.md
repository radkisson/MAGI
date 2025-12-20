# Changelog

All notable changes to the Rhyzomic Intelligence Node (RIN) will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.0] - 2025-12-20

### Added
- **Core Agent System**: Main agent orchestration with observe-think-act cycle
- **Sensors Module**: Real-time browsing and perception capabilities
  - WebBrowser sensor for web content extraction
  - APIConnector sensor for external API integration
  - SensorManager for sensor orchestration
- **Memory Module**: Vectorized recall and knowledge storage
  - MemoryStore for simple key-value storage
  - VectorMemory for semantic search capabilities
  - MemoryManager for unified memory interface
- **Reflexes Module**: Automation and action execution
  - Action execution framework
  - Workflow system for chaining actions
  - ReflexEngine for reflex orchestration
- **Project Structure**: Complete Python package structure
  - Organized source code in `src/rin/`
  - Comprehensive test suite (37 tests)
  - Configuration system (YAML and environment variables)
- **Documentation**:
  - Comprehensive README.md
  - Detailed DESIGN.md architecture document
  - Getting Started guide
  - Examples and usage documentation
  - Contributing guidelines
- **Deployment**:
  - Docker support with Dockerfile
  - setup.py for pip installation
  - requirements.txt for dependencies
- **Testing**: Full test coverage for all core modules
- **Examples**: Working example scripts demonstrating all features

### Classification
- Version: 1.2.0 (Stable)
- Status: Active Development
- Classification: Sovereign AI Infrastructure
- Architect: CTO (Acting)

### Technical Details
- Python 3.9+ support
- Modular architecture with clear separation of concerns
- Extensible plugin system for sensors, memory, and reflexes
- Configuration via environment variables and YAML
- Logging throughout the system
- Docker containerization support

## [1.1.0] - 2025-12-20

### Added - "Expansion": Enhanced Model Support

#### OpenRouter Integration
- **Full Model Marketplace Access**: Support for 20+ models from multiple providers
- **OpenAI Models via OpenRouter**: gpt-4o, gpt-4-turbo
- **Anthropic Models via OpenRouter**: claude-3-5-sonnet, claude-3-opus
- **Meta Llama Models**: llama-3.1-405b, llama-3.1-70b
- **Google Models**: gemini-pro-1.5, gemini-flash-1.5
- **Mistral Models**: mistral-large, mixtral-8x7b
- **Other Providers**: Cohere Command R+, Perplexity with web search
- **Single API Key**: Access all models through unified OpenRouter API

#### Advanced LiteLLM Configuration
- **Temperature Control**: Fine-tune response randomness (0.0-2.0)
- **Top P Sampling**: Control diversity via nucleus sampling (0.0-1.0)
- **Max Tokens**: Configure maximum response length per model
- **Model-Specific Presets**: Different configurations for different use cases
- **Default Parameters**: System-wide defaults for consistent behavior

#### Model Selection UI
- **Open WebUI Integration**: All models appear in model selector dropdown
- **Automatic Model Discovery**: Models auto-register with Open WebUI
- **Model Metadata**: Display capabilities (vision, function calling, etc.)
- **Direct API + OpenRouter**: Choose between direct API or OpenRouter for same model
- **Real-time Switching**: Change models mid-conversation

#### Per-Model Cost Tracking and Budgeting
- **SQLite Database**: Persistent cost tracking at `data/litellm/litellm_cost_tracking.db`
- **Real-time Monitoring**: Track spending as requests are made
- **Per-Model Pricing**: Accurate cost calculation for each model
- **Budget Limits**: Set monthly spending caps (default: $100/month)
- **Cost Alerts**: Warnings at 80% budget threshold
- **Usage Analytics**: Query historical spending by model, date, user
- **Token Tracking**: Monitor input/output tokens separately

#### Fallback Model Chains for Reliability
- **Automatic Failover**: Seamlessly switch to backup models on failure
- **Multi-Provider Redundancy**: Primary and backup from different providers
- **Smart Routing**: Usage-based load balancing across available models
- **Retry Logic**: Configurable retry attempts with exponential backoff
- **Cooldown Periods**: Temporary removal of failing models (60s default)
- **Timeout Protection**: 60-second request timeout with fallback
- **Pre-configured Chains**:
  - GPT-4o → OpenRouter GPT-4o → Claude 3.5 → Llama 3.1 405B
  - Claude 3.5 → OpenRouter Claude 3.5 → GPT-4o → GPT-4 Turbo
  - Mini models → Haiku → Gemini Flash → Mixtral 8x7B

#### Infrastructure Enhancements
- **LiteLLM Database Volume**: Persistent storage for cost tracking
- **Redis Cache Integration**: Reduced costs through response caching
- **Docker Compose Updates**: New volume mounts for database persistence
- **start.sh Enhancement**: Auto-create litellm data directory with permissions

### Documentation
- **Model Configuration Guide**: Complete guide at `docs/MODEL_CONFIGURATION.md`
- **Configuration Examples**: Cost optimization, reliability, specialized models
- **Troubleshooting Guide**: Common issues and solutions
- **Best Practices**: Recommendations for production use

### Changed
- **LiteLLM Router Strategy**: Upgraded to `usage-based-routing-v2`
- **Config File Format**: Enhanced with model_info and cost tracking
- **Environment Variables**: Added `OPENROUTER_API_KEY` to `.env.example`

### Technical Details
- LiteLLM main-latest with full routing capabilities
- SQLite 3 for cost tracking database
- Redis cache for response optimization
- Fallback chain engine with retry logic
- Real-time model health monitoring

## [1.0.0] - Initial Concept

### Added
- Initial project concept and philosophy
- Basic repository structure
- License and initial README

---

## Version Naming Convention

- **Major version (X.0.0)**: Breaking changes, major architecture changes
- **Minor version (0.X.0)**: New features, backward compatible
- **Patch version (0.0.X)**: Bug fixes, minor improvements

## Release Philosophy

RIN follows a philosophy of:
- **Stability**: Releases are well-tested
- **Sovereignty**: Independence from centralized control
- **Transparency**: Clear documentation of all changes
- **Community**: Open to contributions and feedback
