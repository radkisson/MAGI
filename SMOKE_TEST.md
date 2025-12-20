# RIN Smoke Test Protocol

This guide provides step-by-step instructions for testing the synaptic connections between the Cortex (Open WebUI) and the organism's subsystems.

## Prerequisites

- All Docker services running: `docker-compose ps`
- Open WebUI accessible at http://localhost:3000
- At least one LLM model configured (OpenAI, Anthropic, or local Ollama)

## Understanding the Data Path

The nervous system no longer relies on public internet APIs; it uses the internal Docker bridge network:

```
User Query
    ↓
Open WebUI (Cortex)
    ↓
Tool Selection (LLM decides)
    ↓
Internal Docker DNS Resolution
    ↓
Service Execution (SearXNG/FireCrawl/Qdrant)
    ↓
Result Processing
    ↓
LLM Synthesis
    ↓
User Response
```

### Example: "What is the latest news on copper mining in Chile?"

1. **The Trigger**: User asks question in Open WebUI
2. **The Neuron**: Open WebUI detects intent and calls `searxng_search.py`
3. **The Synapse**: Script fires request to `http://searxng:8080` (Internal Docker DNS)
4. **The Result**: SearXNG returns JSON
5. **The Decision**: LLM reads results and calls `firecrawl_scraper.py` on top 3 links
6. **The Digestion**: FireCrawl extracts content as Markdown
7. **The Synthesis**: LLM combines all information into final answer

## Step A: Tool Activation

### 1. Verify Tools Are Loaded

1. Open http://localhost:3000 (or your Tailscale IP)
2. Log in if authentication is enabled
3. Navigate to **Workspace → Tools**
4. You should see three tools:
   - `searxng_search` (or `web_search` function)
   - `firecrawl_scraper` (or `scrape_webpage`/`crawl_website` functions)
   - `qdrant_memory` (or `store_memory`/`recall_memory` functions)

**If tools are missing:**
- Click "Refresh" or "Scan" button in Tools section
- Verify Docker volume mount: `docker exec rin-cortex-ui ls /app/backend/data/tools`
- Should show: `searxng_search.py`, `firecrawl_scraper.py`, `qdrant_memory.py`
- Check logs: `docker-compose logs open-webui`

### 2. Bind Tools to Model

**Critical Step**: Tools must be enabled for your model.

1. Navigate to **Workspace → Models**
2. Select your default model (e.g., `gpt-4o`, `claude-3.5-sonnet`, or `llama3`)
3. Look for **"Tools"** or **"Function Calling"** capability setting
4. **Check the boxes** to bind these specific tools to that model:
   - ☑ `web_search` (SearXNG)
   - ☑ `scrape_webpage` (FireCrawl)
   - ☑ `crawl_website` (FireCrawl)
   - ☑ `store_memory` (Qdrant)
   - ☑ `recall_memory` (Qdrant)

**Without this step, the LLM cannot use the tools!**

## Step B: Individual Tool Tests

Test each subsystem independently before running the full loop.

### Test 1: SearXNG (Vision)

**Prompt**: "Search for recent news about artificial intelligence"

**Expected Behavior**:
- ⏳ Status indicator: "🔍 Searching web anonymously via SearXNG..."
- ✅ Status indicator: "✅ Found X results"
- 📄 Response shows search results with titles, URLs, and snippets

**Debugging**:
```bash
# Test SearXNG directly
curl "http://localhost:8080/search?q=test&format=json"

# Check service health
docker-compose logs searxng

# Verify internal DNS
docker exec rin-cortex-ui ping searxng
```

### Test 2: FireCrawl (Digestion)

**Prompt**: "Scrape the content from https://example.com and summarize it"

**Expected Behavior**:
- ⏳ Status indicator: "🔥 Scraping webpage with FireCrawl..."
- ✅ Status indicator: "✅ Content extracted successfully"
- 📄 Response shows clean Markdown content from the page

**Debugging**:
```bash
# Test FireCrawl directly
curl -X POST http://localhost:3002/v0/scrape \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com", "formats": ["markdown"]}'

# Check service health
docker-compose logs firecrawl

# Verify internal DNS
docker exec rin-cortex-ui ping firecrawl
```

### Test 3: Qdrant (Memory)

**Prompt**: "Remember that I prefer Python over JavaScript for backend development"

**Expected Behavior**:
- ⏳ Status indicator: "💾 Storing in long-term memory..."
- ✅ Status indicator: "✅ Memory stored successfully"
- 📄 Response confirms storage with Memory ID

**Then test recall**:

**Prompt**: "What programming language do I prefer for backend?"

**Expected Behavior**:
- ⏳ Status indicator: "🧠 Searching long-term memory..."
- ✅ Status indicator: "✅ Memory search completed"
- 📄 Response retrieves the stored preference

**Debugging**:
```bash
# Check Qdrant collections
curl http://localhost:6333/collections

# Verify collection was created
curl http://localhost:6333/collections/rin_memory

# Check service health
docker-compose logs qdrant

# Verify internal DNS
docker exec rin-cortex-ui ping qdrant
```

## Step C: Integrated "Hunt" Test

This test validates the entire observe-think-act cycle.

### The Full Loop Test

**Prompt**: 
```
Search for the latest press releases from Codelco regarding lithium partnerships. 
Scrape the official announcement if found, summarize the key terms, and store 
this summary in memory under the tag 'Strategy'.
```

### Success Indicators

You should see these status updates in sequence:

1. ⏳ "🔍 Searching web anonymously via SearXNG..."
2. ✅ "✅ Found X results"
3. ⏳ "🔥 Scraping webpage with FireCrawl..." (may happen multiple times)
4. ✅ "✅ Content extracted successfully"
5. ⏳ "💾 Storing in long-term memory..."
6. ✅ "✅ Memory stored successfully"
7. 📄 Final synthesized summary

### What This Validates

- **Vision**: RIN can search the web anonymously
- **Digestion**: RIN can extract content from complex websites
- **Memory**: RIN can store information for future recall
- **Cognition**: LLM orchestrates multiple tools autonomously
- **Anti-fragility**: If one service fails, others continue working

## Step D: Failure Mode Testing

Test that the organism is truly anti-fragile.

### Test Service Independence

1. **Stop FireCrawl**: `docker-compose stop firecrawl`
2. **Test SearXNG**: "Search for AI news" should still work
3. **Restart FireCrawl**: `docker-compose start firecrawl`

4. **Stop SearXNG**: `docker-compose stop searxng`
5. **Test Memory**: "Remember X" should still work
6. **Restart SearXNG**: `docker-compose start searxng`

### Expected Behavior

- Tools should fail gracefully with error messages
- Other tools continue functioning
- Open WebUI (Cortex) remains responsive
- Error messages guide user to fix the issue

## Common Issues and Solutions

### Issue: Tools Not Appearing

**Symptoms**: Tools section is empty in Open WebUI

**Solution**:
1. Verify volume mount: `docker inspect rin-cortex-ui | grep tools`
2. Restart Open WebUI: `docker-compose restart open-webui`
3. Check file permissions: `ls -la tools/`
4. Verify Python syntax: `python3 -m py_compile tools/*.py`

### Issue: "Collection not found" Error

**Symptoms**: Qdrant memory operations fail with collection error

**Solution**:
- This is handled automatically by `_ensure_collection_exists()`
- If it persists, manually create: 
  ```bash
  curl -X PUT http://localhost:6333/collections/rin_memory \
    -H "Content-Type: application/json" \
    -d '{"vectors": {"size": 768, "distance": "Cosine"}}'
  ```

### Issue: Tool Execution Hangs

**Symptoms**: Status spinner never completes

**Solution**:
1. Check service logs: `docker-compose logs [service-name]`
2. Verify service is running: `docker-compose ps`
3. Test service directly (see debugging commands above)
4. Restart the stuck service: `docker-compose restart [service-name]`

### Issue: "Cannot connect to service" Error

**Symptoms**: Connection refused or timeout errors

**Solution**:
1. Verify all services are on same network: `docker network inspect rin-network`
2. Test internal DNS: `docker exec rin-cortex-ui ping [service-name]`
3. Check service health: `docker-compose ps`
4. Restart entire stack: `docker-compose down && docker-compose up -d`

## Success Criteria

✅ All three tools appear in Open WebUI Tools section
✅ Tools are enabled for your selected model
✅ Individual tool tests pass (Search, Scrape, Memory)
✅ Integrated "Hunt" test completes successfully
✅ Status indicators appear and update during execution
✅ Services fail gracefully when stopped
✅ Error messages are clear and actionable

## Next Steps After Smoke Test

Once all tests pass:

1. **Configure LLM routing** in LiteLLM for multi-model intelligence
2. **Customize tool behavior** by editing Python files in `tools/`
3. **Add new tools** following the pattern in `tools/README.md`
4. **Monitor costs** using PostgreSQL LiteLLM observability
5. **Create workflows** combining multiple tools for complex tasks

## Hot-Swappable Updates

The `./tools` directory is mounted directly into the container. To update tools:

1. Edit the Python file on your host machine
2. Restart Open WebUI: `docker-compose restart open-webui`
3. Tools automatically reload with new logic

**No need to rebuild Docker images!**

---

**Remember**: Code in the repository does not mean logic in the brain. The smoke test validates that the synapses are actually firing. 🧠⚡
