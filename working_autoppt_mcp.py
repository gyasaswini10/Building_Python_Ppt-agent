#!/usr/bin/env python3
"""
Working AutoPPT MCP Server

Functional MCP server that works with the simple AutoPPT agent.
"""

import asyncio
import json
import sys
import os
from pathlib import Path

# Add project directory
sys.path.append(str(Path(__file__).parent))

# IMPORTANT: Redirect ALL standard output to standard error 
# because Claude expects ONLY JSON on stdout.
# We will use sys.stdout.write specifically for the JSON responses.
original_stdout = sys.stdout
sys.stdout = sys.stderr

try:
    from simple_autoppt import SimpleAutoPPT
except ImportError as e:
    print(f"Import error: {e}", file=sys.stderr)
    sys.exit(1)

class WorkingMCPServer:
    def __init__(self):
        self.current_agent = None
        
    async def handle_create_presentation(self, arguments):
        """Handle presentation creation."""
        try:
            request = arguments.get("request", "")
            output_file = arguments.get("output_file", "presentation.pptx")
            
            if not request:
                return {"content": [{"type": "text", "text": "❌ Request is required"}], "isError": True}
            
            print(f"🎯 Claude requested: {request}", file=sys.stderr)
            
            # Create and run the agent
            self.current_agent = SimpleAutoPPT(request, output_file)
            result = await self.current_agent.execute()
            
            if result["ok"]:
                success_text = f"""✅ Presentation created successfully!

📋 Request: {request}
📁 File: {result.get('output_path', 'Unknown')}
📊 Size: {result.get('file_size', 0):,} bytes
📈 Slides: {result.get('slides_created', 0)}

🎉 Your presentation is ready!"""
                
                return {"content": [{"type": "text", "text": success_text}]}
            else:
                error_text = f"""❌ Presentation creation failed!

📋 Request: {request}
❌ Error: {result.get('error', 'Unknown error')}

Please try again."""
                
                return {"content": [{"type": "text", "text": error_text}], "isError": True}
                
        except Exception as e:
            return {"content": [{"type": "text", "text": f"Error: {str(e)}"}], "isError": True}
    
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
                                "description": "Create a PowerPoint presentation from natural language request",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "request": {
                                            "type": "string", 
                                            "description": "Natural language request (e.g., 'Create a 5-slide presentation on solar energy')"
                                        },
                                        "output_file": {
                                            "type": "string",
                                            "description": "Output filename (optional, default: presentation.pptx)"
                                        }
                                    },
                                    "required": ["request"]
                                }
                            }
                        ]
                    }
                }
            elif method == "tools/call":
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                
                if tool_name == "create_presentation":
                    return await self.handle_create_presentation(arguments)
            
            return {"error": {"code": -1, "message": f"Unknown method: {method}"}}
            
        except Exception as e:
            return {"error": {"code": -2, "message": str(e)}}

async def main():
    """Run the working MCP server."""
    server = WorkingMCPServer()
    
    print("🚀 Working AutoPPT MCP Server", file=sys.stderr)
    print("📊 Ready for Claude connection!", file=sys.stderr)
    print("💡 Tool available: create_presentation", file=sys.stderr)
    print("🔗 Waiting for Claude requests...", file=sys.stderr)
    
    # Simple stdio communication loop
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break
                
            line = line.strip()
            if line:
                try:
                    request = json.loads(line)
                    response = await server.handle_request(request)
                    
                    # Send response back on ORIGINAL stdout
                    original_stdout.write(json.dumps(response) + "\n")
                    original_stdout.flush()
                    
                except json.JSONDecodeError:
                    error_response = {"error": {"code": -3, "message": "Invalid JSON"}}
                    original_stdout.write(json.dumps(error_response) + "\n")
                    original_stdout.flush()
                    
        except KeyboardInterrupt:
            break
        except Exception as e:
            error_response = {"error": {"code": -4, "message": str(e)}}
            original_stdout.write(json.dumps(error_response) + "\n")
            original_stdout.flush()
    
    print("Server stopped", file=sys.stderr)

if __name__ == "__main__":
    asyncio.run(main())
