# MCP Tools Guide

## Overview

Model Context Protocol (MCP) is an open standard that enables AI assistants to securely connect to external tools and data sources. RIN includes MCP bridge services that translate MCP tools into OpenAPI format that Open WebUI can understand and use.

## Available MCP Tools

RIN comes with two pre-configured MCP bridges:

1. **Sequential Thinking** - Chain-of-thought reasoning for deeper analysis
2. **YouTube Transcript** - Video subtitle extraction and analysis

## Setup Instructions

### General Connection Process

All MCP tools follow the same connection process in Open WebUI:

1. **Navigate to Tool Servers**
   - Open Open WebUI at http://localhost:3000
   - Go to **Settings** (gear icon)
   - Click **Admin Settings**
   - Select **Tool Servers**

2. **Add the Tool Server**
   - Click the **"+"** button to add a new tool server
   - Enter the OpenAPI URL for the specific tool (see below)
   - Click **Download/Load** (cloud icon)
   - Wait for the tool to be loaded

3. **Activate the Tool**
   - Once loaded, you'll see the tool appear in the list
   - Toggle the switch to **ON** (green)
   - The tool is now available for use in conversations

### Network Hostname Notes

When connecting to MCP tools, try these URLs in order:

1. **First try:** `http://[service-name]:[port]/openapi.json` (Docker network hostname)
2. **If that fails:** `http://host.docker.internal:[port]/openapi.json` (Docker host gateway)
3. **Last resort:** `http://localhost:[port]/openapi.json` (Linux systems)

---

## 1. Sequential Thinking Tool

### Description

The Sequential Thinking tool forces the AI to use a "Chain of Thought" approach, breaking down complex problems into sequential steps. This results in deeper, more methodical reasoning compared to standard single-pass responses.

### How It Works

1. The AI calls the tool with `thoughtNumber: 1` with the first reasoning step
2. The tool acknowledges the thought
3. The AI calls the tool again with `thoughtNumber: 2` with the next step
4. This continues iteratively until the complete thought chain is formed
5. The AI then synthesizes all steps into a comprehensive answer

### Connection URL

```
http://mcp-bridge:9000/openapi.json
```

**Fallback URLs:**
- `http://host.docker.internal:9000/openapi.json`
- `http://localhost:9000/openapi.json`

### Usage Examples

**Complex Analysis:**
```
User: "Use the sequential thinking tool to analyze exactly how we could colonize Mars, step by step."

RIN: [Calls tool with thought 1: "First, we need to solve the transport challenge..."]
     [Calls tool with thought 2: "Next, we need to establish life support systems..."]
     [Calls tool with thought 3: "Then, we need to create sustainable food production..."]
     [Continues until complete]
     [Provides comprehensive, well-reasoned answer]
```

**Problem Solving:**
```
User: "Use sequential thinking to design a secure authentication system."

RIN: [Breaks down the problem into sequential steps]
     [Considers each component methodically]
     [Provides detailed solution with security considerations]
```

### Best Use Cases

- Complex problem solving that requires multi-step reasoning
- Technical architecture design
- Strategic planning and analysis
- Debugging complex issues
- Research synthesis from multiple sources
- Any task where step-by-step thinking improves quality

### Technical Details

- **Service Name:** `rin-mcp-bridge`
- **Image:** `ghcr.io/open-webui/mcpo:main`
- **Port:** 9000 (configurable via `PORT_MCP_BRIDGE`)
- **Package:** `@modelcontextprotocol/server-sequential-thinking` (official)
- **Language:** Node.js (JavaScript)

---

## 2. YouTube Transcript Tool

### Description

The YouTube Transcript tool allows the AI to "watch" videos by extracting and reading their subtitle/caption data. This enables video analysis, summarization, and content search without requiring actual video playback.

### How It Works

1. You provide a YouTube video URL
2. The tool extracts the subtitle/transcript data from YouTube
3. The AI receives the full transcript text
4. The AI can then analyze, summarize, or search the content
5. The tool works with any YouTube video that has captions (automatic or manual)

### Connection URL

```
http://youtube-mcp:9001/openapi.json
```

**Fallback URLs:**
- `http://host.docker.internal:9001/openapi.json`
- `http://localhost:9001/openapi.json`

### Usage Examples

**Video Summarization:**
```
User: "Summarize this video for me: https://www.youtube.com/watch?v=dQw4w9WgXcQ"

RIN: [Retrieves video transcript via YouTube MCP tool]
     [Analyzes the content and structure]
     [Provides comprehensive summary with key points]
```

**Content Search:**
```
User: "Find the exact timestamp in this video where they talk about 'Docker': https://www.youtube.com/watch?v=..."

RIN: [Extracts transcript with timestamps]
     [Searches for the keyword "Docker"]
     [Identifies relevant sections]
     [Provides specific time markers: "At 3:45 and 12:30, they discuss Docker..."]
```

**Multi-Video Analysis:**
```
User: "Compare the arguments made in these three videos about climate change: [URL1], [URL2], [URL3]"

RIN: [Retrieves all three transcripts]
     [Analyzes each perspective]
     [Provides comparative analysis with specific quotes and timestamps]
```

**Lecture Notes:**
```
User: "Create detailed study notes from this lecture: https://www.youtube.com/watch?v=..."

RIN: [Extracts full transcript]
     [Identifies key concepts and explanations]
     [Organizes into structured notes with section headings]
```

### Best Use Cases

- Video summarization and analysis
- Finding specific topics or quotes in long videos
- Creating transcripts for accessibility
- Comparing multiple videos on the same topic
- Extracting actionable information from tutorials
- Creating study notes from educational content
- Analyzing podcast episodes (when published on YouTube)

### Limitations

- Only works with YouTube videos
- Requires that the video has captions (automatic or manual)
- Cannot analyze visual content (only audio/subtitle text)
- Some videos may have caption access restricted by the uploader

### Technical Details

- **Service Name:** `rin-youtube-mcp`
- **Image:** `ghcr.io/open-webui/mcpo:main`
- **Port:** 9001 (configurable via `PORT_YOUTUBE_MCP`)
- **Package:** `@sinco-lab/mcp-youtube-transcript` (NPM)
- **Language:** Node.js (JavaScript)

---

## Troubleshooting

### Tool Server Not Loading

**Problem:** The OpenAPI URL returns an error or times out.

**Solutions:**
1. Verify the service is running: `docker ps | grep mcp`
2. Check service logs: `docker logs rin-mcp-bridge` or `docker logs rin-youtube-mcp`
3. Try alternative URLs (host.docker.internal or localhost)
4. Restart the service: `docker-compose restart mcp-bridge` or `docker-compose restart youtube-mcp`

### Tool Not Appearing After Connection

**Problem:** Tool loads successfully but doesn't appear in conversations.

**Solutions:**
1. Verify the tool is toggled ON (green) in Tool Servers settings
2. Refresh the Open WebUI page
3. Check that the tool has the correct permissions
4. Try disconnecting and reconnecting the tool

### YouTube Tool Returns Errors

**Problem:** YouTube transcript tool fails to extract transcripts.

**Solutions:**
1. Verify the YouTube URL is correct and accessible
2. Check if the video has captions enabled (look for CC button on YouTube)
3. Some videos restrict caption access - try a different video
4. Check service logs for specific error messages: `docker logs rin-youtube-mcp`

### Port Conflicts

**Problem:** Service fails to start due to port already in use.

**Solutions:**
1. Edit `.env` file and change the port:
   - `PORT_MCP_BRIDGE=9000` → `PORT_MCP_BRIDGE=9002`
   - `PORT_YOUTUBE_MCP=9001` → `PORT_YOUTUBE_MCP=9003`
2. Restart services: `./start.sh`
3. Update the OpenAPI URL in Tool Servers to match the new port

---

## Adding More MCP Tools

### Recommended Pattern

All MCP tools should use the `ghcr.io/open-webui/mcpo:main` image for consistency and performance. This image includes Node.js, npm, and mcpo pre-installed, avoiding per-startup installations.

**Basic Template:**

```yaml
services:
  my-mcp-tool:
    image: ghcr.io/open-webui/mcpo:main
    container_name: rin-my-tool
    restart: always
    ports:
      - "${PORT_MY_TOOL:-9002}:${PORT_MY_TOOL:-9002}"
    environment:
      - PORT_MY_TOOL=${PORT_MY_TOOL:-9002}
    command:
      - "--port"
      - "${PORT_MY_TOOL:-9002}"
      - "--"
      - "npx"
      - "-y"
      - "@package-name/mcp-tool-name"
    healthcheck:
      test: ["CMD-SHELL", "wget --no-verbose --tries=1 --spider http://localhost:${PORT_MY_TOOL:-9002}/openapi.json || exit 1"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 30s
```

**Key Configuration Points:**
1. Use environment variables for ports on both sides of the mapping
2. Pass the port variable to the command
3. Include a healthcheck that verifies the OpenAPI endpoint
4. Use the `${VAR:-default}` syntax for default values

### Security Best Practices

When adding new MCP tools, consider these security measures:

1. **Pin Image Versions:** For production, pin the mcpo image to a specific digest instead of using `:main`
   ```yaml
   image: ghcr.io/open-webui/mcpo@sha256:abc123...
   ```

2. **Pin Package Versions:** Instead of using `npx -y @package-name/mcp-tool-name`, pin to specific versions:
   ```yaml
   command:
     - "npx"
     - "-y"
     - "@package-name/mcp-tool-name@1.2.3"
   ```

3. **Network Isolation:** MCP services are only exposed on localhost by default. Keep it that way unless external access is required.

4. **Review Dependencies:** Check the NPM package's dependencies and reputation before deploying.

### Finding MCP Tools

- **Smithery**: https://smithery.ai/ - Directory of MCP tools
- **Model Context Protocol**: https://modelcontextprotocol.io/ - Official documentation
- **NPM Registry**: Search for packages with "mcp" or "model-context-protocol"

---

## Security Considerations

### Network Isolation

MCP bridge services run within the Docker network and are exposed on localhost only by default. They are not accessible from external networks unless you explicitly configure port forwarding.

### API Authentication

Currently, the MCP bridges do not require authentication for internal Docker network access. If you expose these services externally, consider:

1. Adding authentication middleware
2. Using a reverse proxy with authentication (nginx, traefik)
3. Restricting access via firewall rules

### Data Privacy

- **Sequential Thinking**: Processes data entirely within your infrastructure
- **YouTube Transcript**: Fetches public data from YouTube but processes locally
- Neither tool sends your prompts or conversations to external services (only the tool-specific operations)

---

## Performance Optimization

### Resource Usage

**Sequential Thinking:**
- Minimal resources (Node.js process)
- Typical memory: ~50-100MB
- CPU usage: Low (only during tool calls)
- Fast startup time (pre-built image)

**YouTube Transcript:**
- Similar resource profile to Sequential Thinking
- Typical memory: ~50-100MB
- CPU usage: Low (only during tool calls)
- Network bandwidth: Moderate (fetches subtitle data from YouTube)
- Fast startup time (pre-built image)

### Performance Notes

Both MCP services use the `ghcr.io/open-webui/mcpo:main` image, which includes all required dependencies pre-installed. This provides:

1. **Fast startup times** - No package installation on container start
2. **Consistent behavior** - Same runtime environment across deployments
3. **Reduced network usage** - No downloading packages on every restart
4. **Better reliability** - No dependency on external package registries during startup

### Startup Time Optimization

If you're using custom MCP tools or need further optimization:

1. **Pre-pull images**: `docker pull ghcr.io/open-webui/mcpo:main`
2. **Pin image digests** for production to avoid re-pulling on restart
3. **Use volume caching** for NPM packages if using custom tools that aren't in the base image

---

## Further Reading

- [Model Context Protocol Documentation](https://modelcontextprotocol.io/)
- [Open WebUI Tools Documentation](https://docs.openwebui.com/)
- [MCPO Bridge Repository](https://github.com/open-webui/mcpo)
- [Sequential Thinking Tool](https://github.com/modelcontextprotocol/server-sequential-thinking)
- [YouTube Transcript Tool](https://github.com/sinco-lab/mcp-youtube-transcript)

---

## Contributing

Have ideas for new MCP tools? Contributions are welcome!

1. Test the MCP tool locally
2. Add the service definition to `docker-compose.yml`
3. Document the tool in this guide
4. Submit a pull request

See [CONTRIBUTING.md](../CONTRIBUTING.md) for more details.
