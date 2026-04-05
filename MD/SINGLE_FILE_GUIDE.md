# AutoPPT Single-File Agent

Complete PowerPoint creation system with a single command - no separate servers needed!

Created by: Yasaswini
Course: AI Agents & MCP Architecture

---

## 🎯 **What This Is**

**Single-file solution** that combines everything:
- PowerPoint creation
- Web research  
- AI content generation
- Professional styling
- API management

**No separate MCP servers** - everything runs in one process!

---

## 🚀 **How to Use**

### **Basic Usage:**
```bash
python autoppt_single.py "Create a 5-slide presentation on solar energy"
```

### **With Custom Output:**
```bash
python autoppt_single.py "Make a presentation about AI" --output "ai_presentation.pptx"
```

### **With Debug Mode:**
```bash
python autoppt_single.py "Create presentation on blockchain" --debug --output "blockchain.pptx"
```

---

## 📋 **Command Options**

| Option | Description | Example |
|--------|-------------|---------|
| (request) | Presentation request (required) | "Create a 5-slide presentation on climate change" |
| --output FILE | Output filename | --output "energy.pptx" |
| --debug | Enable debug output | --debug |

---

## 🎯 **Example Requests**

### **Technology Topics:**
```bash
python autoppt_single.py "Create a 5-slide presentation on machine learning"
python autoppt_single.py "Make a presentation about cybersecurity" --output "security.pptx"
python autoppt_single.py "Generate slides on cloud computing" --output "cloud.pptx"
```

### **Science Topics:**
```bash
python autoppt_single.py "Create a 5-slide presentation on renewable energy"
python autoppt_single.py "Make a presentation about quantum physics" --output "quantum.pptx"
python autoppt_single.py "Generate slides on biotechnology" --debug
```

### **Business Topics:**
```bash
python autoppt_single.py "Create a 5-slide presentation on digital marketing"
python autoppt_single.py "Make a presentation about startup funding" --output "funding.pptx"
python autoppt_single.py "Generate slides on project management" --output "pm.pptx"
```

### **Educational Topics:**
```bash
python autoppt_single.py "Create a 5-slide presentation on study techniques"
python autoppt_single.py "Make a presentation about online learning" --output "learning.pptx"
python autoppt_single.py "Generate slides on research methods" --debug
```

---

## 🎨 **What You Get**

### **Professional PowerPoint Features:**
- **Dark theme** with navy background (#0F192D)
- **Gold accent text** (#FFDF80) for titles
- **White bullet points** for readability
- **Professional layout** with proper spacing
- **6 slides maximum** for optimal presentation length

### **Content Quality:**
- **Real research** from Wikipedia API
- **AI-generated content** when research is limited
- **Intelligent filtering** for quality content
- **Automatic formatting** for bullet points

### **Output:**
- **Valid .pptx files** that open in PowerPoint
- **35-40KB file size** for 6-slide presentations
- **Saved in current directory** or custom path
- **Professional quality** suitable for business/academic use

---

## 📊 **Workflow Process**

### **What Happens When You Run:**

1. **🎯 Parse Request**
   - Extract topic from natural language
   - Determine slide count and output file

2. **🔍 Research Content**
   - Search Wikipedia for real information
   - Generate fallback content if needed
   - Filter for quality and relevance

3. **🤖 Generate AI Content**
   - Use OpenRouter API (primary)
   - Fallback to HuggingFace API
   - Generate slide-specific content

4. **📊 Create Presentation**
   - Initialize PowerPoint with professional theme
   - Add slides with titles and bullets
   - Apply dark theme consistently

5. **💾 Save and Report**
   - Save to specified output file
   - Report success with file details
   - Show location and file size

---

## 🔧 **Setup Requirements**

### **Environment Variables (.env file):**
```env
# OpenRouter API Keys (recommended)
OPENROUTER_API_KEY_1=your_openrouter_key_here
OPENROUTER_API_KEY_2=backup_openrouter_key

# HuggingFace Tokens (fallback)
HF_TOKENS=hf_token1,hf_token2,hf_token3

# Alternative formats
OPENROUTER_KEYS=key1,key2,key3
HF_TOKEN=combined_token_string
```

### **Python Packages:**
```bash
pip install python-pptx httpx python-dotenv asyncio
```

---

## 🎯 **Benefits of Single-File Approach**

### **Simplicity:**
✅ **One command** - No separate servers to manage
✅ **No setup** - Just run the script
✅ **Self-contained** - Everything in one file
✅ **Easy deployment** - Copy and run anywhere

### **Reliability:**
✅ **Integrated error handling** - All errors caught in one place
✅ **Smart API rotation** - Automatic key management
✅ **Graceful fallbacks** - Research → AI → Fallback
✅ **Professional output** - Consistent formatting

### **Performance:**
✅ **Fast execution** - No server communication overhead
✅ **Lower memory** - Single process
✅ **Better debugging** - All logs in one place
✅ **Portable** - Works on any system with Python

---

## 🧪 **Testing Examples**

### **Quick Test:**
```bash
# Test with simple topic
python autoppt_single.py "Create a 5-slide presentation on Python programming"

# Expected output:
# 🎯 AutoPPT Single-File Agent
# 🚀 Starting AutoPPT Agent Workflow
# 📋 Topic extracted: Python programming
# 🔍 Researching content...
# 📊 Creating presentation...
# 🤖 Generating slide content...
# 💾 Saving presentation...
# 🎉 Presentation created successfully!
```

### **Debug Mode:**
```bash
python autoppt_single.py "Test presentation" --debug

# Shows detailed API calls, research results, and processing steps
```

---

## 🎉 **Success Indicators**

### **When It Works:**
✅ **Command parses** without syntax errors
✅ **API keys load** from environment
✅ **Research succeeds** or falls back gracefully
✅ **Presentation creates** with professional styling
✅ **File saves** to specified location
✅ **PowerPoint opens** the generated file

### **Expected Output:**
```
🎯 AutoPPT Single-File Agent
========================================
🚀 Starting AutoPPT Agent Workflow
==================================================
📋 Topic extracted: solar energy
🔍 Researching content...
📊 Creating presentation...
🤖 Generating slide content...
💾 Saving presentation...
🎉 Presentation created successfully!
📁 Location: C:\Users\gyasu\Desktop\CAlibo noww\ASSIGNMENT\solar.pptx
📊 File size: 38,456 bytes
✅ Success! Created 6 slides
```

---

## 🔍 **Troubleshooting**

### **Common Issues:**

#### **Import Errors:**
```bash
# Install missing packages
pip install python-pptx httpx python-dotenv

# Check Python version (3.8+ required)
python --version
```

#### **API Key Issues:**
```bash
# Check if .env file exists
ls .env

# Test API key loading
python -c "from dotenv import load_dotenv; load_dotenv(); import os; print('Keys found:', bool(os.getenv('OPENROUTER_API_KEY_1')))"
```

#### **Permission Errors:**
```bash
# Check write permissions
python -c "from pathlib import Path; Path('test.pptx').touch(); print('Write OK')"

# Use different output directory
python autoppt_single.py "Test" --output "C:/temp/test.pptx"
```

---

## 🎯 **Ready to Use!**

**The single-file AutoPPT agent is now ready!**

**Just run:**
```bash
python autoppt_single.py "Create a 5-slide presentation on YOUR_TOPIC"
```

**No setup, no servers, no complexity - just one command and you get a professional PowerPoint presentation!** 🚀
