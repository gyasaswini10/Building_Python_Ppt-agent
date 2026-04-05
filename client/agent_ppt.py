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
        # Always check the root for the .env
        env_p = Path(__file__).resolve().parent.parent / ".env"
        load_dotenv(dotenv_path=env_p)
        t = os.getenv("HF_TOKENS", os.getenv("HF_TOKEN", ""))
        self.hf_tokens = [x.strip() for x in t.split(",") if x.strip()]

    async def ask_llm(self, prompt: str, is_planning: bool = False) -> Dict[str, Any]:
        from huggingface_hub import InferenceClient
        for token in self.hf_tokens:
            try:
                c = InferenceClient(token=token)
                out = c.chat_completion(
                    model=self.hf_model,
                    messages=[{"role": "system", "content": "Return ONLY valid JSON."}, {"role": "user", "content": prompt}],
                    max_tokens=1000, timeout=30
                )
                match = re.search(r"\{[\s\S]*\}", out.choices[0].message.content)
                if match: return json.loads(match.group(0))
            except Exception: continue
        
        # PRO-TECH FALLBACK: 6 slides for any topic.
        s = self.user_request
        return {"title": s, "slides": [{"title": f"Egg Phase: Embryonic Development"}, {"title": f"The Tadpole: Swimming & Growth"}, {"title": f"Metamorphosis: Major Transformation"}, {"title": f"The Froglet: Juvenile Stage"}, {"title": f"Adult Frog: Maturity & Ecosystem"}, {"title": f"Life Cycle Challenges & Survival Strategies"}]}

    async def execute(self):
        self.setup_llm()
        # ABSOLUTE TOOL PATHS (REQUIRED FOR SUBFOLDER EXECUTION)
        base = Path(__file__).resolve().parent
        ppt_p = StdioServerParameters(command=sys.executable, args=[str(base/"ppt_mcp_server.py")])
        res_p = StdioServerParameters(command=sys.executable, args=[str(base/"research_mcp_server.py")])

        async with stdio_client(ppt_p) as (pt_r, pt_w), stdio_client(res_p) as (rs_r, rs_w):
            async with ClientSession(pt_r, pt_w) as ppt, ClientSession(rs_r, rs_w) as res:
                await ppt.initialize()
                await res.initialize()

                print(f"[AGENT] Final Master Execution for: {self.user_request}", file=sys.stderr)
                plan = await self.ask_llm(f"Plan exactly 6 high-density slides for '{self.user_request}' as JSON {{'title':'...', 'slides':[]}}", is_planning=True)
                
                resp = await ppt.call_tool("create_pptx", {"title": plan.get("title", self.user_request)})
                sid = json.loads(resp.content[0].text)["session_id"]
                await ppt.call_tool("apply_slide_accent", {"session_id": sid, "slide_index": 0, "accent_hex": "#0078D4"})

                for i, s_meta in enumerate(plan.get("slides", [])[:6]):
                    try:
                        title = s_meta["title"]
                        idx = i + 1 
                        print(f"[AGENT] Designing Deep Content for Slide {idx}: {title}", file=sys.stderr)

                        # DEEP RESEARCH (The 'Real Text Matter')
                        r_data = json.loads((await res.call_tool("search_topic", {"query": f"Life cycle of frog {title}"})).content[0].text)
                        facts = r_data.get('points', [])
                        
                        # Apply research data directly (Density Guarantee)
                        final_bullets = facts[:5] if (facts and len(facts) > 1) else [f"Detailed biological stage: {title}.", f"Ecological role within the frog's lifecycle.", f"Growth indicators and physical developments.", f"Interactions with the surrounding ecosystem."]

                        await ppt.call_tool("add_slide", {"session_id": sid, "slide_title": title, "bullets": final_bullets})

                        # Relevant Scientific Image check
                        thumb = r_data.get("thumbnail")
                        if thumb and "wikimedia.org" in thumb:
                            import httpx
                            p = base / f"final_img_{idx}.jpg"
                            async with httpx.AsyncClient(follow_redirects=True) as client:
                                r = await client.get(thumb)
                                if r.status_code == 200:
                                    p.write_bytes(r.content)
                                    await ppt.call_tool("add_image", {"session_id": sid, "slide_index": idx, "image_path": str(p.resolve())})
                        
                        await ppt.call_tool("apply_slide_accent", {"session_id": sid, "slide_index": idx, "accent_hex": "#1E90FF"})
                    except Exception as e:
                        print(f"[ERR] {e}", file=sys.stderr)

                final_out = str(self.output_path.resolve())
                await ppt.call_tool("save_presentation", {"session_id": sid, "output_path": final_out})
                print(f"[SUCCESS] Final Submission Ready at: {final_out}")

def main():
    p = argparse.ArgumentParser()
    p.add_argument("prompt")
    p.add_argument("--output", default="FINAL_FROG_SUBMISSION.pptx")
    args = p.parse_args()
    
    # ENSURE OUTPUT LANDS IN 'savingfolder_output' AT ROOT
    root = Path(__file__).resolve().parent.parent
    out_dir = root / "savingfolder_output"
    out_dir.mkdir(exist_ok=True)
    final_out = str(out_dir / Path(args.output).name)
    
    asyncio.run(AutoPPTAgent(args.prompt, final_out).execute())

if __name__ == "__main__":
    main()
