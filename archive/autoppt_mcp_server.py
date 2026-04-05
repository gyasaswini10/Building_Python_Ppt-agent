#!/usr/bin/env python3
"""
AutoPPT MCP Server - Combined PowerPoint and Research Tools

This server combines both PowerPoint creation and research capabilities
into a single MCP server for Claude integration.

Created by: Yasaswini
Course: AI Agents & MCP Architecture
"""

import asyncio
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add the modular code path to import our servers
sys.path.append(str(Path(__file__).parent / "Modular" / "code"))

try:
    from ppt_mcp_server import create_pptx, open_presentation, add_slide, delete_slide, get_slide_info, save_presentation
    from research_mcp_server import search_topic
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Make sure the Modular/code/ directory contains the required files")
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

class AutoPPTMCPServer:
    """Combined AutoPPT MCP Server for Claude integration."""
    
    def __init__(self):
        """Initialize the combined AutoPPT server."""
        self.server = Server("autoppt")
        
    async def list_tools(self) -> List[Tool]:
        """List all available AutoPPT tools."""
        tools = [
            Tool(
                name="create_presentation",
                description="Create a new PowerPoint presentation with a title",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "Title for the presentation"
                        }
                    },
                    "required": ["title"]
                }
            ),
            Tool(
                name="add_slide",
                description="Add a slide with title and bullet points to the presentation",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "session_id": {
                            "type": "string",
                            "description": "Session ID from create_presentation"
                        },
                        "slide_title": {
                            "type": "string",
                            "description": "Title for the slide"
                        },
                        "bullets": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of bullet points for the slide"
                        }
                    },
                    "required": ["session_id", "slide_title", "bullets"]
                }
            ),
            Tool(
                name="research_topic",
                description="Research a topic online for presentation content",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Topic to research"
                        },
                        "slide_title": {
                            "type": "string",
                            "description": "Slide title to match content with"
                        }
                    },
                    "required": ["query"]
                }
            ),
            Tool(
                name="save_presentation",
                description="Save the presentation to a file",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "session_id": {
                            "type": "string",
                            "description": "Session ID from create_presentation"
                        },
                        "output_path": {
                            "type": "string",
                            "description": "Path to save the PowerPoint file"
                        }
                    },
                    "required": ["session_id", "output_path"]
                }
            ),
            Tool(
                name="get_slide_info",
                description="Get information about slides in the presentation",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "session_id": {
                            "type": "string",
                            "description": "Session ID from create_presentation"
                        },
                        "slide_index": {
                            "type": "integer",
                            "description": "Index of specific slide (optional, -1 for all)"
                        }
                    },
                    "required": ["session_id"]
                }
            ),
            Tool(
                name="delete_slide",
                description="Delete a slide from the presentation",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "session_id": {
                            "type": "string",
                            "description": "Session ID from create_presentation"
                        },
                        "slide_index": {
                            "type": "integer",
                            "description": "Index of slide to delete"
                        }
                    },
                    "required": ["session_id", "slide_index"]
                }
            )
        ]
        return tools
    
    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> CallToolResult:
        """Execute a tool call."""
        try:
            if name == "create_presentation":
                result = await create_pptx(arguments.get("title", ""))
                return CallToolResult(content=[TextContent(type="text", text=json.dumps(result))])
            
            elif name == "add_slide":
                result = await add_slide(
                    arguments.get("session_id", ""),
                    arguments.get("slide_title", ""),
                    arguments.get("bullets", [])
                )
                return CallToolResult(content=[TextContent(type="text", text=json.dumps(result))])
            
            elif name == "research_topic":
                result = await search_topic(
                    arguments.get("query", ""),
                    arguments.get("slide_title", "")
                )
                return CallToolResult(content=[TextContent(type="text", text=json.dumps(result))])
            
            elif name == "save_presentation":
                result = await save_presentation(
                    arguments.get("session_id", ""),
                    arguments.get("output_path", "")
                )
                return CallToolResult(content=[TextContent(type="text", text=json.dumps(result))])
            
            elif name == "get_slide_info":
                result = await get_slide_info(
                    arguments.get("session_id", ""),
                    arguments.get("slide_index", -1)
                )
                return CallToolResult(content=[TextContent(type="text", text=json.dumps(result))])
            
            elif name == "delete_slide":
                result = await delete_slide(
                    arguments.get("session_id", ""),
                    arguments.get("slide_index", 0)
                )
                return CallToolResult(content=[TextContent(type="text", text=json.dumps(result))])
            
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

    async def run(self):
        """Run the MCP server."""
        # Set up the server with tool handlers
        self.server.list_tools = self.list_tools
        self.server.call_tool = self.call_tool
        
        # Run the server
        options = ServerOptions(
            server_name="autoppt",
            version="1.0.0",
            capabilities={
                "tools": {}
            }
        )
        
        print("🚀 AutoPPT MCP Server starting...")
        print("📊 Available tools:")
        print("  - create_presentation: Create new PowerPoint")
        print("  - add_slide: Add slide with content")
        print("  - research_topic: Research topics online")
        print("  - save_presentation: Save to file")
        print("  - get_slide_info: Get slide information")
        print("  - delete_slide: Remove slide")
        print("🔗 Ready for Claude connection!")
        
        await self.server.run(options)

# Import ServerOptions
try:
    from mcp.server import ServerOptions
except ImportError:
    # Fallback for older MCP versions
    ServerOptions = None

async def main():
    """Main entry point for the AutoPPT MCP server."""
    server = AutoPPTMCPServer()
    await server.run()

if __name__ == "__main__":
    print("🎯 AutoPPT MCP Server for Claude Integration")
    print("=" * 50)
    asyncio.run(main())
