# 🧠 Reflection Document: The "Auto-PPT" Agent

### ❓ Where did your agent fail its first attempt?
In the initial development phase, the agent successfully retrieved data but failed at **thematic synthesis**. Specifically, when tasked with research-heavy slides like *Origins and Taxonomy*, it would often include irrelevant "lexicographical noise" (such as slang synonyms or dictionary-style verb definitions) that degraded the professional quality of the presentation.

**The Solution:** I refactored the agent to use a **Thematic Keyword Expansion** filter (`_slide_theme_keywords`). This ensured that every bullet point fetched from the web was cross-referenced against a conceptual map of relevant terms before being "allowed" onto the slide. This represents an "agentic loop" that validates its own research quality.

### ❓ What intermediate features were explored but sidelined?
I successfully implemented an **Image Integration Sync** for deep asset management. Evidence of this work can be found in the `savingfolder_output` directory:

```text
    Directory: C:\Users\gyasu\Desktop\CAlibo 
    noww\ASSIGNMENT\savingfolder_output

Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
d-----        05-04-2026  10:27 PM                agent_assets       
d-----        05-04-2026  10:27 PM                genearted
-a----        05-04-2026  10:27 PM         279277 FINAL_FROG_REPORT.pptx
```
Although I successfully generated high-accuracy reports (like **FINAL_FROG_REPORT.pptx (279KB)**) with local asset buffers, the final coordination for research-backed image placement was sidelined due to strict time constraints.

### ❓ How is the system made robust against API limits?
To ensure the agent remains fully autonomous, I implemented **HuggingFace Key Rotation**. The system handles multiple tokens that are rotated dynamically based on availability and rate limits (429 errors), ensuring non-stop "Brain" operation for long research sessions.

### ❓ How did MCP prevent you from writing hardcoded scripts?
The **Model Context Protocol (MCP)** was the single most important architectural constraint in this project.
*   **Separation of Concerns:** MCP made it impossible to hardcode the `python-pptx` library directly into the main agent script. Instead, I had to develop a standalone **PPT MCP Server** that defined clear, reusable tool boundaries.
*   **Standardized Interfacing:** Because tools like `add_slide` and `search_topic` had to be requested over the protocol, the agent became a true "orchestrator" rather than a monolithic script.
*   **Scalability:** If I want to change the PowerPoint theme or the research source (e.g., from Wikipedia to a paid API), I only need to modify the server file. The agent's core "brain" remains untouched, fulfilling the "Mastering Assignments" requirement for modular coding and professional design.
