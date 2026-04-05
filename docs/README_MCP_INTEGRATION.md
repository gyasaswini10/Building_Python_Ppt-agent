# AutoPPT MCP Integration Guide

## Overview
This AutoPPT system provides MCP (Model Context Protocol) servers that enable Claude to autonomously create PowerPoint presentations from natural language prompts.

## Setup Instructions

### 1. Start the MCP Servers

You need to run two MCP servers that Claude will connect to:

```bash
# Terminal 1: Start PPT Server
cd "c:\Users\gyasu\Desktop\CAlibo noww\ASSIGNMENT"
python client\ppt_mcp_server.py

# Terminal 2: Start Research Server  
python client\research_mcp_server.py
```

### 2. Configure Claude Connection

When connecting Claude to these MCP servers, use the prompt from `CLAUDE_PROMPT.md`:

```
You are an expert Presentation Agent that creates professional PowerPoint presentations using MCP servers.

[Copy the full prompt from CLAUDE_PROMPT.md]
```

### 3. Available MCP Tools

#### PPT Management Tools:
- `create_pptx(title)` - Initialize presentation
- `add_slide(session_id, title, bullets)` - Add content slide
- `delete_slide(session_id, slide_index)` - Remove slide
- `get_slide_info(session_id, slide_index)` - Check slides
- `add_image(session_id, slide_index, image_path)` - Add images
- `save_presentation(session_id, output_path)` - Save .pptx

#### Research Tools:
- `search_topic(query, slide_title)` - Get content for slides

## Usage Examples

### Basic Usage
```
User: "Create a 5-slide presentation on renewable energy"

Claude will:
1. Plan slide titles (Introduction, Solar Power, Wind Energy, etc.)
2. Research each topic
3. Create slides with detailed content
4. Save as renewable_energy.pptx
```

### Advanced Usage
```
User: "Create a 6-slide presentation on tomato origins and taxonomy with concrete examples"

Claude will generate:
- Slide 1: Origins and Taxonomy (with concrete examples)
- Slide 2: Physiological & Structural Features
- Slide 3: Biological Growth & Lifecycle
- Slide 4: Ecological & Environmental Roles
- Slide 5: Industrial & Societal Impact
- Slide 6: Future Research & Conservation Directions
```

## Key Features

### ✅ Smart Content Generation
- Uses OpenRouter API for high-quality content
- Falls back to HuggingFace if needed
- Research integration for accurate information
- No placeholder content - all slides have substantive matter

### ✅ Robust Error Handling
- Multiple API keys with automatic rotation
- 5-minute cooldown for failed keys
- Graceful fallback when research fails
- Always completes the presentation

### ✅ Professional Output
- Dark scientific theme with gold accents
- Proper formatting and styling
- Image support when available
- Valid .pptx files

## Architecture

### MCP Server 1: ppt_mcp_server.py
- Handles PowerPoint creation using python-pptx
- Manages in-memory presentation sessions
- Provides slide manipulation tools
- Applies professional styling

### MCP Server 2: research_mcp_server.py  
- Web research integration
- Wikipedia content extraction
- Image thumbnail discovery
- Content filtering and validation

### Agent Logic: agent_ppt.py
- Orchestrates the presentation creation workflow
- Manages API keys and error handling
- Coordinates between MCP servers
- Ensures content quality and coherence

## File Structure

```
ASSIGNMENT/
├── client/
│   ├── agent_ppt.py           # Main agent logic
│   ├── ppt_mcp_server.py      # PowerPoint MCP server
│   └── research_mcp_server.py  # Research MCP server
├── savingfolder_output/        # Generated presentations
├── .env                        # API keys configuration
├── CLAUDE_PROMPT.md           # Claude system prompt
└── MCP_PROMPT_TEMPLATE.md     # Detailed MCP documentation
```

## API Configuration

Update your `.env` file with API keys:

```env
# OpenRouter API Keys (Primary - Fast)
OPENROUTER_API_KEY_1=your_key_here
OPENROUTER_API_KEY_2=your_key_here

# HuggingFace Tokens (Fallback)
HF_TOKENS=token1,token2,token3
```

## Testing

Test the system works:

```bash
python client\agent_ppt.py "Create a 5-slide presentation on Artificial Intelligence" --output "ai_test.pptx"
```

Check the output in `savingfolder_output/ai_test.pptx`.

## Troubleshooting

### Common Issues:

1. **API Key Errors**: Check .env file format and key validity
2. **MCP Connection**: Ensure both servers are running before connecting Claude
3. **Empty Presentations**: Verify API keys have sufficient credits
4. **Research Failures**: System will generate content automatically if research fails

### Debug Mode:
The system outputs detailed debug information showing:
- Which API keys are loaded
- API call attempts and successes
- Content generation process
- Final file save location

## Integration with Claude

When Claude is connected to the MCP servers:

1. **Planning Phase**: Claude analyzes the request and plans slide structure
2. **Research Phase**: Uses search_topic for each slide's content
3. **Creation Phase**: Builds slides with add_slide using researched content
4. **Review Phase**: Checks slides with get_slide_info
5. **Finalization**: Saves presentation with save_presentation

The entire process is autonomous - Claude handles all tool calls and creates a complete .pptx file without user intervention.

## Quality Assurance

- All slides contain 3-6 substantive bullet points
- Content is factual and educational
- Professional formatting and styling
- Valid PowerPoint files that open correctly
- Error-free operation with multiple fallbacks

This system fulfills all assignment requirements:
✅ MCP Integration (2 servers)
✅ Agentic Loop (plan → research → create → save)
✅ Content Generation (real content, no placeholders)
✅ Output (valid .pptx files)
✅ Error Handling (graceful fallbacks)
