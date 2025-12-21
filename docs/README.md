# RIN Documentation

Welcome to the Rhyzomic Intelligence Node (RIN) documentation hub. This directory contains comprehensive guides for all features.

## 📚 Documentation Index

### Getting Started
- **[GETTING_STARTED.md](GETTING_STARTED.md)** - Initial setup and first steps with RIN
- **[../CLI_REFERENCE.md](../CLI_REFERENCE.md)** - Complete CLI management tool reference ⭐ **NEW**

### Core Features
- **[API.md](API.md)** - API reference and integration guide

### v1.1 Enhanced Model Support
- **[V1.1_QUICK_REFERENCE.md](V1.1_QUICK_REFERENCE.md)** - Quick reference card for v1.1 features ⭐ **START HERE**
- **[MODEL_CONFIGURATION.md](MODEL_CONFIGURATION.md)** - Complete guide to model configuration
- **[V1.1_SMOKE_TESTS.md](V1.1_SMOKE_TESTS.md)** - Smoke tests to verify v1.1 deployment

### Architecture & Design
- **[../DESIGN.md](../DESIGN.md)** - System architecture and design philosophy
- **[../README.md](../README.md)** - Main project documentation

### Development
- **[../CHANGELOG.md](../CHANGELOG.md)** - Version history and release notes
- **[../CONTRIBUTING.md](../CONTRIBUTING.md)** - Contribution guidelines

## 🚀 Quick Links by Use Case

### "I want to get started quickly"
1. [GETTING_STARTED.md](GETTING_STARTED.md)
2. [../CLI_REFERENCE.md](../CLI_REFERENCE.md)
3. [V1.1_QUICK_REFERENCE.md](V1.1_QUICK_REFERENCE.md)

### "I want to configure models"
1. [V1.1_QUICK_REFERENCE.md](V1.1_QUICK_REFERENCE.md)
2. [MODEL_CONFIGURATION.md](MODEL_CONFIGURATION.md)

### "I want to test my deployment"
1. [V1.1_SMOKE_TESTS.md](V1.1_SMOKE_TESTS.md)

### "I want to understand the architecture"
1. [../DESIGN.md](../DESIGN.md)
2. [../README.md](../README.md)

### "I want to integrate with APIs"
1. [API.md](API.md)

### "I want to contribute"
1. [../CONTRIBUTING.md](../CONTRIBUTING.md)
2. [../CHANGELOG.md](../CHANGELOG.md)

## 📖 Documentation by Feature

### Model Management
| Feature | Quick Reference | Detailed Guide | Testing |
|---------|----------------|----------------|---------|
| OpenRouter Integration | [Quick Ref](V1.1_QUICK_REFERENCE.md#1-openrouter-integration) | [Full Guide](MODEL_CONFIGURATION.md#openrouter-integration) | [Smoke Tests](V1.1_SMOKE_TESTS.md#test-4-openrouter-integration) |
| Model Parameters | [Quick Ref](V1.1_QUICK_REFERENCE.md#2-advanced-model-parameters) | [Full Guide](MODEL_CONFIGURATION.md#advanced-model-parameters) | [Smoke Tests](V1.1_SMOKE_TESTS.md#test-5-advanced-model-parameters) |
| Cost Tracking | [Quick Ref](V1.1_QUICK_REFERENCE.md#4-cost-tracking--budgeting) | [Full Guide](MODEL_CONFIGURATION.md#cost-tracking-and-budgeting) | [Smoke Tests](V1.1_SMOKE_TESTS.md#test-3-cost-tracking-database) |
| Fallback Chains | [Quick Ref](V1.1_QUICK_REFERENCE.md#5-fallback-chains) | [Full Guide](MODEL_CONFIGURATION.md#fallback-model-chains) | [Smoke Tests](V1.1_SMOKE_TESTS.md#test-6-fallback-chain-advanced) |

### System Components
| Component | Documentation | Configuration |
|-----------|---------------|---------------|
| Open WebUI (Cortex) | [DESIGN.md](../DESIGN.md#a-the-cortex-cognition) | `docker-compose.yml` |
| LiteLLM (Router) | [MODEL_CONFIGURATION.md](MODEL_CONFIGURATION.md) | `config/litellm/config.yaml` |
| SearXNG (Vision) | [DESIGN.md](../DESIGN.md#b-the-sensorium-perception) | `config/searxng/` |
| Qdrant (Memory) | [DESIGN.md](../DESIGN.md#c-the-memory-recall) | `docker-compose.yml` |
| Redis (Nervous System) | [DESIGN.md](../DESIGN.md#d-the-nervous-system-reflex) | `docker-compose.yml` |
| n8n (Reflex Arc) | [README.md](../README.md#autonomous-workflows-n8n) | `workflows/` |

## 🆕 What's New in v1.1

The v1.1 "Expansion" release introduces major enhancements to model support:

### Features
- ✅ **OpenRouter Integration** - Access 20+ models through unified API
- ✅ **Advanced Parameters** - Fine-tune temperature, top_p, max_tokens
- ✅ **Cost Tracking** - Monitor spending with SQLite database
- ✅ **Fallback Chains** - Automatic failover for 99.9% reliability
- ✅ **Model Selection UI** - All models in Open WebUI dropdown

### Documentation
- 📄 New: [V1.1_QUICK_REFERENCE.md](V1.1_QUICK_REFERENCE.md)
- 📄 New: [MODEL_CONFIGURATION.md](MODEL_CONFIGURATION.md)
- 📄 New: [V1.1_SMOKE_TESTS.md](V1.1_SMOKE_TESTS.md)
- 🔄 Updated: [README.md](../README.md) - Marked v1.1 as complete
- 🔄 Updated: [CHANGELOG.md](../CHANGELOG.md) - Full v1.1 details

### Learn More
- [v1.1 Release Notes](../CHANGELOG.md#110---2025-12-20)
- [v1.1 Quick Reference](V1.1_QUICK_REFERENCE.md)

## 📋 Common Tasks

### Configuration Tasks
```bash
# Start RIN
./rin start

# Stop RIN
./rin stop

# Check system status
./rin status

# View logs
./rin logs

# View current model configuration
cat config/litellm/config.yaml

# Edit model parameters
nano config/litellm/config.yaml

# Restart to apply changes
./rin restart
```

### Monitoring Tasks
```bash
# Check cost tracking database
sqlite3 data/litellm/litellm_cost_tracking.db

# View all models
curl http://localhost:4000/models

# Check LiteLLM health
curl http://localhost:4000/health
```

### Troubleshooting Tasks
```bash
# View LiteLLM logs
./rin logs litellm

# View all logs with follow
./rin logs -f

# Restart all services
./rin restart

# Check service status
./rin status

# Or use docker-compose directly
docker-compose ps
```

## 🔗 External Resources

### LiteLLM
- [Official Documentation](https://docs.litellm.ai/)
- [Supported Models](https://docs.litellm.ai/docs/providers)
- [Configuration Guide](https://docs.litellm.ai/docs/proxy/configs)

### OpenRouter
- [Model Marketplace](https://openrouter.ai/models)
- [API Documentation](https://openrouter.ai/docs)
- [Pricing](https://openrouter.ai/models)

### Open WebUI
- [Official Docs](https://docs.openwebui.com/)
- [GitHub Repository](https://github.com/open-webui/open-webui)

### Model Providers
- [OpenAI Platform](https://platform.openai.com/)
- [Anthropic Console](https://console.anthropic.com/)
- [Google AI Studio](https://makersuite.google.com/)

## 💬 Support & Community

- **Issues**: [GitHub Issues](https://github.com/radkisson/Rhyzomic-Intelligence-Node-RIN-/issues)
- **Discussions**: [GitHub Discussions](https://github.com/radkisson/Rhyzomic-Intelligence-Node-RIN-/discussions)
- **Contributing**: [CONTRIBUTING.md](../CONTRIBUTING.md)

## 📝 Contributing to Docs

Found an error or want to improve the documentation?

1. Fork the repository
2. Edit the relevant `.md` file
3. Submit a pull request
4. Follow the [contribution guidelines](../CONTRIBUTING.md)

### Documentation Standards
- Use clear, concise language
- Include code examples where helpful
- Test all commands before documenting
- Keep formatting consistent
- Update the index when adding new docs

---

**RIN Documentation** - Everything you need to master your sovereign AI infrastructure. 🧠📚
