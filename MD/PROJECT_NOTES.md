# Project Notes - AutoPPT Agent

## What I Built

I made a system that creates PowerPoint presentations automatically. You give it a simple request like "Create a 5-slide presentation on solar energy" and it does everything:

1. Plans out what slides to make
2. Researches the topic online  
3. Writes content for each slide
4. Formats everything nicely
5. Saves the final PowerPoint file

## How It Works

The system has been **consolidated into a single comprehensive notebook** (`client/Build_Agent.ipynb`) for better understanding and ease of use.

### The Complete Notebook Contains:

1. **The Brain (Agent Logic)** - Main coordinator that:
   - Takes your request and figures out what slides to create
   - Manages API keys so it doesn't run out of requests
   - Coordinates between different tools
   - Makes sure everything flows logically

2. **PowerPoint Tools** - These handle the actual PowerPoint creation:
   - `create_pptx()` - Starts a new presentation
   - `add_slide()` - Adds slides with titles and bullet points
   - `delete_slide()` - Removes slides if needed
   - `get_slide_info()` - Checks what slides exist
   - `save_presentation()` - Saves the final file

3. **Research Helper** - This finds real information online:
   - `search_topic()` - Searches Wikipedia for facts
   - Filters content to match slide topics
   - Gets images when available

4. **API Management** - Smart system that:
   - Uses multiple API keys so it doesn't get stuck
   - Switches between OpenRouter and HuggingFace automatically
   - Remembers failed keys and tries again later

## Cool Features

### Smart API Management
- Uses multiple API keys so it doesn't get stuck
- Switches between OpenRouter and HuggingFace automatically
- Remembers failed keys and tries again later

### Real Content
- Uses Wikipedia for accurate information
- Filters out low-quality content
- Generates actual educational material, not placeholders

### Professional Look
- Dark theme with gold accents
- Consistent formatting
- Automatic text sizing
- Professional layouts

## What You Need

### API Keys
Get API keys from:
- OpenRouter: https://openrouter.ai/keys (fast, works best)
- HuggingFace: https://huggingface.co/settings/tokens (backup option)

Put them in a `.env` file:
```env
OPENROUTER_API_KEY_1=your_key_here
OPENROUTER_API_KEY_2=backup_key
HF_TOKENS=token1,token2
```

### Software
Install the requirements:
```bash
pip install -r requirements.txt
```

## Using It

### Start the Servers
Open two terminal windows:

```bash
# Terminal 1
python client/ppt_mcp_server.py

# Terminal 2  
python client/research_mcp_server.py
```

### Create Presentations
```bash
python client/agent_ppt.py "Create a 5-slide presentation on renewable energy" --output "energy.pptx"
```

## What I Learned

This project taught me:
- How to build MCP servers from scratch
- Working with multiple AI APIs
- Async programming in Python
- Error handling and fallbacks
- Making systems that don't break easily

## Problems I Solved

1. **API Rate Limits**: Built key rotation system
2. **Bad Content**: Added filtering and validation
3. **Broken APIs**: Made backup systems
4. **Empty Presentations**: Fixed content generation
5. **Ugly Slides**: Added professional styling

## Examples

The system can create presentations on:
- Science topics (photosynthesis, climate change)
- Technology (AI, machine learning)
- Business (marketing strategies)
- Education (study techniques)

Each presentation has 6 slides with real content, not placeholders.

## Final Thoughts

This was a challenging but fun project. It shows how you can combine different AI tools to do something genuinely useful. Instead of just generating text, it creates complete presentations that people can actually use for work or school.

The best part is that it's reliable - it handles errors gracefully and always produces something useful, even when things go wrong.

---

**Created by:** Yasaswini  
**Course:** AI Agents & MCP Architecture
