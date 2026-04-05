# MCP Inspector (npx) — stdio servers

This assignment uses **stdio** MCP servers (spawned by Python subprocesses). To debug tool discovery and tool calls, use the official inspector package:

## Requirements

- Node.js version `^22.7.5` (you have `v23.x`, so it’s OK)
- Activate your Python venv (so `python` points at your installed dependencies)

## Start inspector for the PPT writer server

From the `ASSIGNMENT` folder:

```powershell
npx --yes @modelcontextprotocol/inspector --transport stdio -- python ppt_mcp_server.py
```

If you want to force the venv python:

```powershell
npx --yes @modelcontextprotocol/inspector --transport stdio -- .\.venv\Scripts\python.exe ppt_mcp_server.py
```

Open the UI at `http://localhost:6274`.

## Start inspector for the research server

```powershell
npx --yes @modelcontextprotocol/inspector --transport stdio -- python research_mcp_server.py
```

## Optional: Cursor / Claude Desktop `mcp.json` example

Create `mcp.json` (name may vary by your app) and paste this. **Edit the absolute paths**:

```json
{
  "mcpServers": {
    "auto-ppt-writer": {
      "command": "python",
      "args": [
        "C:/Users/yourname/Desktop/CAlibo noww/ASSIGNMENT/ppt_mcp_server.py"
      ],
      "env": {}
    },
    "auto-ppt-research": {
      "command": "python",
      "args": [
        "C:/Users/yourname/Desktop/CAlibo noww/ASSIGNMENT/research_mcp_server.py"
      ],
      "env": {}
    }
  }
}
```

