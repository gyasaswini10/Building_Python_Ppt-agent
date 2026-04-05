#!/usr/bin/env python3
"""
Simple AutoPPT MCP Server

Minimal MCP server for Claude integration with AutoPPT functionality.
"""

import asyncio
import json
import sys
from pathlib import Path

# Add project directory
sys.path.append(str(Path(__file__).parent))

try:
    from autoppt_single import AutoPPTSingle
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)

# Simple MCP server implementation
class SimpleMCPServer:
    def __init__(self):
        self.agent = None
        
    async def handle_request(self, request_data):
        """Handle MCP request."""
        try:
            method = request_data.get("method")
            params = request_data.get("params", {})
            
            if method == "tools/list":
                return {
                    "result": {
                        "tools": [
                            {
                                "name": "create_presentation",
                                "description": "Create a PowerPoint presentation from natural language",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "request": {"type": "string", "description": "Presentation request"}
                                    }
                                }
                            }
                        ]
                    }
                }
            elif method == "tools/call":
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                
                if tool_name == "create_presentation":
                    request = arguments.get("request", "")
                    if request:
                        print(f"🎯 Creating presentation: {request}")
                        self.agent = AutoPPTSingle(request, "presentation.pptx")
                        result = await self.agent.execute()
                        
                        return {
                            "result": {
                                "content": [{"type": "text", "text": f"✅ Presentation created! {result}"}]
                            }
                        }
            
            return {"error": {"code": -1, "message": "Unknown method"}}
            
        except Exception as e:
            return {"error": {"code": -2, "message": str(e)}}

async def main():
    """Run the simple MCP server."""
    server = SimpleMCPServer()
    
    print("🚀 Simple AutoPPT MCP Server")
    print("📊 Ready for Claude connection!")
    print("💡 Use create_presentation tool to get started")
    
    # Simple stdio communication
    while True:
        try:
            line = input()
            if line:
                request = json.loads(line)
                response = await server.handle_request(request)
                print(json.dumps(response))
            else:
                break
        except EOFError:
            break
        except Exception as e:
            print(json.dumps({"error": {"code": -3, "message": str(e)}}))
    
    print("🔚 Server stopped")

if __name__ == "__main__":
    asyncio.run(main())
