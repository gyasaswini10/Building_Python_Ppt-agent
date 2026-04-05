# AutoPPT Agent - Build Your Own Presentations

**Created by:** Yasaswini  
**Course:** AI Agents & MCP Architecture  
**Project:** Make PowerPoint presentations automatically using code  

---

## What This Does

I built this system to create PowerPoint presentations automatically. You just give it a simple request like "Create a 5-slide presentation on renewable energy" and it does all the work - research, writing, and formatting.

### How It Works

```
Your Request → My Agent Brain → Research Tools → PowerPoint File
                    ↓
              Plans the slides first
                    ↓
              Finds content online
                    ↓
              Creates each slide
                    ↓
              Saves the final file
```

### Project Files

```
ASSIGNMENT/
├── client/                          # Main code
│   ├── Build_Agent.ipynb           # Complete implementation guide
│   ├── agent_ppt.py                # The brain of the operation
│   ├── ppt_mcp_server.py           # PowerPoint tools
│   └── research_mcp_server.py      # Web research tools
├── docs/                           # Documentation
│   ├── CLAUDE_PROMPT.md            # For Claude integration
│   ├── MCP_PROMPT_TEMPLATE.md      # Technical details
│   └── README_MCP_INTEGRATION.md   # Setup guide
├── savingfolder_output/            # Your presentations end up here
├── config/.env.template            # API key template
└── README.md                       # This file
```

---

## Getting Started

### 1. Setup Your Environment

```bash
# Install what you need
pip install -r requirements.txt

# Set up your API keys
cp config/.env.template .env
# Edit .env with your API keys
```

### 2. Start the Servers

You'll need two terminal windows:

```bash
# Terminal 1: PowerPoint Server
python client/ppt_mcp_server.py

# Terminal 2: Research Server  
python client/research_mcp_server.py
```

### 3. Create Your First Presentation

**Option 1: Using the Complete Notebook (Recommended)**
```bash
# Open the complete system
jupyter notebook client/Build_Agent.ipynb

# Run cells in order to create presentations
# Everything is included - no separate files needed
```

**Option 2: Quick Command Line (Legacy)**
```bash
# If you prefer command line, use the reference files:
python client/Modular\code\agent_ppt.py "Create a 5-slide presentation on solar energy" --output "solar.pptx"

# Note: You'll need to start MCP servers manually
```

---

## API Keys Setup

You'll need API keys for the content generation. Create a `.env` file:

```env
# OpenRouter API Keys (these work best)
OPENROUTER_API_KEY_1=your_key_here
OPENROUTER_API_KEY_2=backup_key_here

# HuggingFace Tokens (backup option)
HF_TOKENS=token1,token2,token3
```

**Where to get keys:**
- OpenRouter: https://openrouter.ai/keys (fast, reliable)
- HuggingFace: https://huggingface.co/settings/tokens (free tier available)

---

## What You Can Ask For

The system works with simple requests like:
- "Create a 5-slide presentation on renewable energy"
- "Make a presentation about machine learning"
- "Generate slides on climate change impacts"
- "Create presentation on photosynthesis for students"

---

## How the Pieces Fit Together

### The Main Agent (`agent_ppt.py`)
This is the coordinator. It:
- Takes your request and figures out what slides to make
- Talks to the research servers to get content
- Uses AI to write good bullet points
- Puts everything together in the right order

### PowerPoint Server (`ppt_mcp_server.py`)
These are the PowerPoint tools:
- `create_pptx(title)` - Start a new presentation
- `add_slide(session_id, title, bullets)` - Add content slides
- `delete_slide(session_id, slide_index)` - Remove slides
- `get_slide_info(session_id)` - Check what you have
- `save_presentation(session_id, path)` - Save your work

### Research Server (`research_mcp_server.py`)
This finds content for your slides:
- `search_topic(query, title)` - Research online
- `get_definition(word)` - Get word meanings

---

## Quality You Can Expect

Each presentation includes:
- ✅ 3-6 bullet points per slide with real information
- ✅ Professional dark theme with consistent formatting
- ✅ Educational content, not placeholder text
- ✅ Logical flow from introduction to conclusion
- ✅ Proper PowerPoint files that open anywhere

---

## Handling Problems

I built this to be reliable:

1. **Multiple API Keys**: If one key fails, it tries others
2. **Research Backup**: If web research fails, it uses AI knowledge
3. **Error Recovery**: If something breaks, it tries to fix itself
4. **Quality Control**: Filters out bad content automatically

---

## Testing It Out

```python
# Quick test to see if everything works
python client/agent_ppt.py "Create a 3-slide presentation on testing" --output "test.pptx"
```

You should see something like:
```
[AGENT] Designing Professional Research Deck: testing
[AGENT] Generating Expert Content for Slide 1: Origins and Taxonomy
[DEBUG] Trying OpenRouter API...
[DEBUG] OpenRouter succeeded!
[SUCCESS] Expert Presentation Finalized: /path/to/test.pptx
```

---

## Troubleshooting

**If you get API errors:**
- Check your .env file has real API keys
- Make sure the keys have credits available
- Try the backup HuggingFace tokens

**If presentations are empty:**
- Check both servers are running
- Look at the debug messages for clues
- Try a simpler topic first

**If files won't open:**
- Make sure you have the full path ending in .pptx
- Check the folder exists
- Try saving to a different location

---

## Cool Features I Built In

### Smart API Management
- **Key Rotation**: Spreads requests across multiple keys
- **Failure Tracking**: Remembers broken keys and tries again later
- **Provider Switching**: Uses OpenRouter first, falls back to HuggingFace

### Content Quality
- **Context-Aware**: Different prompts for different slide types
- **Real Research**: Uses Wikipedia for accurate information
- **No Placeholders**: Always generates real content

### Professional Output
- **Dark Theme**: Consistent professional styling
- **Smart Layouts**: Automatic text sizing and positioning
- **Image Support**: Adds pictures when available

---

## For Developers

If you want to extend this:

### Adding New Tools
```python
@mcp.tool()
def your_custom_tool(param1: str) -> dict:
    """Do something cool with presentations."""
    # Your code here
    return {"ok": True, "result": "success"}
```

### Custom Content Strategies
Edit the `_finalize_bullets` method in `agent_ppt.py` to add your own content sources.

### New Themes
Modify the color schemes in `ppt_mcp_server.py` to create different visual styles.

---

## What I Learned

Building this taught me a lot about:
- **MCP Protocol**: How to build custom servers
- **Async Programming**: Handling multiple operations at once
- **API Integration**: Working with different AI providers
- **Content Generation**: Making AI write useful content
- **Error Handling**: Building systems that don't break easily

---

## Final Thoughts

This system shows how you can combine different AI tools to do something genuinely useful. Instead of just generating text, it creates complete, professional presentations that people can actually use.

The best part? Once it's set up, you can create presentations on almost any topic in under a minute, and they actually contain good information rather than placeholder text.

---

**Need help?** Check the `docs/` folder for detailed guides, or look through the Jupyter notebook for step-by-step instructions.

**Happy presenting!** 🎉
