#!/usr/bin/env python3
"""
Debug MCP Server
"""

import asyncio
import json
import sys
from pathlib import Path

# Add project directory
sys.path.append(str(Path(__file__).parent))

try:
    from working_autoppt_mcp import WorkingMCPServer
    print("✅ Import successful!")
except Exception as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

async def test_server():
    """Test MCP server functionality."""
    server = WorkingMCPServer()
    
    # Test tool listing
    tools_request = {"method": "tools/list", "params": {}}
    response = await server.handle_request(tools_request)
    print("Tools response:", json.dumps(response, indent=2))
    
    # Test tool call
    tool_request = {
        "method": "tools/call", 
        "params": {
            "name": "create_presentation",
            "arguments": {
                "request": "Create a 3-slide presentation on debug test",
                "output_file": "debug_test.pptx"
            }
        }
    }
    response = await server.handle_request(tool_request)
    print("Tool call response:", json.dumps(response, indent=2))

if __name__ == "__main__":
    print("🎯 Debug MCP Server Test")
    print("=" * 40)
    asyncio.run(test_server())
