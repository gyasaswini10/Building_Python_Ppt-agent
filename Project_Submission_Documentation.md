# 📜 Project: The "Auto-PPT" Agent - Technical Documentation
## **Autonomous Presentation Agent (Modular Implementation)**

**Developer:** YASASWINI  
**Course:** AI Agents & MCP Architecture  
**Objective:** To design and implement a functional, modular agent that coordinates multiple MCP servers to autonomously research and generate professional PowerPoint presentations based on a user's single-sentence prompt.

---

## 🚀 Project Overview
The "Auto-PPT" Agent is an agentic system that follows a structured loop to build scientifically accurate presentations. By leveraging the **Model Context Protocol (MCP)**, the system separates cognitive tasks (Research and Planning) from execution tasks (PowerPoint generation).

### **Key Technical Features:**
- **Dynamic Research Loop:** Uses the Research MCP server to fetch encyclopedia-grade facts from Wikipedia and safe-hallucination fallbacks from Dictionary APIs.
- **Agentic Slide Planning:** Before writing, the agent establishes a 6-slide thematic hierarchy (Taxonomy, Physiology, Lifecycle, etc.) to ensure logical narrative flow.
- **Modular Decoupling:** Separates the core agent brain from the tool servers, allowing for independent scaling and maintenance of research or design logic.
- **Professional Aesthetics:** Automatically applies a Midnight Navy and Gold theme with precise alignment and designer ribbons.

---

## 📂 Modular System Workflow: How it Works

The system architecture is distributed across three specialized files in the `Modular code/` directory:

### 1. `agent_ppt.py` (The Orchestrator / Brain)
- **Primary Role:** Manages the high-level logic, API fallbacks, and tool coordination.
- **Workflow:**
    - **Stage 1 (Initialization):** Handshakes with both MCP servers using async standard IO.
    - **Stage 2 (Planning):** Analyzes the user prompt and generates a scientific slide hierarchy.
    - **Stage 3 (Synthesis):** Iterates through slides, requesting filtered facts from the sensor and directing the construction of layouts.

### 2. `ppt_mcp_server.py` (The Design Engine / Hands)
- **Primary Role:** Handles all PowerPoint manipulation and visual formatting.
- **Workflow:**
    - Manages multi-session in-memory presentation states using `python-pptx`.
    - Implements professional layout templates with custom font styling and color-accurate themes.
    - Executes precise shape placement for bullet points and decorative UI elements.

### 3. `research_mcp_server.py` (The Research Engine / Senses)
- **Primary Role:** Queries external APIs for topic-specific scientific data.
- **Workflow:**
    - Sanitizes research queries to optimize Wikipedia search accuracy.
    - Ranks and filters sentences to ensure thematic relevance to specific slide headings.
    - Provides a redundancy layer using Dictionary APIs to ensure robustness if the primary source fails.

---

## 🛠️ Assignment Technical Checklist
| Feature | Technical Implementation |
| :--- | :--- |
| **MCP Integration** | Fully implemented using Stdio Transport across three modular files. |
| **Agentic Loop** | Uses a 6-stage scientific planning strategy before fetching content. |
| **Content Generation** | Each slide contains 5 strictly-filtered, research-backed bullet points. |
| **Image Handling** | Automatically embeds topical images when available in source metadata. |
| **Error Handling** | redundant search paths and Dictionary-based fallback mechanisms ensure the system never crashes. |

---
**Built by YASASWINI**
