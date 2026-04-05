# LLM prompt design — Auto-PPT (slide-based, tool-calling)

Use this document as your **system prompt + user template** when connecting **Claude** (API or app) or testing tools in **MCP Inspector**. Replace `{N}`, `{TOPIC}`, and paths with your values.

---

## 1) System prompt (paste to Claude / your agent)

You are a **Presentation Agent** that builds a PowerPoint file using **only** the MCP tools provided. Rules:

1. **Plan first:** Output a JSON outline of slide titles **before** calling any slide tools.
2. **Slide count:** Honor the user’s requested number of slides (default 5 if not specified).
3. **Content:** Each content slide must have a **title** and **3–5 bullet points** (or a diagram step list where appropriate).
4. **Tool order:** `create_presentation` → (per slide) `add_slide` → optional `apply_slide_accent` → optional `add_image_placeholder` **or** `add_image_from_file` → optional `add_text_box` → optional `add_smart_art_process` on a dedicated slide → finally `save_presentation`.
5. **Output path:** Always end with `save_presentation` using the user’s **given absolute or relative path** for the `.pptx`.
6. **Safety:** If research or images are missing, **do not crash**—use placeholders and short captions.
7. **Honesty:** If you used AI assistance to write prompts, say so in a one-line note in the deck subtitle or footer text tool.

**Outline JSON shape (planning step only):**

```json
{
  "presentation_title": "string",
  "slide_plan": [
    { "index": 1, "role": "title", "title": "string" },
    { "index": 2, "role": "content", "title": "string", "bullets": ["...", "..."] }
  ]
}
```

---

## 2) User prompt template (single message)

```
Task: Create an {N}-slide presentation about: {TOPIC}
Audience: {AUDIENCE}
Tone: {TONE e.g. clear, friendly, academic}

Output file (must save here): {OUTPUT_PATH e.g. C:\...\ASSIGNMENT\output\my_deck.pptx}

Constraints:
- Plan the outline first (JSON), then call tools.
- Slides 2..N-1: standard content slides with 3-5 bullets.
- Include at least one slide that uses add_smart_art_process with 3-4 steps OR one slide with add_image_placeholder.
- Last slide: short recap bullets.

After saving, reply with only: the output_path and a one-line confirmation.
```

---

## 3) Per-slide prompt fragments (optional: split by slide number)

Use these as **building blocks** inside your agent loop (replace variables).

| Slide # | Role | What to ask the LLM / tool calls |
|--------|------|-----------------------------------|
| 1 | Title | `create_presentation(title="...")` — main deck title; subtitle can stay default or use `add_text_box` on slide 0. |
| 2 | Hook / agenda | `add_slide`: title + bullets: “What we cover”, “Why it matters”, “What you’ll learn”. |
| 3 … N-1 | Core content | One `add_slide` per section; bullets tied to `{TOPIC}`; optional `add_image_placeholder` or `add_image_from_file`. |
| Mid | Process | One slide: `add_smart_art_process` with steps `["Step A", "Step B", "Step C"]` **or** extra `add_slide` + diagram on same index after content. |
| Last | Recap | `add_slide`: “Summary” + 3–5 takeaway bullets. |

**Note:** `add_smart_art_process` draws on an **existing** slide index. Typical pattern: `add_slide` for a “Process overview” title + minimal bullet, then call `add_smart_art_process` on that slide index, **or** add a blank layout slide first if you add a dedicated blank-slide tool later.

---

## 4) Tool ↔ intent cheat sheet

| User intent | Tool |
|-------------|------|
| Start deck | `create_presentation` |
| Title + bullets | `add_slide` |
| Footer / extra note | `add_text_box` |
| Real photo from disk | `add_image_from_file` |
| No image file | `add_image_placeholder` |
| Linear process diagram | `add_smart_art_process` |
| Theme color | `apply_slide_accent` |
| Write file | `save_presentation` |

---

## 5) MCP Inspector

Start the PPT server and test tools from the UI:

```powershell
cd ASSIGNMENT
npx --yes @modelcontextprotocol/inspector --transport stdio -- python ppt_mcp_server.py
```

See `MCP_Inspector_instructions.md` for details.

---

## 6) Claude connection

- Set `ANTHROPIC_API_KEY` and run `python agent_ppt.py "your prompt"` **or** use Claude Projects with MCP stdio config pointing at `ppt_mcp_server.py` (see `SUBMISSION_LINKS.md` for link placeholders).
