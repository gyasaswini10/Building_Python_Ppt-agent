# Claude MCP Integration Setup Guide

This guide shows how to connect your AutoPPT system to Claude using MCP (Model Context Protocol).

Created by: Yasaswini
Course: AI Agents & MCP Architecture

---

## 🎯 **What We've Created**

### **1. Combined AutoPPT MCP Server**
- **File:** `autoppt_mcp_server.py`
- **Purpose:** Single server with all PowerPoint and research tools
- **Benefits:** Easier Claude integration, single connection point

### **2. Claude Configuration**
- **File:** `claude_mcp_config.json`
- **Purpose:** Tells Claude how to connect to your AutoPPT tools
- **Format:** Standard MCP server configuration

---

## 🔧 **Setup Steps**

### **Step 1: Verify Files**
Make sure these files exist:
```
c:\Users\gyasu\Desktop\CAlibo noww\ASSIGNMENT\
├── autoppt_mcp_server.py          # Combined MCP server
├── claude_mcp_config.json          # Claude configuration
└── client\Modular\code\           # Reference implementations
    ├── ppt_mcp_server.py
    ├── research_mcp_server.py
    └── agent_ppt.py
```

### **Step 2: Test the MCP Server**
```bash
cd "c:\Users\gyasu\Desktop\CAlibo noww\ASSIGNMENT"
python autoppt_mcp_server.py
```

**Expected Output:**
```
🎯 AutoPPT MCP Server for Claude Integration
==================================================
🚀 AutoPPT MCP Server starting...
📊 Available tools:
  - create_presentation: Create new PowerPoint
  - add_slide: Add slide with content
  - research_topic: Research topics online
  - save_presentation: Save to file
  - get_slide_info: Get slide information
  - delete_slide: Remove slide
🔗 Ready for Claude connection!
```

### **Step 3: Configure Claude**

**Option A: Using Claude Desktop App**
1. **Open Claude Desktop**
2. **Go to Settings** → **Developer**
3. **Edit MCP Servers** configuration
4. **Copy-paste** the content from `claude_mcp_config.json`
5. **Restart Claude** to load the new tools

**Option B: Using Claude Web**
1. **Open Claude.ai** in browser
2. **Go to Settings** → **API & Integrations**
3. **Find MCP section** and add server configuration
4. **Use the JSON** from `claude_mcp_config.json`

---

## 🛠️ **Available Tools in Claude**

Once connected, you'll have these tools available:

### **🎨 PowerPoint Creation Tools**
```
create_presentation(title)
- Creates a new PowerPoint presentation
- Returns session_id for further operations

add_slide(session_id, slide_title, bullets)
- Adds a slide with title and bullet points
- Automatically formats with professional theme

save_presentation(session_id, output_path)
- Saves the presentation to .pptx file
- Returns success status and file location
```

### **🔍 Research Tools**
```
research_topic(query, slide_title)
- Researches topics online using Wikipedia
- Returns bullet points and relevant content
- Automatically filters for presentation quality
```

### **📊 Management Tools**
```
get_slide_info(session_id, slide_index)
- Gets information about slides
- Returns titles and content

delete_slide(session_id, slide_index)
- Removes a slide from presentation
- Updates slide numbering automatically
```

---

## 🎯 **Example Claude Usage**

### **Creating a Presentation**
```
User: "Create a 6-slide presentation on renewable energy"

Claude will:
1. research_topic("renewable energy", "Introduction")
2. create_presentation("Renewable Energy")
3. add_slide(session_id, "Introduction", research_results)
4. add_slide(session_id, "Solar Energy", more_research)
5. save_presentation(session_id, "renewable_energy.pptx")
```

### **Research-First Approach**
```
User: "Research blockchain technology and create a presentation"

Claude will:
1. research_topic("blockchain technology", "What is Blockchain")
2. research_topic("blockchain technology", "Applications")
3. research_topic("blockchain technology", "Future")
4. Create presentation with researched content
5. Save as professional PowerPoint
```

---

## 🔧 **Configuration Details**

### **Server Configuration**
```json
{
  "mcpServers": {
    "autoppt": {
      "command": "C:\\Users\\gyasu\\AppData\\Local\\Programs\\Python\\Python313\\python.exe",
      "args": [
        "C:\\Users\\gyasu\\Desktop\\CAlibo noww\\ASSIGNMENT\\autoppt_mcp_server.py"
      ],
      "env": {
        "PYTHONPATH": "C:\\Users\\gyasu\\Desktop\\CAlibo noww\\ASSIGNMENT"
      }
    }
  }
}
```

### **Environment Variables**
- **PYTHONPATH:** Points to your project directory
- **Command:** Uses your Python installation
- **Args:** Points to the combined MCP server

---

## 🚀 **Testing the Connection**

### **Step 1: Start the Server**
```bash
python autoppt_mcp_server.py
```

### **Step 2: Connect Claude**
1. **Open Claude Desktop/Web**
2. **Check for "AutoPPT" tools** in your tool list
3. **Try a simple command** like creating a presentation

### **Step 3: Verify Output**
- **Presentations appear** in `savingfolder_output/`
- **Professional formatting** with dark theme
- **Real content** from web research

---

## 🎯 **Benefits of MCP Integration**

### **For Claude Users:**
✅ **Native PowerPoint creation** - No external tools needed
✅ **Real-time research** - Up-to-date information
✅ **Professional output** - Consistent formatting
✅ **Workflow automation** - Multi-step processes

### **For Your System:**
✅ **Single connection point** - One MCP server
✅ **Easy maintenance** - Combined codebase
✅ **Claude integration** - Native tool support
✅ **Scalable architecture** - Easy to extend

---

## 🔍 **Troubleshooting**

### **Server Won't Start:**
```bash
# Check Python path
where python

# Check file exists
dir autoppt_mcp_server.py

# Test imports
python -c "import sys; print(sys.path)"
```

### **Claude Can't Connect:**
1. **Check JSON format** - Must be valid JSON
2. **Verify file paths** - Use double backslashes
3. **Restart Claude** - Required for new servers
4. **Check permissions** - Python needs execute rights

### **Tools Not Available:**
1. **Verify server is running** - Check terminal output
2. **Check Claude settings** - MCP section
3. **Look for errors** - In Claude developer console

---

## 🎉 **Success Indicators**

### **When It's Working:**
✅ **Server starts** without errors
✅ **Claude shows** "AutoPPT" tools
✅ **Commands execute** successfully
✅ **Presentations create** in output folder
✅ **Files open** in PowerPoint

### **Expected Claude Experience:**
- **Tool suggestions** appear automatically
- **Multi-step workflows** execute smoothly
- **Research integration** works seamlessly
- **Professional output** every time

---

**🎯 Your AutoPPT system is now ready for Claude MCP integration!**

**Next Steps:**
1. **Test the MCP server** with `python autoppt_mcp_server.py`
2. **Configure Claude** using the JSON file
3. **Start creating presentations** directly in Claude!
