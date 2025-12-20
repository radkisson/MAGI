# v1.1 Deployment Verification Checklist

Use this checklist to verify that v1.1 Enhanced Model Support is correctly deployed and working.

## Pre-Deployment Verification

- [ ] **Configuration Tests Pass**
  ```bash
  python3 tests/test_model_config.py
  ```
  Expected: 7/7 tests pass ✅

- [ ] **Git Status Clean**
  ```bash
  git status
  ```
  Expected: "nothing to commit, working tree clean"

- [ ] **Changes Committed**
  ```bash
  git log --oneline -5
  ```
  Expected: See v1.1 implementation commits

## Deployment Steps

### 1. Update Repository
```bash
# Pull latest changes
git pull origin copilot/add-enhanced-model-support

# Verify you're on the right branch
git branch --show-current
```

### 2. Configure API Keys
```bash
# Edit .env file
nano .env

# Add at least one API key:
# OPENAI_API_KEY=sk-...
# ANTHROPIC_API_KEY=sk-ant-...
# OPENROUTER_API_KEY=sk-or-...

# Verify keys are set (without showing values)
grep "API_KEY=" .env | wc -l
```
Expected: At least 3 keys defined (internal + at least 1 external)

### 3. Run Startup Script
```bash
# Make start.sh executable (if needed)
chmod +x start.sh

# Run startup
./start.sh

# Wait for services to start (30-60 seconds)
sleep 60
```

### 4. Verify Services
```bash
# Check all services are running
docker-compose ps

# Verify LiteLLM is healthy
docker-compose ps | grep rin-router | grep "Up"

# Check LiteLLM logs for errors
docker-compose logs litellm | tail -20
```
Expected: All services "Up" and healthy

## Post-Deployment Verification

### ✅ Test 1: LiteLLM Health Check
```bash
curl -s http://localhost:4000/health | jq
```
Expected: `{"status": "healthy"}` or similar

### ✅ Test 2: Model Discovery
```bash
curl -s http://localhost:4000/models | jq '.data | length'
```
Expected: 16 (or number of configured models)

### ✅ Test 3: Model List
```bash
curl -s http://localhost:4000/models | jq '.data[].id' | head -10
```
Expected: See model IDs like "gpt-4o", "claude-3-5-sonnet", "openrouter/llama-3.1-70b"

### ✅ Test 4: Cost Tracking Database
```bash
# Wait for first request to create database
sleep 10

# Check database was created
ls -lh data/litellm/litellm_cost_tracking.db

# Connect to database
sqlite3 data/litellm/litellm_cost_tracking.db ".tables"
```
Expected: Database file exists, tables created (spend_log, etc.)

### ✅ Test 5: Open WebUI Access
```bash
# Check Open WebUI is accessible
curl -s http://localhost:3000 | head -1
```
Expected: HTML content

Manual: Open http://localhost:3000 in browser
- [ ] Page loads successfully
- [ ] Can create/login to account
- [ ] Model selector dropdown appears
- [ ] See all configured models in dropdown

### ✅ Test 6: Send Test Message
Manual in Open WebUI (http://localhost:3000):
1. Select "gpt-4o-mini" (or any available model)
2. Send message: "Hello, what model are you?"
3. Wait for response

Expected:
- [ ] Response received within 10 seconds
- [ ] Model identifies itself correctly
- [ ] No errors in UI

### ✅ Test 7: Verify Cost Tracking
```bash
# Wait a few seconds after sending message
sleep 5

# Check cost was recorded
sqlite3 data/litellm/litellm_cost_tracking.db \
  "SELECT COUNT(*) FROM spend_log;"
```
Expected: At least 1 request logged

### ✅ Test 8: Verify Different Model
Manual in Open WebUI:
1. Switch to "claude-3-5-haiku" (or another model)
2. Send same message
3. Verify different response

Expected:
- [ ] Can switch models
- [ ] Different model responds
- [ ] Both requests tracked in database

### ✅ Test 9: Check Logs
```bash
# Check for errors in LiteLLM logs
docker-compose logs litellm | grep -i "error" | tail -10

# Check for successful requests
docker-compose logs litellm | grep -i "POST /chat" | tail -5
```
Expected: No critical errors, successful POST requests visible

### ✅ Test 10: Configuration Verification
```bash
# Verify config file
cat config/litellm/config.yaml | grep "model_name:" | wc -l

# Verify fallback chains
cat config/litellm/config.yaml | grep -A 3 "fallbacks:"

# Verify cost tracking enabled
cat config/litellm/config.yaml | grep "database_url"
```
Expected:
- 16 models configured
- Fallback chains present
- Database URL configured

## Troubleshooting

### Issue: Services won't start
```bash
# Check Docker daemon
docker ps

# Check compose file
docker-compose config

# View full logs
docker-compose logs
```

### Issue: LiteLLM not healthy
```bash
# Restart LiteLLM
docker-compose restart litellm

# View detailed logs
docker-compose logs -f litellm

# Check config syntax
cat config/litellm/config.yaml | yaml-validator
```

### Issue: Models not appearing
```bash
# Verify API keys
docker-compose exec litellm env | grep API_KEY

# Restart Open WebUI
docker-compose restart open-webui

# Clear browser cache
# Close and reopen browser
```

### Issue: Cost tracking not working
```bash
# Check data directory
ls -la data/litellm/

# Fix permissions
chmod 777 data/litellm/

# Restart LiteLLM
docker-compose restart litellm

# Send test request and check logs
docker-compose logs litellm | grep -i database
```

## Success Criteria

All checks must pass:

- [x] Configuration tests: 7/7 ✅
- [ ] All services running and healthy
- [ ] LiteLLM health check passes
- [ ] 16 models discovered
- [ ] Cost tracking database created
- [ ] Open WebUI accessible
- [ ] Can send messages to multiple models
- [ ] Cost tracking records requests
- [ ] No critical errors in logs
- [ ] Documentation accessible

## Post-Verification

Once all checks pass:

1. **Run Full Smoke Tests**
   ```bash
   # Follow the guide
   cat docs/V1.1_SMOKE_TESTS.md
   ```

2. **Read Documentation**
   - Quick Reference: `docs/V1.1_QUICK_REFERENCE.md`
   - Full Guide: `docs/MODEL_CONFIGURATION.md`
   - Smoke Tests: `docs/V1.1_SMOKE_TESTS.md`

3. **Monitor Costs**
   ```bash
   # Set up daily cost check
   echo "sqlite3 data/litellm/litellm_cost_tracking.db \
     'SELECT ROUND(SUM(cost), 2) as total_cost FROM spend_log;'" \
     > check_costs.sh
   chmod +x check_costs.sh
   ```

4. **Share Feedback**
   - Report issues: GitHub Issues
   - Share use cases: GitHub Discussions
   - Contribute improvements: Pull Requests

## Rollback Plan (If Needed)

If deployment fails critically:

```bash
# Stop all services
docker-compose down

# Checkout previous version
git checkout 8d0bb36  # or previous stable commit

# Restart services
./start.sh
```

## Monitoring Commands

Keep these handy for ongoing monitoring:

```bash
# Quick health check
docker-compose ps && curl -s http://localhost:4000/health

# View costs
sqlite3 data/litellm/litellm_cost_tracking.db \
  "SELECT model, COUNT(*) as requests, ROUND(SUM(cost), 4) as cost 
   FROM spend_log GROUP BY model;"

# Check errors
docker-compose logs litellm | grep -i error | tail -20

# View recent requests
docker-compose logs litellm | grep "POST /chat" | tail -10
```

---

**Deployment Verification Complete!** 🚀✅

Once all checks pass, v1.1 Enhanced Model Support is successfully deployed and ready for use.
