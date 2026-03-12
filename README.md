# Shrinking Algorithm MCP Server

> **Disclaimer:** This setup assumes you are using **Claude Desktop** as your MCP client.

This MCP server exposes a single tool — `shrink_diagram_by_kruskal` — that accepts the text content of a PlantUML (`.puml`) file and returns a shrunken version of the diagram using Kruskal's algorithm. The intended workflow is:

1. Paste your `.puml` file content into Claude Desktop
2. Claude calls `shrink_diagram_by_kruskal` with the content
3. The MCP server processes it and returns the shrunken diagram
4. Claude presents the result back to you

---

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running
- [Claude Desktop](https://claude.ai/download) installed

---

## Step 1 — Build the Docker Image

> ⚠️ The build command **must be run from the repository root**, not from inside `mcp_server/`.

**macOS / Linux:**
```bash
docker build -f mcp_server/Dockerfile -t shrinking-algorithm-mcp .
```

**Windows (Command Prompt):**
```cmd
docker build -f mcp_server\Dockerfile -t shrinking-algorithm-mcp .
```

**Windows (PowerShell):**
```powershell
docker build -f mcp_server\Dockerfile -t shrinking-algorithm-mcp .
```

To verify the image was built successfully:
```bash
docker images | grep shrinking-algorithm-mcp
```

---

## Step 2 — Create the Docker MCP Catalog

### 2a — Create the catalog YAML file

Create the following file at `~/.docker/mcp/catalogs/shrinking-algorithm.yaml`:

**macOS / Linux:**
```bash
mkdir -p ~/.docker/mcp/catalogs
```

Then create the file `~/.docker/mcp/catalogs/shrinking-algorithm.yaml` with this content:

```yaml
tools:
  shrinking-algorithm:
    image: shrinking-algorithm-mcp:latest
    description: Shrinks PlantUML diagrams using Kruskal's algorithm.
```

**Windows** — create the file at `%USERPROFILE%\.docker\mcp\catalogs\shrinking-algorithm.yaml` with the same content.

### 2b — Register the catalog in the Docker MCP registry

Open (or create) `~/.docker/mcp/registry.yaml` and add the following entry under the top-level `servers` key:

```yaml
servers:
  shrinking-algorithm:
    ref: ""
```

If the file already has other entries, just append the `shrinking-algorithm` block under `servers`.

**Windows** — the file is at `%USERPROFILE%\.docker\mcp\registry.yaml`.

---

## Step 3 — Configure Claude Desktop

Locate your Claude Desktop config file:

| Platform | Path |
|----------|------|
| macOS | `~/Library/Application Support/Claude/claude_desktop_config.json` |
| Windows | `%APPDATA%\Claude\claude_desktop_config.json` |
| Linux | `~/.config/Claude/claude_desktop_config.json` |

The contents of `/mcp_server/claude_desktop_config.json` in this repository show the server entry you need. Open your Claude Desktop config and merge in the `shrinking-algorithm` block under `mcpServers`:

```json
{
  "mcpServers": {
    "shrinking-algorithm": {
      "command": "docker",
      "args": [
        "run",
        "--rm",
        "-i",
        "shrinking-algorithm-mcp"
      ]
    }
  }
}
```

If you already have other servers in `mcpServers`, just add the `shrinking-algorithm` entry alongside them.

---

## Step 4 — Restart Claude Desktop

Fully quit and reopen Claude Desktop:

- **macOS:** `Cmd+Q`, then reopen
- **Windows / Linux:** Close from the system tray, then reopen

After restarting, click the 🔧 tools icon in the chat input area — you should see `shrink_diagram_by_kruskal` listed.

---

## Usage

Paste the contents of a `.puml` file into the chat and prompt Claude:

> *"Use the shrink_diagram_by_kruskal tool on this diagram."*

Claude will extract the text, call the tool, and return the shrunken diagram directly in the conversation.

---

## Troubleshooting

**Tool not appearing in Claude Desktop:**
- Make sure Docker Desktop is running
- Verify the image exists: `docker images | grep shrinking-algorithm-mcp`
- Check for JSON syntax errors in `claude_desktop_config.json`

**Checking live logs:**
```bash
# macOS / Linux
tail -f ~/Library/Logs/Claude/mcp-server-shrinking-algorithm.log
```

**Testing the container directly:**
```bash
docker run --rm -i shrinking-algorithm-mcp
```