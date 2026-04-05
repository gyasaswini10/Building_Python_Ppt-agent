demo vedio link : https://drive.google.com/file/d/1JfxPmNVy4kLWcd53rKCmejVOCKFKGTx5/view?usp=sharing

# ✨ Autonomous Scientific Presentation System

High-accuracy generation of research-backed presentations using multi-layered automation and modular architecture.

---

## **1. Project Overview**
This repository provides an automated engine for scientific visualization. The system is engineered for modularity, separating fact-retrieval from design logic to ensure consistent slide quality and data integrity.

## **2. Key Project Assets**

### **System Logic: `Build_Agent.ipynb`**
The primary entry point for managing the automated workflow.
- **Modularity**: Implements encapsulated classes for design and orchestration.
- **Transparency**: Detailed line-by-line code documentation for maintenance and clarity.
- **Theming**: Integrated high-end dark aesthetics with automated scientific hierarchies.

### **Documentation Layer: `Project_Submission_Documentation.md`**
Direct technical documentation describing the system's modular architecture, stage-based lifecycle, and technical requirements.

### **Analysis Layer: `reflection.md`**
Critical reflection addressing initial failure points (thematic relevance) and the architectural constraints enforced by the MCP protocol.

### **Processing Engine: `/Modular code`**
The core processing layer is separated into specialized service modules:
- **`agent_ppt.py`**: The system's primary orchestrator.
- **`ppt_mcp_server.py`**: Dedicated server for PowerPoint structure and themes.
- **`research_mcp_server.py`**: Specialized server for information retrieval (Wikipedia/Dictionary).

### **Walkthrough: `DEMO_VEDIO_PPt_agent.mp4`**
A visual screen-recording of the system in action:
1. Terminal command-line execution.
2. Live slide generation and real-time research synthesis.
3. Final PowerPoint output showcasing precise scientific alignment.

---

## **3. Structural Hierarchy (6-Slide Standard)**
Every presentation follows a standard scientific curriculum:
1. **Origins & Taxonomy**: Historical context and nomenclature.
2. **Physiological & Structural Features**: Biological morphology and anatomy.
3. **Biological Growth & Lifecycle**: Reproduction and lifecycle phases.
4. **Ecological & Environmental Roles**: Habitat impact and ecosystem role.
5. **Industrial & Societal Impact**: Commercial, nutritional, and social relevance.
6. **Future Research & Conservation**: Future prospects and sustainability outlook.

---

## **4. Technical Specification**
- **Modular Design**: Complete separation of tool discovery and tool execution.
- **Fact Integrity**: Uses validated REST APIs to minimize data hallucinations.
- **Design Stability**: Uses `python-pptx` with predefined professional color tokens.
