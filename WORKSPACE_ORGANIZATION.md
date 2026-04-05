# Workspace Organization

## Folder Structure

```
ASSIGNMENT/
├── 📁 client/                    # Main application code
│   ├── Build_Agent.ipynb        # Complete implementation notebook
│   ├── agent_ppt.py              # Main agent logic
│   ├── ppt_mcp_server.py        # PowerPoint tools
│   ├── research_mcp_server.py   # Research tools
│   └── agent_assets/            # Agent resource files
├── 📁 docs/                     # Documentation and guides
│   ├── Agentic_assignment_1_AutoPPT.ipynb  # Original notebook
│   ├── CLAUDE_PROMPT.md         # Claude integration prompt
│   ├── MCP_PROMPT_TEMPLATE.md   # MCP technical docs
│   └── README_MCP_INTEGRATION.md # Setup guide
├── 📁 config/                   # Configuration files
│   ├── .env                      # API keys (gitignored)
│   ├── .env.example              # Example configuration
│   └── .env.template            # Setup template
├── 📁 savingfolder_output/      # Generated presentations
├── 📁 logs/                     # Log files
│   ├── frog_log.txt             # Debug logs
│   └── prompt                    # Prompt history
├── 📁 debug/                    # Debug files
├── 📁 temp_images/              # Temporary image files
├── 📁 MD/                       # Course materials
├── 📁 __pycache__/              # Python cache files
├── 📄 README.md                 # Main project documentation
├── 📄 PROJECT_NOTES.md          # Project summary
├── 📄 requirements.txt          # Python dependencies
├── 📄 .gitignore               # Git ignore rules
└── 📁 .git/                    # Git repository
```

## What's Where

### Code (`client/`)
All the working Python code and the main implementation notebook

### Documentation (`docs/`)
All guides, prompts, and technical documentation

### Configuration (`config/`)
API keys and environment setup files

### Output (`savingfolder_output/`)
All generated PowerPoint presentations

### Logs (`logs/`)
Debug information and system logs

### Cache (`__pycache__/`, `temp_images/`)
Temporary files that can be deleted

## Clean Root Directory
The root directory now only contains:
- Main README.md
- Project notes
- Requirements file
- Git configuration
- Folder organization

This makes it easy to understand the project structure at a glance.
