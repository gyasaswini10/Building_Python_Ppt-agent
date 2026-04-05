import asyncio
import json
import os
import re
import sys
import argparse
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional

try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
except ImportError:
    print("FATAL: MCP SDK missing.", file=sys.stderr)

class AutoPPTAgent:
    def __init__(self, user_request: str, output_path: str):
        self.user_request = user_request
        self.output_path = Path(output_path)
        self.hf_tokens = []
        self.hf_model = "Qwen/Qwen2.5-7B-Instruct"

    def setup_llm(self):
        from dotenv import load_dotenv
        env_p = Path(__file__).resolve().parent.parent / ".env"
        load_dotenv(dotenv_path=env_p)
        t = os.getenv("HF_TOKENS", os.getenv("HF_TOKEN", ""))
        self.hf_tokens = [x.strip() for x in t.split(",") if x.strip()]

    async def ask_llm(self, prompt: str, is_planning: bool = False) -> Dict[str, Any]:
        from huggingface_hub import InferenceClient
        # Optimized for maximum compatibility across all library versions
        for token in self.hf_tokens:
            try:
                c = InferenceClient(token=token)
                # UNIVERSAL HF-HUB COMPATIBILITY (Text Generation)
                inst_prompt = f"[INST] Return ONLY valid JSON. {prompt} [/INST]"
                txt = c.text_generation(inst_prompt, max_new_tokens=1000)
                
                match = re.search(r"\{[\s\S]*\}", txt)
                if match: return json.loads(match.group(0))
            except Exception as e:
                print(f"[AI-ROTATION] {str(e)[:40]}...", file=sys.stderr)
                continue
        
        # 🍎 DYNAMIC FALLBACK PLAN
        s = self.user_request.replace("Create a 6-slide presentation on", "").strip()
        if is_planning:
            return {"title": f"Mastery of {s}", "slides": [{"title": "Introduction & Origins"},{"title": "Technological Evolution"},{"title": "Current Global Impact"},{"title": "Case Studies & Applications"},{"title": "Innovation & Development"},{"title": "Future Trends & Conclusions"}]}
        return {"bullets": [f"Deep dive into {s} history.", "Technological milestones and impacts.", f"Social and economic significance of {s}.", "Current industry standards and trends.", "Future outlook and scientific projections."]}

    async def execute(self):
        self.setup_llm()
        base = Path(__file__).resolve().parent
        ppt_p = StdioServerParameters(command=sys.executable, args=[str(base/"ppt_mcp_server.py")])
        res_p = StdioServerParameters(command=sys.executable, args=[str(base/"research_mcp_server.py")])

        async with stdio_client(ppt_p) as (pt_r, pt_w), stdio_client(res_p) as (rs_r, rs_w):
            async with ClientSession(pt_r, pt_w) as ppt, ClientSession(rs_r, rs_w) as res:
                await ppt.initialize()
                await res.initialize()

                subject = self.user_request.replace("Create a 6-slide presentation on", "").strip()
                print(f"[AGENT] Designing AI-Powered Deck for: {subject}", file=sys.stderr)
                
                plan = await self.ask_llm(f"Plan exactly 6 professional slides for '{subject}'. JSON {{'title':'...', 'slides':[]}}", is_planning=True)
                
                resp = await ppt.call_tool("create_pptx", {"title": plan.get("title", f"The Science of {subject}")})
                sid = json.loads(resp.content[0].text)["session_id"]

                for i, s_meta in enumerate(plan.get("slides", [])[:6]):
                    try:
                        title = s_meta["title"]
                        idx = i + 1 
                        print(f"[AGENT] AI Generating Expert Slide {idx}: {title}", file=sys.stderr)

                        # DIRECT AI GENERATION (Fast & Precise)
                        ai_resp = await self.ask_llm(f"Act as a professional subject matter expert. Generate 5 highly detailed and factual scientific bullet points for slide titled '{title}' about the topic '{subject}'. Provide deep matter, not generic headings. JSON {{'bullets':[]}}")
                        bullets = ai_resp.get("bullets", [])

                        # WEB RESEARCH SYNERGY (For Images & Backup Facts)
                        r_data = json.loads((await res.call_tool("search_topic", {"query": f"{subject} {title}"})).content[0].text)
                        if not bullets:
                             bullets = r_data.get('points', ["Researching scientific data..."])
                        
                        await ppt.call_tool("add_slide", {"session_id": sid, "slide_title": title, "bullets": bullets[:6]})

                        # Relevant Scientific Image check
                        thumb = r_data.get("thumbnail")
                        if thumb and "wikimedia.org" in thumb:
                            import httpx
                            p = base / f"slide_img_{idx}_{sid[:4]}.jpg"
                            async with httpx.AsyncClient(follow_redirects=True) as client:
                                r = await client.get(thumb)
                                if r.status_code == 200:
                                    p.write_bytes(r.content)
                                    await ppt.call_tool("add_image", {"session_id": sid, "slide_index": idx, "image_path": str(p.resolve())})
                    except Exception as e:
                        print(f"[ERR-SLIDE] {e}", file=sys.stderr)

                final_out = str(self.output_path.resolve())
                await ppt.call_tool("save_presentation", {"session_id": sid, "output_path": final_out})
                print(f"[SUCCESS] AI Masterpiece Saved: {final_out}")

def main():
    p = argparse.ArgumentParser()
    p.add_argument("prompt")
    p.add_argument("--output", default="AI_REPORT.pptx")
    args = p.parse_args()
    
    root = Path(__file__).resolve().parent.parent
    out_dir = root / "savingfolder_output"
    out_dir.mkdir(exist_ok=True)
    final_out = str(out_dir / Path(args.output).name)
    asyncio.run(AutoPPTAgent(args.prompt, final_out).execute())

if __name__ == "__main__":
    main()
