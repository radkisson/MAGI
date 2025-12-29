# Changelog

All notable changes to the Rhyzomic Intelligence Node (RIN) will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **Jupyter Lab Integration**: Interactive notebook environment for code execution and data analysis
  - Full scipy stack (NumPy, Pandas, Matplotlib, SciPy) pre-installed
  - OpenRouter API integration via environment variables
  - Direct access to internal LiteLLM router at `http://litellm:4000`
  - pydiode support for AI-assisted code execution (optional)
  - HTTPS support when enabled via SSL certificates
  - Access to all other MAGI services from notebooks
  - Pre-installed example notebook: `Welcome_to_MAGI.ipynb`
  - Default access at `http://localhost:8888` (configurable via `PORT_JUPYTER`)
  - Documentation added to TOOLS.md, CONFIGURATION.md, and ARCHITECTURE.md
  - Jupyter added as "The Laboratory" subsystem in architecture
  - **Security**: Token-based authentication configurable via `JUPYTER_TOKEN` environment variable
  - Default configuration optimized for local development (no authentication)
  - Production-ready security options documented in TOOLS.md

### Fixed
- **LiteLLM Streaming Timeout**: Increased timeout from 60s to 300s to prevent `httpx.TimeoutException` during long streaming responses
  - Updated `router_settings.timeout` to 300 seconds
  - Added `litellm_settings.request_timeout` parameter (300 seconds)
  - Updated documentation to reflect new timeout values

### Planned
- Future enhancements and features will be listed here

## [1.3.0] - 2025-12-26

### Added
- **Python 3.12 Support in n8n**: Full Python support for workflow automation
  - Upgraded n8n to use `hank033/n8n-python:latest` Docker image with Python 3.12.12
  - **Security Note**: Uses community-maintained image; for production with strict security requirements, consider building custom image from official n8n base or pinning to specific version digest
  - Code nodes now support both JavaScript and Python languages
  - Full Python standard library available in workflows
  - Support for installing external packages via pip (pandas, numpy, scikit-learn, etc.)
  - **Note**: Installed packages may not persist across container restarts; see documentation for production strategies
  - New `workflows/PYTHON_EXAMPLES.md` - Comprehensive guide with real-world Python workflow examples
  - Documentation includes data science, API integration, and text analysis examples with security best practices
  - Updated main README.md and workflow documentation to document Python capabilities and security considerations

- **Dynamic OpenRouter Model Loading**: Automatically fetch and sync the latest models from OpenRouter API
  - New `scripts/sync_openrouter_models.py` - Core sync script that fetches models from OpenRouter API
  - New `scripts/sync_models.sh` - Convenience wrapper for manual model syncing
  - New `scripts/search_models.py` - Search and filter models by capabilities, cost, and tags
  - New `docs/DYNAMIC_MODELS.md` - Complete guide for dynamic model loading
  - Automatic model sync on startup via `start.sh`
  - Model filtering to exclude deprecated and unavailable models
  - Automatic capability detection (function calling, vision support)
  - Graceful fallback to static configuration if API is unavailable
  - Config backup before updates
  - Test suite for model sync functionality (9 tests)

- **Model Intelligence Features** (Enhancement implementations):
  - **Popularity Rankings**: Models ranked 0-100 based on provider, pricing, and capabilities
  - **Cost Metadata**: All models tagged with cost tiers (budget/standard/premium) and per-token pricing
  - **Capability Tags**: Searchable tags for providers, capabilities, and specializations
  - **Automatic Recommendations**: Generated recommendations for 6 use cases (best value, coding, vision, etc.)
  - **Model Search Tool**: Command-line tool to search/filter models by any criteria
  - Recommendations saved to `data/model_recommendations.json`

- **RIN CLI Model Management Integration**:
  - `./rin models sync` - Sync latest models from OpenRouter
  - `./rin models list [N] [filter]` - List available models with limit and filter
  - `./rin models top [N]` - Show top N models by popularity
  - `./rin models filter <type> [N]` - Filter models by type (vision, budget, etc.)
  - `./rin models search <query>` - Search models with advanced criteria
  - `./rin models recommend` - Show curated recommendations
  - All model commands integrated into main `rin` CLI tool
  - Support for limiting display (default 50, customizable)
  - Multiple filter types: openrouter, popular, budget, vision, function-calling, provider-specific

- **MCP (Model Context Protocol) Integration**:
  - MCP Bridge service for connecting MCP tools to Open WebUI
  - Sequential Thinking tool for chain-of-thought reasoning
  - YouTube Transcript tool for video analysis
  - OpenAPI translation layer for MCP tools

- **Auto-Registration Tooling**:
  - `scripts/register_tools.py` - Automatic tool registration on startup
  - Tools auto-authenticate using Smart Valves pattern
  - Zero-friction tool configuration via environment variables
  - Pre-authenticated tools appear immediately in Open WebUI

### Changed
- **LiteLLM Configuration**: Now supports dynamic model updates while preserving custom configurations
- **Model Conversion**: Enhanced to include popularity scores, cost metadata, and capability tags
- **README.md**: Updated to mention dynamic model loading feature (100+ models available)
- **docs/MODEL_CONFIGURATION.md**: Added documentation for automatic vs manual model configuration
- **docs/DYNAMIC_MODELS.md**: Updated with implemented enhancement features
- **docs/QUICK_START_MODELS.md**: Added RIN CLI integration examples
- **CLI_REFERENCE.md**: Added comprehensive model management command documentation
- **start.sh**: Integrated automatic model sync on startup with error handling
- **rin CLI**: Enhanced with complete model management subcommands
- **Version**: Updated to 1.3.0 to reflect new dynamic intelligence features

### Fixed
- Model list no longer limited to hardcoded entries in config file
- Users can now access all available OpenRouter models without manual configuration updates
- Model display can be limited to prevent overwhelming output (configurable limit)
- Tool visibility issues resolved with auto-registration
- OpenRouter exception handling improvements

## [1.2.1] - 2025-12-21

### Added
- **Comprehensive CLI Management Tool**: New `./rin` command-line interface for complete lifecycle management
  - `rin start` - Start all RIN services (wraps start.sh)
  - `rin stop` - Gracefully stop all services
  - `rin restart` - Restart all services
  - `rin status` - System health checks and service status
  - `rin logs [service] [-f]` - View and follow logs
  - `rin update` - Pull latest Docker images
  - `rin upgrade` - Upgrade RIN to latest version
  - `rin backup [dir]` - Backup all data and configuration
  - `rin restore <dir>` - Restore from backup
  - `rin ps` - List running containers
  - `rin exec <service> [cmd]` - Execute commands in containers
  - `rin clean` - Remove containers and images
  - `rin version` - Show version information
  - `rin help` - Comprehensive help documentation
- **CLI Documentation**: Complete CLI reference guide (CLI_REFERENCE.md)
- **Backup System**: Automated backup and restore functionality
- **Enhanced Monitoring**: Health checks for all services with status reporting

### Changed
- **README.md**: Updated with CLI management examples and quick start guide
- **docs/README.md**: Added CLI reference to documentation index
- **.gitignore**: Added backups directory to prevent accidental commits

### Fixed
- Improved error handling when services are not running
- Better user feedback with colored output and clear status messages

### Backward Compatibility
- Original `./start.sh` script remains fully functional
- All existing Docker Compose commands still work
- No breaking changes to existing workflows

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
