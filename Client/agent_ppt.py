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
    print("WARNING: MCP SDK missing. Some features may not work.", file=sys.stderr)

NUM_SLIDE_BULLETS = 5

class AutonomousPresenter:
    """
    Modular Class to encapsulate the entire presentation generation lifecycle.
    Adapted for web integration with Flask backend.
    """
    
    _STOP = frozenset(
        "and the for with from their this that are was were has have been being "
        "into such each over also than then only both about under when what which "
        "while where there these those they them very much some more most other "
        "your can may not its our out any all per via".split()
    )

    @staticmethod
    def _words(s: str) -> set[str]:
        """Simple tokenizer that drops punctuation and noise words"""
        return {w for w in re.findall(r"[a-z]{3,}", s.lower()) if w not in AutonomousPresenter._STOP}

    @staticmethod
    def _slide_theme_keywords(title: str) -> set[str]:
        """Expands conceptual keywords based on the specific slide header"""
        t = title.lower()
        base = AutonomousPresenter._words(title)
        extra: set[str] = set()
        
        if "future" in t or "conservation" in t or "research" in t:
            extra.update(
                """conservation sustainable sustainability biodiversity climate wild preserve protect
                restoration threat endangered habitat genetic breeding organic pesticide yield resistance
                disease soil water seed variety trial initiative policy management stewardship resource
                emerging study innovation challenge goal priority funding cultivar land use waste carbon
                nitrogen ecosystem service monitor inventory survey field plot experiment""".split()
            )
        
        if "origin" in t or "taxonom" in t:
            extra.update(
                """species genus family domestic cultivar native introduced wild ancestor evolved
                historical classification name region lineage phylogeny subspecies variety breed
                discovery domestication ancestor fossil record earliest""".split()
            )
        
        if "physiological" in t or "structural" in t:
            extra.update(
                """structure cell tissue root leaf stem flower fruit skin chemical nutrient growth
                morphology anatomy physical tuber starch protein carbohydrate vitamin mineral compound
                metabolism photosynthesis respiration water vascular fiber hull peel flesh""".split()
            )
        
        if "lifecycle" in t or "growth" in t or "biological" in t:
            extra.update(
                """seed germinate mature harvest season develop stage life cycle reproduction
                pollination sprout vegetative flowering ripening dormancy juvenile adult senescence
                planting spacing irrigation ripen""".split()
            )
        
        return base | extra

    @staticmethod
    def bullet_matches_slide(subj: str, title: str, text: str) -> bool:
        """Determines if a candidate bullet point belongs on the current slide"""
        low = text.strip().lower()
        
        if len(low) < 12:
            return False
        
        if any(low.startswith(x) for x in ["related term:", "synonym:", "example:"]):
            return False
        
        if re.search(r"\blookit\b|hot tomato|pelt with", low):
            return False
        
        theme = AutonomousPresenter._slide_theme_keywords(title)
        if theme & AutonomousPresenter._words(low):
            return True
        return False

    async def _dictionary_bullets_direct(self, subj: str, title: str, limit: int = 8) -> List[str]:
        """Fallback logic: Uses the Free Dictionary API"""
        word = subj.lower().split()[0]
        try:
            from urllib.parse import quote
            url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{quote(word)}"
            async with httpx.AsyncClient(timeout=20.0) as client:
                r = await client.get(url)
            if r.status_code != 200: return []
            data = r.json()
            out = []
            for entry in data:
                for meaning in entry.get("meanings", []):
                    if meaning.get("partOfSpeech") == "noun":
                        for d in meaning.get("definitions", []):
                            line = d.get("definition", "")
                            if self.bullet_matches_slide(subj, title, line):
                                out.append(line)
            return out[:limit]
        except Exception:
            return []

    def __init__(self, user_request: str, output_path: str):
        """Constructor: Initializes instances with specific user intent and output destinations"""
        self.user_request = user_request
        self.output_path = Path(output_path)
        self.openrouter_keys = []
        self.hf_tokens = []
        self._failed_keys = set()

    def setup_llm(self):
        """Loads environment variables securely"""
        try:
            from dotenv import load_dotenv
            env_p = Path(__file__).resolve().parent.parent / ".env"
            load_dotenv(dotenv_path=env_p)
        except ImportError:
            print("Warning: python-dotenv not available, using environment variables only")
        
        raw_keys = os.getenv("OPENROUTER_KEYS", "") or os.getenv("OPENROUTER_API_KEY", "")
        self.openrouter_keys = [k.strip() for k in raw_keys.split(",") if k.strip()]
        
        hf_raw = os.getenv("HF_TOKENS", "") or os.getenv("HF_TOKEN", "")
        self.hf_tokens = [t.strip() for t in hf_raw.split(",") if t.strip()]

    async def ask_llm(self, prompt: str) -> Dict[str, Any]:
        """Orchestration logic for Model Fallback and Redundancy"""
        for key in self.openrouter_keys:
            if key in self._failed_keys: continue
            try:
                # Mock implementation for web compatibility
                # In production, this would make actual API calls
                return {"bullets": [f"AI-generated insight about: {prompt[:50]}...", "Professional analysis based on current research."]}
            except Exception:
                self._failed_keys.add(key)
        
        return {"bullets": ["Fallback research-based bullet point.", "Ensuring comprehensive content coverage."]}

    async def execute_web_mode(self, topic: str, custom_slides: List[Dict] = None) -> Dict[str, Any]:
        """
        Web-compatible execution mode that doesn't rely on MCP servers
        Returns structured data for the Flask backend
        """
        self.setup_llm()
        
        # Use custom slides if provided, otherwise generate standard structure
        if custom_slides:
            plan = {
                "title": f"Presentation on {topic}",
                "slides": custom_slides
            }
        else:
            plan = {
                "title": f"Scientific Breakdown of {topic}",
                "slides": [
                    {"title": "Origins and Taxonomy"},
                    {"title": "Physiological & Structural Features"},
                    {"title": "Biological Growth & Lifecycle"},
                    {"title": "Ecological & Environmental Roles"},
                    {"title": "Industrial & Societal Impact"},
                    {"title": "Future Research & Conservation"}
                ]
            }
        
        results = []
        
        for i, slide_info in enumerate(plan["slides"]):
            title = slide_info["title"]
            
            # Generate bullets using LLM or fallback
            if slide_info.get("bullets"):
                bullets = slide_info["bullets"][:5]
            else:
                model_res = await self.ask_llm(f"Generate 5 professional bullets regarding {title} for {topic}")
                bullets = model_res.get("bullets", [f"Key fact about {title}", f"Important information on {title}"])[:5]
            
            results.append({
                "slide_number": i + 1,
                "title": title,
                "bullets": bullets
            })
        
        return {
            "success": True,
            "presentation": {
                "title": plan["title"],
                "topic": topic,
                "slides": results
            }
        }

    async def execute(self):
        """
        The Main Agentic Loop Orchestrator (original MCP version)
        """
        self.setup_llm() 
        base = Path(__file__).resolve().parent 
        
        # Check if MCP servers are available
        ppt_server_path = base / "ppt_mcp_server.py"
        research_server_path = base / "research_mcp_server.py"
        
        if not ppt_server_path.exists() or not research_server_path.exists():
            print("MCP servers not found, falling back to web mode")
            return await self.execute_web_mode(self.user_request)
        
        try:
            ppt_p = StdioServerParameters(command=sys.executable, args=[str(ppt_server_path)])
            res_p = StdioServerParameters(command=sys.executable, args=[str(research_server_path)])

            async with stdio_client(ppt_p) as (pt_r, pt_w), stdio_client(res_p) as (rs_r, rs_w):
                async with ClientSession(pt_r, pt_w) as ppt, ClientSession(rs_r, rs_w) as res:
                    await ppt.initialize(); await res.initialize()

                    subj = self.user_request.split("on")[-1].strip()
                    
                    plan = {
                        "title": f"Scientific Breakdown of {subj}",
                        "slides": [
                            {"title": "Origins and Taxonomy"},
                            {"title": "Physiological & Structural Features"},
                            {"title": "Biological Growth & Lifecycle"},
                            {"title": "Ecological & Environmental Roles"},
                            {"title": "Industrial & Societal Impact"},
                            {"title": "Future Research & Conservation"}
                        ]
                    }
                    
                    resp = await ppt.call_tool("create_pptx", {"title": plan["title"]})
                    sid = json.loads(resp.content[0].text)["session_id"]

                    for i, s_m in enumerate(plan["slides"]):
                        title = s_m["title"]; idx = i + 1
                        print(f"[AGENT] Processing Slide {idx}: {title}")
                        
                        r_raw = await res.call_tool("search_topic", {"query": f"{subj} {title}"})
                        points = json.loads(r_raw.content[0].text).get("points", [])
                        
                        model_res = await self.ask_llm(f"Synthesize 5 professional bullets regarding {title} for {subj}")
                        bullets = model_res.get("bullets", points[:5]) 
                        
                        await ppt.call_tool("add_slide", {"session_id": sid, "slide_title": title, "bullets": bullets[:5]})
                    
                    final_out = str(self.output_path.resolve())
                    await ppt.call_tool("save_presentation", {"session_id": sid, "output_path": final_out})
                    print(f"[AGENT] SUCCESS: High-quality Presentation Finalized at {final_out}")
                    
                    return {
                        "success": True,
                        "output_path": final_out,
                        "session_id": sid
                    }
        except Exception as e:
            print(f"MCP execution failed, falling back to web mode: {e}")
            return await self.execute_web_mode(self.user_request)

def main():
    """CLI Primary Entrypoint"""
    p = argparse.ArgumentParser(description="Autonomous Presenter Agent CLI")
    p.add_argument("prompt")
    p.add_argument("--output", default="FINAL_PROJECT.pptx")
    args = p.parse_args()
    
    asyncio.run(AutonomousPresenter(args.prompt, args.output).execute())

if __name__ == "__main__":
    main()
