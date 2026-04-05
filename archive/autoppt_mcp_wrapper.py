#!/usr/bin/env python3
"""
AutoPPT MCP Wrapper for Single-File Agent

This wrapper allows the single-file AutoPPT agent to work as an MCP server
for Claude integration while maintaining the simple single-file architecture.

Created by: Yasaswini
Course: AI Agents & MCP Architecture
"""

import asyncio
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

# Add the project directory to import our single agent
sys.path.append(str(Path(__file__).parent))

try:
    from autoppt_single import AutoPPTSingle
except ImportError as e:
    print(f"Error importing AutoPPTSingle: {e}")
    print("Make sure autoppt_single.py is in the same directory")
    sys.exit(1)

# MCP imports
try:
    from mcp.server.models import InitializationOptions
    from mcp.server import NotificationOptions, Server
    from mcp.types import (
        Resource, TextContent, ImageContent, EmbeddedResource,
        CallToolRequest, CallToolResult, ListToolsRequest, ListToolsResult,
        Tool, TextContent, ImageContent
    )
except ImportError:
    print("MCP library not found. Install with: pip install mcp")
    sys.exit(1)

class AutoPPTMCPWrapper:
    """MCP wrapper for the single-file AutoPPT agent."""
    
    def __init__(self):
        """Initialize the MCP wrapper."""
        self.server = Server("autoppt-single")
        self.current_agent = None
        self.current_session = None
        
    async def list_tools(self) -> List[Tool]:
        """List available AutoPPT tools for Claude."""
        tools = [
            Tool(
                name="create_presentation",
                description="Create a PowerPoint presentation on any topic",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "request": {
                            "type": "string",
                            "description": "Natural language request for the presentation (e.g., 'Create a 5-slide presentation on solar energy')"
                        },
                        "output_file": {
                            "type": "string",
                            "description": "Output filename for the PowerPoint file (optional, default: presentation.pptx)"
                        }
                    },
                    "required": ["request"]
                }
            ),
            Tool(
                name="research_topic",
                description="Research a topic for presentation content",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Topic to research"
                        }
                    },
                    "required": ["query"]
                }
            ),
            Tool(
                name="get_presentation_status",
                description="Get status of current presentation creation",
                inputSchema={
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            )
        ]
        return tools
    
    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> CallToolResult:
        """Execute tool calls for AutoPPT functionality."""
        try:
            if name == "create_presentation":
                return await self._handle_create_presentation(arguments)
            elif name == "research_topic":
                return await self._handle_research_topic(arguments)
            elif name == "get_presentation_status":
                return await self._handle_get_status(arguments)
            else:
                return CallToolResult(
                    content=[TextContent(type="text", text=f"Unknown tool: {name}")],
                    isError=True
                )
        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error executing {name}: {str(e)}")],
                isError=True
            )
    
    async def _handle_create_presentation(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Handle presentation creation request."""
        try:
            request = arguments.get("request", "")
            output_file = arguments.get("output_file", "presentation.pptx")
            
            if not request:
                return CallToolResult(
                    content=[TextContent(type="text", text="Request is required")],
                    isError=True
                )
            
            print(f"🎯 Creating presentation: {request}")
            print(f"📁 Output file: {output_file}")
            
            # Create the agent
            self.current_agent = AutoPPTSingle(request, output_file)
            self.current_session = {
                "request": request,
                "output_file": output_file,
                "status": "initializing",
                "started_at": str(asyncio.get_event_loop().time())
            }
            
            # Execute the presentation creation
            result = await self.current_agent.execute()
            
            if result["ok"]:
                self.current_session["status"] = "completed"
                self.current_session["completed_at"] = str(asyncio.get_event_loop().time())
                self.current_session["file_path"] = result.get("output_path", "")
                self.current_session["file_size"] = result.get("file_size", 0)
                self.current_session["slides_created"] = result.get("slides_created", 0)
                
                success_message = f"""✅ Presentation created successfully!

📋 Request: {request}
📁 File: {result.get('output_path', 'Unknown')}
📊 Size: {result.get('file_size', 0):,} bytes
📈 Slides: {result.get('slides_created', 0)}

The presentation is ready for use!"""
                
                return CallToolResult(
                    content=[TextContent(type="text", text=success_message)]
                )
            else:
                self.current_session["status"] = "failed"
                self.current_session["error"] = result.get("error", "Unknown error")
                
                error_message = f"""❌ Presentation creation failed!

📋 Request: {request}
❌ Error: {result.get('error', 'Unknown error')}

Please check your request and try again."""
                
                return CallToolResult(
                    content=[TextContent(type="text", text=error_message)],
                    isError=True
                )
                
        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error in create_presentation: {str(e)}")],
                isError=True
            )
    
    async def _handle_research_topic(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Handle topic research request."""
        try:
            query = arguments.get("query", "")
            if not query:
                return CallToolResult(
                    content=[TextContent(type="text", text="Query is required")],
                    isError=True
                )
            
            print(f"🔍 Researching topic: {query}")
            
            # Create a temporary agent for research
            temp_agent = AutoPPTSingle(f"Research {query}", "temp.pptx")
            research_results = await temp_agent.research_topic(query)
            
            if research_results:
                research_text = f"""🔍 Research Results for: {query}

{'=' * 50}

Found Information:
"""
                for i, point in enumerate(research_results[:8], 1):
                    research_text += f"{i}. {point}\n"
                
                research_text += f"""
{'=' * 50}

📊 Total points found: {len(research_results)}
💡 These can be used for presentation content"""
                
                return CallToolResult(
                    content=[TextContent(type="text", text=research_text)]
                )
            else:
                return CallToolResult(
                    content=[TextContent(type="text", text=f"No research results found for: {query}")],
                    isError=True
                )
                
        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error in research_topic: {str(e)}")],
                isError=True
            )
    
    async def _handle_get_status(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Handle status request."""
        try:
            if not self.current_session:
                return CallToolResult(
                    content=[TextContent(type="text", text="No presentation session active")]
                )
            
            status_text = f"""📊 Current Presentation Status

{'=' * 40}

📋 Request: {self.current_session.get('request', 'Unknown')}
📁 Output File: {self.current_session.get('output_file', 'Unknown')}
🔄 Status: {self.current_session.get('status', 'Unknown')}

📅 Timeline:
• Started: {self.current_session.get('started_at', 'Unknown')}
"""
            
            if self.current_session.get("completed_at"):
                status_text += f"• Completed: {self.current_session['completed_at']}\n"
            
            if self.current_session.get("file_path"):
                status_text += f"""
📁 Results:
• File: {self.current_session['file_path']}
• Size: {self.current_session.get('file_size', 0):,} bytes
• Slides: {self.current_session.get('slides_created', 0)}
"""
            
            if self.current_session.get("error"):
                status_text += f"""
❌ Error Information:
• Error: {self.current_session['error']}
"""
            
            status_text += f"\n{'=' * 40}"
            
            return CallToolResult(
                content=[TextContent(type="text", text=status_text)]
            )
            
        except Exception as e:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error in get_status: {str(e)}")],
                isError=True
            )
    
    async def run(self):
        """Run the MCP wrapper server."""
        # Set up the server with tool handlers
        self.server.list_tools = self.list_tools
        self.server.call_tool = self.call_tool
        
        # Run the server
        options = ServerOptions(
            server_name="autoppt-single",
            version="1.0.0",
            capabilities={
                "tools": {}
            }
        )
        
        print("🚀 AutoPPT Single-File MCP Server starting...")
        print("📊 Available tools:")
        print("  - create_presentation: Create PowerPoint from natural language")
        print("  - research_topic: Research topics for content")
        print("  - get_presentation_status: Check creation status")
        print("🔗 Ready for Claude connection!")
        print("💡 Use create_presentation with your topic to get started!")
        
        await self.server.run(options)

# Import ServerOptions
try:
    from mcp.server import ServerOptions
except ImportError:
    # Fallback for older MCP versions
    ServerOptions = None

async def main():
    """Main entry point for the MCP wrapper."""
    server = AutoPPTMCPWrapper()
    await server.run()

if __name__ == "__main__":
    print("🎯 AutoPPT MCP Wrapper for Claude Integration")
    print("=" * 50)
    asyncio.run(main())
