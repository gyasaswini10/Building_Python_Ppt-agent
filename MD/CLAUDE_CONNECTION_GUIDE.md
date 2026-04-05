# AutoPPT MCP Connection Guide

## 🎯 **Complete Setup for Claude Integration**

### **✅ What You Have:**

**Working Files:**
- `simple_autoppt.py` - Working standalone agent
- `working_autoppt_mcp.py` - Working MCP server
- `claude_final_config.json` - Final Claude configuration
- `start_mcp_server.bat` - Server startup script

### **🚀 How to Connect to Claude:**

## **Step 1: Start MCP Server**

**Option A: Direct Python**
```bash
cd "c:\Users\gyasu\Desktop\CAlibo noww\ASSIGNMENT"
python working_autoppt_mcp.py
```

**Option B: PowerShell**
```powershell
cd "c:\Users\gyasu\Desktop\CAlibo noww\ASSIGNMENT"
Start-Process python -ArgumentList "working_autoppt_mcp.py"
```

**Option C: Command Prompt**
```cmd
cd "c:\Users\gyasu\Desktop\CAlibo noww\ASSIGNMENT"
cmd /k start /min python working_autoppt_mcp.py
```

## **Step 2: Configure Claude**

1. **Open Claude Desktop** or **Claude.ai**
2. **Go to Settings** → **Developer** → **MCP Servers**
3. **Add New Server** with this configuration:

```json
{
  "name": "AutoPPT",
  "command": "C:\\Users\\gyasu\\AppData\\Local\\Programs\\Python\\Python313\\python.exe",
  "args": [
    "C:\\Users\\gyasu\\Desktop\\CAlibo noww\\ASSIGNMENT\\working_autoppt_mcp.py"
  ]
}
```

4. **Save and Restart Claude**

## **Step 3: Use AutoPPT in Claude**

### **Available Tool:**
- **`create_presentation`** - Create PowerPoint from natural language

### **Example Usage in Claude:**
```
User: Create a 6-slide presentation on solar energy

Claude: I'll create a professional PowerPoint presentation on solar energy for you.

[Creates presentation with slides:
- Introduction to Solar Energy
- Key Technologies
- Applications and Uses
- Benefits and Advantages
- Challenges and Solutions
- Conclusion and Future]

✅ Presentation saved as: presentation.pptx
📁 Location: C:\Users\gyasu\Desktop\CAlibo noww\ASSIGNMENT\solar_energy.pptx
```

---

## 🔧 **Quick Test Commands**

### **Test Standalone Agent:**
```bash
python simple_autoppt.py "Create a 5-slide presentation on artificial intelligence" --output "ai_test.pptx"
```

### **Test MCP Server:**
```bash
python working_autoppt_mcp.py
# Server will start and wait for Claude connections
```

---

## 🎯 **What You'll See:**

### **MCP Server Output:**
```
🎯 AutoPPT MCP Server for Claude
========================================
🚀 Working AutoPPT MCP Server
📊 Ready for Claude connection!
💡 Tool available: create_presentation
🔗 Waiting for Claude requests...
```

### **Claude Integration:**
- **AutoPPT tool appears** in Claude's tool list
- **Natural language requests** work seamlessly
- **Professional PowerPoint files** generated automatically
- **Real-time feedback** in Claude interface

---

## 🎉 **Success Indicators:**

### **When Connected:**
✅ **MCP server starts** without errors
✅ **Claude shows** "AutoPPT" tool
✅ **Tool calls execute** successfully
✅ **Presentations create** in output folder
✅ **Files open** in PowerPoint

### **Expected Workflow:**
1. **Start MCP server** (keeps running)
2. **Configure Claude** with the JSON config
3. **Use in Claude** - Just ask for presentations!
4. **Get results** - Professional PowerPoint files

---

## 🔍 **Troubleshooting**

### **Server Won't Start:**
- Check Python path: `where python`
- Check file exists: `dir working_autoppt_mcp.py`
- Test imports: `python -c "import sys; print(sys.path)"`

### **Claude Won't Connect:**
- Verify JSON format in Claude settings
- Check file paths (use double backslashes)
- Restart Claude after configuration
- Check MCP server is running

### **Tool Not Available:**
- Look for "AutoPPT" in Claude's tool list
- Check Claude developer console for errors
- Verify MCP server output in terminal

---

## 🎯 **Final Setup Summary:**

**You now have a complete AutoPPT system that:**

✅ **Works standalone** with simple command
✅ **Integrates with Claude** via MCP protocol
✅ **Creates professional presentations** automatically
✅ **Handles errors gracefully** with fallbacks
✅ **Provides real-time feedback** in Claude interface

**The system is ready for both standalone use and Claude integration!** 🚀

---

## 📁 **Files You Need:**

1. **`claude_final_config.json`** - Copy this to Claude settings
2. **`working_autoppt_mcp.py`** - MCP server for Claude
3. **`simple_autoppt.py`** - Standalone agent
4. **Start the MCP server** using any method above

**That's it! Your AutoPPT system is ready for Claude integration!** 🎉
