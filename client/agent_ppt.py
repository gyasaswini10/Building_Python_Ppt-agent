import asyncio
import json
import os
import re
import sys
import argparse
import httpx
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional

try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
except ImportError:
    print("FATAL: MCP SDK missing.", file=sys.stderr)

class AutoPPTAgent:
    @staticmethod
    def _slide_fact_window(pool: List[str], slide_index: int, width: int = 6) -> List[str]:
        """Rotate through a shared research pool so slides are not identical when the pool is long."""
        if len(pool) <= width:
            return pool[:width]
        span = len(pool) - width + 1
        start = (slide_index - 1) % span
        return pool[start : start + width]

    def __init__(self, user_request: str, output_path: str):
        self.user_request = user_request
        self.output_path = Path(output_path)
        self.hf_tokens = []
        self.models = ["Qwen/Qwen2.5-72B-Instruct", "mistralai/Mistral-7B-Instruct-v0.3", "meta-llama/Llama-3.2-3B-Instruct"]

    def setup_llm(self):
        from dotenv import load_dotenv
        env_p = Path(__file__).resolve().parent.parent / ".env"
        load_dotenv(dotenv_path=env_p)
        t = os.getenv("HF_TOKENS", os.getenv("HF_TOKEN", ""))
        self.hf_tokens = [x.strip() for x in t.split(",") if x.strip()]

    async def ask_llm(self, prompt: str) -> Dict[str, Any]:
        # 🔗 AI BRAIN CHAIN (Multi-token rotation)
        for model in self.models:
            for token in self.hf_tokens:
                try:
                    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
                    wrapped = (
                        "You output a single JSON object only, no markdown, no explanation.\n"
                        f"Task: {prompt}\n"
                        'Schema: {"bullets":["string", ...]} with exactly 6 strings.'
                    )
                    payload = {
                        "inputs": wrapped,
                        "parameters": {"max_new_tokens": 900, "return_full_text": False},
                    }
                    url = f"https://api-inference.huggingface.co/models/{model}"
                    async with httpx.AsyncClient(timeout=60) as client:
                        r = await client.post(url, headers=headers, json=payload)
                        if r.status_code == 200:
                            body = r.json()
                            txt = ""
                            if isinstance(body, list) and body:
                                txt = body[0].get("generated_text", "") or ""
                            elif isinstance(body, dict):
                                txt = body.get("generated_text", "") or ""
                            match = re.search(r"\{[\s\S]*\}", txt)
                            if match:
                                return json.loads(match.group(0))
                except Exception:
                    continue
        return {}

    async def execute(self):
        self.setup_llm()
        base = Path(__file__).resolve().parent
        ppt_p = StdioServerParameters(command=sys.executable, args=[str(base/"ppt_mcp_server.py")])
        res_p = StdioServerParameters(command=sys.executable, args=[str(base/"research_mcp_server.py")])

        async with stdio_client(ppt_p) as (pt_r, pt_w), stdio_client(res_p) as (rs_r, rs_w):
            async with ClientSession(pt_r, pt_w) as ppt, ClientSession(rs_r, rs_w) as res:
                await ppt.initialize(); await res.initialize()

                subj = re.sub(
                    r"(?i)^\s*create\s+(a\s+)?(\d+-slide\s+)?presentation\s+(on|about)\s*",
                    "",
                    self.user_request,
                ).strip() or self.user_request.strip()
                print(f"[AGENT] Designing Professional Research Deck: {subj}")

                # 🧠 PLAN: Scientific Hierarchy
                plan = {"title": f"The Science and Evolution of {subj}", "slides": [{"title": "Origins and Taxonomy"},{"title": "Physiological & Structural Features"},{"title": "Biological Growth & Lifecycle"},{"title": "Ecological & Environmental Roles"},{"title": "Industrial & Societal Impact"},{"title": "Future Research & Conservation Directions"}]}
                
                resp = await ppt.call_tool("create_pptx", {"title": plan["title"]})
                sid = json.loads(resp.content[0].text)["session_id"]

                for i, s_m in enumerate(plan["slides"]):
                    title = s_m["title"]; idx = i + 1
                    print(f"[AGENT] Generating Expert Content for Slide {idx}: {title}")

                    # 🔍 1. WIKI-RESEARCH (topic-based title so en.wikipedia resolves a real article)
                    r_raw = await res.call_tool("search_topic", {"query": f"{subj} {title} facts biology"})
                    raw_points = json.loads(r_raw.content[0].text).get("points", [])
                    pool = [str(x).strip() for x in raw_points if str(x).strip()]
                    facts = self._slide_fact_window(pool, idx, 6)
                    facts_snip = json.dumps(facts[:10])[:1200]

                    # 🧠 2. AI REFINEMENT — 6 bullets grounded in research (HF free tier: huggingface.co/settings/tokens)
                    ai_gen = await self.ask_llm(
                        f"Presentation topic: {subj!r}. Slide heading: {title!r}.\n"
                        f"Research bullets (may be partial; stay faithful): {facts_snip}\n"
                        "Write exactly 6 concise bullet points for this slide only. "
                        "Each bullet one sentence, factual, on-topic for the heading. "
                        "Do not mix unrelated domains (e.g. do not use animal physiology for a laptop). "
                        "Prefer paraphrasing the research bullets when they apply; otherwise state accurate general knowledge about the topic."
                    )
                    bullets = ai_gen.get("bullets", [])
                    if isinstance(bullets, list):
                        bullets = [str(b).strip() for b in bullets if str(b).strip()]
                    else:
                        bullets = []

                    # 🛡️ 3. Pad or fall back to Wikipedia-derived lines (always 6)
                    seen = {b.lower() for b in bullets}
                    if len(bullets) < 6 and facts:
                        for f in facts:
                            if len(bullets) >= 6:
                                break
                            if f.lower() not in seen:
                                bullets.append(f)
                                seen.add(f.lower())
                    if len(bullets) < 6:
                        print(f"[AGENT] Padding slide {idx} to 6 bullets...")
                        for line in (
                            f"{subj}: context and background for “{title}”.",
                            f"Key definitions and main parts of {subj} relevant to this section.",
                            f"How “{title}” appears in concrete examples of {subj}.",
                            f"Trade-offs, limits, or common issues tied to {title}.",
                            f"Design, use, or impact of {subj} connected to this theme.",
                            f"Takeaway: why “{title}” matters for understanding {subj}.",
                        ):
                            if len(bullets) >= 6:
                                break
                            if line.lower() not in seen:
                                bullets.append(line)
                                seen.add(line.lower())

                    await ppt.call_tool("add_slide", {"session_id": sid, "slide_title": title, "bullets": bullets[:6]})

                    # Thumbnail handler
                    thumb = json.loads(r_raw.content[0].text).get("thumbnail")
                    if thumb and "wikimedia.org" in thumb:
                        try:
                            async with httpx.AsyncClient(follow_redirects=True) as client:
                                r = await client.get(thumb)
                                if r.status_code == 200:
                                    p = base / f"img_{idx}.jpg"; p.write_bytes(r.content)
                                    await ppt.call_tool("add_image", {"session_id": sid, "slide_index": idx, "image_path": str(p.resolve())})
                        except: pass

                final_out = str(self.output_path.resolve())
                await ppt.call_tool("save_presentation", {"session_id": sid, "output_path": final_out})
                print(f"[SUCCESS] Expert Presentation Finalized: {final_out}")

def main():
    p = argparse.ArgumentParser(); p.add_argument("prompt"); p.add_argument("--output", default="FINAL.pptx"); args = p.parse_args()
    root = Path(__file__).resolve().parent.parent; out_dir = root / "savingfolder_output"; out_dir.mkdir(exist_ok=True)
    f_path = out_dir / Path(args.output).name; c = 1
    while f_path.exists(): f_path = out_dir / f"{Path(args.output).stem}_v{c}{Path(args.output).suffix}"; c += 1
    asyncio.run(AutoPPTAgent(args.prompt, str(f_path.resolve())).execute())

if __name__ == "__main__": main()
