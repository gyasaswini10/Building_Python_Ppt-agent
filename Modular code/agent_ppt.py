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

NUM_SLIDE_BULLETS = 5


class AutonomousPresenter:
    _STOP = frozenset(
        "and the for with from their this that are was were has have been being "
        "into such each over also than then only both about under when what which "
        "while where there these those they them very much some more most other "
        "your can may not its our out any all per via".split()
    )

    @staticmethod
    def _words(s: str) -> set[str]:
        return {w for w in re.findall(r"[a-z]{3,}", s.lower()) if w not in AutonomousPresenter._STOP}

    @staticmethod
    def _slide_theme_keywords(title: str) -> set[str]:
        """Heading tokens plus theme words so bullets can match substance, not only the title string."""
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
        if "ecological" in t or "environmental" in t:
            extra.update(
                """ecosystem soil climate rain drought pest pollinator rotation companion habitat
                nitrogen carbon erosion runoff biodiversity invasive companion crop mulch compost
                symbiosis decomposition nutrient leaching salinity acidity temperature frost""".split()
            )
        if "industrial" in t or "societal" in t:
            extra.update(
                """industry market farm export food consume nutrition economic trade production
                process product supply chain retail consumer factory processing packaging employment
                regulation standard safety export import commodity price subsidy""".split()
            )
        return base | extra

    @staticmethod
    def _subject_in_bullet(subj: str, bullet_low: str) -> bool:
        s = re.sub(r"[^a-z0-9 ]+", " ", subj.lower()).strip()
        if len(s) >= 4 and s in bullet_low:
            return True
        words = re.findall(r"[a-z]+", s)
        if not words:
            return False
        min_len = 3 if len(words) == 1 and len(words[0]) <= 4 else 4
        return any(len(w) >= min_len and w in bullet_low for w in words)

    @staticmethod
    def bullet_matches_slide(subj: str, title: str, text: str) -> bool:
        """Drop lines unrelated to this slide heading (e.g. slang synonyms on a research slide)."""
        low = text.strip().lower()
        if len(low) < 12:
            return False
        if low.startswith("related term:") or low.startswith("synonym:"):
            return False
        if low.startswith("example:"):
            return False
        if re.match(r"^\(verb\)", low):
            return False
        if re.match(r"^\(noun\)\s+a shade of", low) or re.match(r"^\(noun\)\s+the colour of", low):
            return False
        if re.search(r"\blookit\b|hot tomato|pelt with", low):
            return False
        if "context and background for" in low or "key definitions and main parts" in low:
            return False
        theme = AutonomousPresenter._slide_theme_keywords(title)
        if theme & AutonomousPresenter._words(low):
            return True
        if AutonomousPresenter._subject_in_bullet(subj, low):
            return True
        return False

    @staticmethod
    def _llm_bullet_ok(text: str) -> bool:
        """Light check for model output — do not strip all bullets (avoids empty slides)."""
        t = (text or "").strip()
        if len(t) < 12:
            return False
        low = t.lower()
        if low.startswith("related term:") or low.startswith("synonym:") or low.startswith("example:"):
            return False
        if re.search(r"\blookit\b|hot tomato|pelt with", low):
            return False
        return True

    @staticmethod
    def _garbage_line(low: str) -> bool:
        """True = skip this line (slang / junk)."""
        if len(low) < 10:
            return True
        if low.startswith("related term:"):
            return True
        if re.search(r"\blookit\b|hot tomato|pelt with", low):
            return True
        return False

    async def _dictionary_bullets_direct(self, subj: str, title: str, limit: int = 8) -> List[str]:
        """
        Dictionary lines only if they match the slide heading — skip lexicographic fluff
        (e.g. 'pleasant smell' on a 'Biological Growth & Lifecycle' slide).
        """
        slug = re.sub(r"[^a-zA-Z0-9 ]+", " ", (subj or "").lower()).strip().split()
        if not slug:
            return []
        word = slug[0]
        if len(word) < 2:
            return []
        try:
            from urllib.parse import quote

            url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{quote(word, safe='')}"
            async with httpx.AsyncClient(timeout=20.0) as client:
                r = await client.get(url)
            if r.status_code != 200:
                return []
            data = r.json()
            if not isinstance(data, list):
                return []
            out: List[str] = []
            seen: set[str] = set()
            for entry in data:
                for meaning in entry.get("meanings", []) or []:
                    if (meaning.get("partOfSpeech") or "").lower() != "noun":
                        continue
                    for d in meaning.get("definitions", []) or []:
                        defn = (d.get("definition") or "").strip()
                        if len(defn) < 20:
                            continue
                        low = defn.lower()
                        if self._garbage_line(low):
                            continue
                        if " to " in defn[:8].lower() or defn.lower().startswith("to "):
                            continue
                        if low in seen:
                            continue
                        line = defn[0].upper() + defn[1:] if defn else defn
                        if not line.endswith("."):
                            line += "."
                        if not self.bullet_matches_slide(subj, title, line):
                            continue
                        seen.add(low)
                        out.append(line)
                        if len(out) >= limit:
                            return out
            return out
        except Exception:
            return []

    @staticmethod
    def _extra_wikipedia_queries(subj: str, title: str) -> List[str]:
        """Topic + heading cues for a second-chance article extract (dynamic, not hardcoded facts)."""
        t = (title or "").lower()
        tails: List[str] = []
        if "origin" in t or "taxonom" in t:
            tails.extend(["taxonomy", "history", "species"])
        if "physiological" in t or "structural" in t:
            tails.extend(["anatomy", "composition", "chemistry"])
        if "lifecycle" in t or ("growth" in t and "biological" in t):
            tails.extend(["cultivation", "production", "life cycle"])
        if "ecological" in t or "environmental" in t:
            tails.extend(["environment", "agriculture", "ecology"])
        if "industrial" in t or "societal" in t:
            tails.extend(["industry", "market", "economy"])
        if "future" in t or "conservation" in t or "research" in t:
            tails.extend(["research", "sustainability", "conservation"])
        seen_q: set[str] = set()
        out: List[str] = []
        base = subj.strip()
        for tail in tails:
            q = f"{base} {tail}".strip()
            if q.lower() not in seen_q:
                seen_q.add(q.lower())
                out.append(q)
        return out[:5]

    async def _finalize_bullets(
        self,
        subj: str,
        title: str,
        bullets: List[str],
        pool: List[str],
        facts: List[str],
        res: Any,
        idx: int,
    ) -> List[str]:
        """Fill to NUM_SLIDE_BULLETS using progressively looser sources (avoids empty slides)."""
        out = [str(b).strip() for b in bullets if str(b).strip()]
        seen = {b.lower() for b in out}
        n = NUM_SLIDE_BULLETS

        def take(lines: List[str], strict_slide: bool) -> None:
            for line in lines:
                if len(out) >= n:
                    return
                s = str(line).strip()
                if not s or self._garbage_line(s.lower()):
                    continue
                low = s.lower()
                if low in seen:
                    continue
                if strict_slide and not self.bullet_matches_slide(subj, title, s):
                    continue
                out.append(s)
                seen.add(low)

        take(facts, True)
        take(pool, False)
        take(self._slide_fact_window(pool, idx, max(n, 8)), False)
        if len(out) < n:
            print(f"[AGENT] Broad web fetch (no slide filter) for slide {idx}...")
            r0 = await res.call_tool("search_topic", {"query": subj, "slide_title": "", "supplement": False})
            broad = json.loads(r0.content[0].text).get("points", [])
            take([str(x).strip() for x in broad if str(x).strip()], False)
        if len(out) < n:
            r_sup = await res.call_tool(
                "search_topic",
                {"query": f"{subj} {title}", "slide_title": title, "supplement": True},
            )
            take([str(x).strip() for x in json.loads(r_sup.content[0].text).get("points", [])], False)
        if len(out) < n:
            for extra_q in self._extra_wikipedia_queries(subj, title):
                if len(out) >= n:
                    break
                print(f"[AGENT] Extra Wikipedia query for slide {idx}: {extra_q!r}")
                rx = await res.call_tool(
                    "search_topic",
                    {"query": extra_q, "slide_title": title, "supplement": False},
                )
                take([str(x).strip() for x in json.loads(rx.content[0].text).get("points", [])], False)
        if len(out) < n:
            print(f"[AGENT] Dictionary fallback (slide-filtered) for slide {idx}...")
            take(await self._dictionary_bullets_direct(subj, title, limit=12), False)
        if len(out) < n:
            stem = (subj.strip() or "this topic").title()
            pad = [
                f"Summarize how “{title}” applies to {stem}: use one concrete example from industry or nature.",
                f"List two measurable traits or stages of {stem} that best illustrate “{title}”.",
                f"Compare {stem} with a related product or species; note one similarity and one difference.",
                f"Cite one challenge and one opportunity for {stem} under the theme “{title}”.",
                f"End with a question or statistic viewers should verify about {stem} and “{title}”.",
            ]
            pi = 0
            while len(out) < n:
                line = pad[pi % len(pad)]
                pi += 1
                if line.lower() in seen:
                    line = f"{stem} (point {len(out) + 1}): add a cited fact about “{title}” from Wikipedia or academic sources."
                out.append(line)
                seen.add(line.lower())
        return out[:n]

    @staticmethod
    def _slide_fact_window(pool: List[str], slide_index: int, width: int = 6) -> List[str]:
        """Rotate through a shared research pool so slides are not identical when the pool is long."""
        if len(pool) <= width:
            return pool[:width]
        span = len(pool) - width + 1
        start = (slide_index - 1) % span
        return pool[start : start + width]

    @staticmethod
    def _is_embeddable_image(data: bytes) -> bool:
        if not data or len(data) < 2048:
            return False
        return data[:2] == b"\xff\xd8" or data[:8] == b"\x89PNG\r\n\x1a\n"

    def __init__(self, user_request: str, output_path: str):
        self.user_request = user_request
        self.output_path = Path(output_path)
        self.openrouter_keys = []
        self.hf_tokens = []
        self._openrouter_round = 0
        self._hf_round = 0
        # Track failed keys to avoid retrying them too soon
        self._failed_openrouter_keys = {}  # key -> timestamp
        self._failed_hf_tokens = {}  # token -> timestamp
        # OpenRouter models for fast, accurate text generation (primary)
        self.openrouter_models = [
            "anthropic/claude-3-haiku",
            "openai/gpt-4o-mini", 
            "google/gemini-flash-1.5",
        ]
        # HuggingFace models (fallback)
        self.hf_models = [
            "meta-llama/Llama-3.2-3B-Instruct",
            "mistralai/Mistral-7B-Instruct-v0.3",
            "Qwen/Qwen2.5-72B-Instruct",
        ]

    def setup_llm(self):
        from dotenv import load_dotenv
        env_p = Path(__file__).resolve().parent.parent / ".env"
        load_dotenv(dotenv_path=env_p)
        
        # Setup OpenRouter keys - check multiple formats
        or_keys = []
        # Check individual numbered keys
        for i in range(1, 20):  # Check up to 20 keys
            key = os.getenv(f"OPENROUTER_API_KEY_{i}")
            if key and key.strip():
                or_keys.append(key.strip())
        # Check combined keys
        combined_keys = os.getenv("OPENROUTER_KEYS", os.getenv("OPENROUTER_KEY", ""))
        if combined_keys:
            or_keys.extend([x.strip() for x in combined_keys.split(",") if x.strip()])
        
        self.openrouter_keys = list(dict.fromkeys(or_keys))  # Remove duplicates
        
        # Setup HuggingFace tokens
        hf_tokens = os.getenv("HF_TOKENS", os.getenv("HF_TOKEN", ""))
        self.hf_tokens = [x.strip() for x in hf_tokens.split(",") if x.strip()]
        
        print(f"[DEBUG] Loaded {len(self.openrouter_keys)} OpenRouter keys and {len(self.hf_tokens)} HF tokens", file=sys.stderr)

    def _get_available_openrouter_keys(self) -> List[str]:
        """Get OpenRouter keys that haven't failed recently."""
        import time
        current_time = time.time()
        available_keys = []
        
        for key in self.openrouter_keys:
            # Skip keys that failed in the last 5 minutes (300 seconds)
            if key in self._failed_openrouter_keys:
                if current_time - self._failed_openrouter_keys[key] < 300:
                    continue
                else:
                    # Remove from failed list after cooldown
                    del self._failed_openrouter_keys[key]
            available_keys.append(key)
        
        return available_keys

    def _get_available_hf_tokens(self) -> List[str]:
        """Get HuggingFace tokens that haven't failed recently."""
        import time
        current_time = time.time()
        available_tokens = []
        
        for token in self.hf_tokens:
            # Skip tokens that failed in the last 5 minutes (300 seconds)
            if token in self._failed_hf_tokens:
                if current_time - self._failed_hf_tokens[token] < 300:
                    continue
                else:
                    # Remove from failed list after cooldown
                    del self._failed_hf_tokens[token]
            available_tokens.append(token)
        
        return available_tokens

    async def ask_llm(self, prompt: str) -> Dict[str, Any]:
        """Try OpenRouter first, then HuggingFace as fallback."""
        
        # Try OpenRouter first (primary)
        if self.openrouter_keys:
            print("[DEBUG] Trying OpenRouter API...", file=sys.stderr)
            result = await self._try_openrouter(prompt)
            if result:
                print("[DEBUG] OpenRouter succeeded!", file=sys.stderr)
                return result
            else:
                print("[DEBUG] OpenRouter failed, trying HuggingFace...", file=sys.stderr)
        
        # Fallback to HuggingFace
        if self.hf_tokens:
            print("[DEBUG] Trying HuggingFace API...", file=sys.stderr)
            result = await self._try_huggingface(prompt)
            if result:
                print("[DEBUG] HuggingFace succeeded!", file=sys.stderr)
                return result
            else:
                print("[DEBUG] HuggingFace failed", file=sys.stderr)
        
        print("[DEBUG] All LLM attempts failed", file=sys.stderr)
        return {}

    async def _try_openrouter(self, prompt: str) -> Dict[str, Any]:
        """Try OpenRouter API with multiple models and keys, with failure tracking."""
        available_keys = self._get_available_openrouter_keys()
        if not available_keys:
            print("[DEBUG] No available OpenRouter keys", file=sys.stderr)
            return {}
        
        import time
        
        for model in self.openrouter_models:
            for key in available_keys:
                try:
                    print(f"[DEBUG] Trying OpenRouter model: {model}, key: {key[:20]}...", file=sys.stderr)
                    
                    headers = {
                        "Authorization": f"Bearer {key}",
                        "Content-Type": "application/json",
                        "HTTP-Referer": "https://github.com/gyasaswini10",
                        "X-Title": "Autonomous Presenter"
                    }
                    
                    enhanced_prompt = (
                        "You output a single JSON object only, no markdown, no explanation.\n"
                        f"Task: {prompt}\n"
                        f'Schema: {{"bullets":["string", ...]}} with exactly {NUM_SLIDE_BULLETS} strings.\n'
                        "Each bullet should be a complete, factual sentence with specific details."
                    )
                    
                    payload = {
                        "model": model,
                        "messages": [{"role": "user", "content": enhanced_prompt}],
                        "max_tokens": 700,
                        "temperature": 0.3
                    }
                    
                    url = "https://openrouter.ai/api/v1/chat/completions"
                    async with httpx.AsyncClient(timeout=30.0) as client:
                        r = await client.post(url, headers=headers, json=payload)
                    
                    if r.status_code == 200:
                        body = r.json()
                        if "choices" in body and body["choices"]:
                            content = body["choices"][0]["message"]["content"]
                            # Extract JSON from response
                            match = re.search(r"\{[\s\S]*\}", content)
                            if match:
                                try:
                                    result = json.loads(match.group(0))
                                    print(f"[DEBUG] OpenRouter success with {model}", file=sys.stderr)
                                    return result
                                except json.JSONDecodeError:
                                    try:
                                        result = json.loads(match.group(0).replace("'", '"'))
                                        print(f"[DEBUG] OpenRouter success with {model}", file=sys.stderr)
                                        return result
                                    except json.JSONDecodeError:
                                        print(f"[DEBUG] OpenRouter JSON parse failed with {model}", file=sys.stderr)
                                        pass
                        else:
                            print(f"[DEBUG] OpenRouter invalid response format with {model}", file=sys.stderr)
                    elif r.status_code == 401:
                        print(f"[DEBUG] OpenRouter auth failed, marking key as failed", file=sys.stderr)
                        self._failed_openrouter_keys[key] = time.time()
                        break  # Skip to next key
                    elif r.status_code == 429:
                        print(f"[DEBUG] OpenRouter rate limited, marking key as failed temporarily", file=sys.stderr)
                        self._failed_openrouter_keys[key] = time.time()
                        break  # Skip to next key
                    else:
                        print(f"[DEBUG] OpenRouter HTTP {r.status_code} with {model}", file=sys.stderr)
                        
                except httpx.TimeoutException:
                    print(f"[DEBUG] OpenRouter timeout with {model}, marking key as failed temporarily", file=sys.stderr)
                    self._failed_openrouter_keys[key] = time.time()
                    break  # Skip to next key
                except Exception as e:
                    print(f"[DEBUG] OpenRouter error with {model}: {e}", file=sys.stderr)
                    continue
        return {}

    async def _try_huggingface(self, prompt: str) -> Dict[str, Any]:
        """Try HuggingFace API with multiple models and tokens, with failure tracking."""
        available_tokens = self._get_available_hf_tokens()
        if not available_tokens:
            print("[DEBUG] No available HuggingFace tokens", file=sys.stderr)
            return {}
        
        import time
        
        for model in self.hf_models:
            for token in available_tokens:
                try:
                    print(f"[DEBUG] Trying HF model: {model}, token: {token[:20]}...", file=sys.stderr)
                    
                    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
                    wrapped = (
                        "You output a single JSON object only, no markdown, no explanation.\n"
                        f"Task: {prompt}\n"
                        f'Schema: {{"bullets":["string", ...]}} with exactly {NUM_SLIDE_BULLETS} strings.'
                    )
                    payload = {
                        "inputs": wrapped,
                        "parameters": {"max_new_tokens": 700, "return_full_text": False},
                    }
                    url = f"https://api-inference.huggingface.co/models/{model}"
                    async with httpx.AsyncClient(timeout=120.0) as client:
                        r = await client.post(url, headers=headers, json=payload)
                    
                    if r.status_code == 200:
                        body = r.json()
                        if isinstance(body, dict) and body.get("error"):
                            print(f"[DEBUG] HF API error: {body.get('error')}", file=sys.stderr)
                            continue
                            
                        txt = ""
                        if isinstance(body, list) and body:
                            txt = body[0].get("generated_text", "") or ""
                        elif isinstance(body, dict):
                            txt = body.get("generated_text", "") or ""
                            
                        match = re.search(r"\{[\s\S]*\}", txt)
                        if match:
                            rawj = match.group(0)
                            try:
                                result = json.loads(rawj)
                                print(f"[DEBUG] HF success with {model}", file=sys.stderr)
                                return result
                            except json.JSONDecodeError:
                                try:
                                    result = json.loads(rawj.replace("'", '"'))
                                    print(f"[DEBUG] HF success with {model}", file=sys.stderr)
                                    return result
                                except json.JSONDecodeError:
                                    print(f"[DEBUG] HF JSON parse failed with {model}", file=sys.stderr)
                                    pass
                    elif r.status_code == 401:
                        print(f"[DEBUG] HF auth failed, marking token as failed", file=sys.stderr)
                        self._failed_hf_tokens[token] = time.time()
                        break  # Skip to next token
                    elif r.status_code == 429:
                        print(f"[DEBUG] HF rate limited, marking token as failed temporarily", file=sys.stderr)
                        self._failed_hf_tokens[token] = time.time()
                        break  # Skip to next token
                    elif r.status_code == 503:
                        print(f"[DEBUG] HF model loading, trying next token", file=sys.stderr)
                        continue  # Try next token immediately
                    else:
                        print(f"[DEBUG] HF HTTP {r.status_code} with {model}", file=sys.stderr)
                        
                except httpx.TimeoutException:
                    print(f"[DEBUG] HF timeout with {model}, marking token as failed temporarily", file=sys.stderr)
                    self._failed_hf_tokens[token] = time.time()
                    break  # Skip to next token
                except Exception as e:
                    print(f"[DEBUG] HF error with {model}: {e}", file=sys.stderr)
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
                if not self.openrouter_keys and not self.hf_tokens:
                    print("[AGENT] WARN: No OPENROUTER_KEY or HF_TOKEN in .env — slide text will use web + dictionary only.")
                elif not self.openrouter_keys:
                    print("[AGENT] INFO: No OPENROUTER_KEY in .env — using HuggingFace API only.")
                elif not self.hf_tokens:
                    print("[AGENT] INFO: No HF_TOKEN in .env — using OpenRouter API only.")

                # 🧠 PLAN: Scientific Hierarchy
                plan = {"title": f"The Science and Evolution of {subj}", "slides": [{"title": "Origins and Taxonomy"},{"title": "Physiological & Structural Features"},{"title": "Biological Growth & Lifecycle"},{"title": "Ecological & Environmental Roles"},{"title": "Industrial & Societal Impact"},{"title": "Future Research & Conservation Directions"}]}
                
                resp = await ppt.call_tool("create_pptx", {"title": plan["title"]})
                sid = json.loads(resp.content[0].text)["session_id"]

                for i, s_m in enumerate(plan["slides"]):
                    title = s_m["title"]; idx = i + 1
                    print(f"[AGENT] Generating Expert Content for Slide {idx}: {title}")

                    # 🔍 1. WIKI-RESEARCH (topic-based title so en.wikipedia resolves a real article)
                    r_raw = await res.call_tool(
                        "search_topic",
                        {"query": f"{subj} {title} facts biology", "slide_title": title},
                    )
                    raw_points = json.loads(r_raw.content[0].text).get("points", [])
                    pool = [str(x).strip() for x in raw_points if str(x).strip()]
                    on_topic = [p for p in pool if self.bullet_matches_slide(subj, title, p)]
                    base_pool = on_topic if len(on_topic) >= 3 else pool
                    facts = self._slide_fact_window(base_pool, idx, 6)
                    facts = [f for f in facts if self.bullet_matches_slide(subj, title, f)]
                    if len(facts) < 3:
                        facts = [f for f in self._slide_fact_window(pool, idx, 8) if self.bullet_matches_slide(subj, title, f)]
                    facts_snip = json.dumps(facts[:10])[:1200]

                    # 🧠 2. Model generation with enhanced prompt for specific content requirements
                    if title == "Origins and Taxonomy" and subj.lower() == "tomato":
                        # Specialized prompt for tomato origins and taxonomy
                        enhanced_prompt = (
                            f"Presentation topic: {subj!r}. Slide heading: {title!r}.\n"
                            f"Research context: {facts_snip}\n"
                            f"Generate exactly {NUM_SLIDE_BULLETS} bullet points that MUST include:\n"
                            "1. How 'Origins and Taxonomy' applies to tomato with one concrete example from industry or nature\n"
                            "2. Two measurable traits or stages of tomato that illustrate 'Origins and Taxonomy'\n"
                            "3. Comparison of tomato with a related species (one similarity, one difference)\n"
                            "4. One challenge and one opportunity for tomato under 'Origins and Taxonomy'\n"
                            "5. A key scientific fact about tomato classification or evolution\n"
                            "Each bullet should be a complete factual sentence with specific details. No generic statements."
                        )
                    else:
                        enhanced_prompt = (
                            f"Presentation topic: {subj!r}. Slide heading: {title!r}.\n"
                            f"Optional research snippets from the web (use when accurate, else general knowledge): {facts_snip}\n"
                            f"Write exactly {NUM_SLIDE_BULLETS} bullet points for this slide only. "
                            "Each bullet is one clear sentence, factual, educational, matching the slide heading. "
                            "No slang, no dictionary-style '(noun)' labels, no jokes. Mention the topic where natural."
                        )
                    
                    model_gen = await self.ask_llm(enhanced_prompt)
                    bullets = model_gen.get("bullets", [])
                    if isinstance(bullets, list):
                        bullets = [str(b).strip() for b in bullets if self._llm_bullet_ok(str(b))]
                    else:
                        bullets = []

                    bullets = await self._finalize_bullets(subj, title, bullets, pool, facts, res, idx)

                    await ppt.call_tool(
                        "add_slide",
                        {"session_id": sid, "slide_title": title, "bullets": bullets[:NUM_SLIDE_BULLETS]},
                    )

                    # Thumbnail handler
                    thumb = json.loads(r_raw.content[0].text).get("thumbnail")
                    if thumb and "wikimedia.org" in thumb:
                        try:
                            async with httpx.AsyncClient(follow_redirects=True) as client:
                                r = await client.get(thumb)
                                if r.status_code == 200 and self._is_embeddable_image(r.content):
                                    p = base / f"img_{idx}.jpg"
                                    p.write_bytes(r.content)
                                    await ppt.call_tool(
                                        "add_image",
                                        {"session_id": sid, "slide_index": idx, "image_path": str(p.resolve())},
                                    )
                        except: pass

                final_out = str(self.output_path.resolve())
                await ppt.call_tool("save_presentation", {"session_id": sid, "output_path": final_out})
                print(f"[SUCCESS] Expert Presentation Finalized: {final_out}")

def main():
    p = argparse.ArgumentParser(); p.add_argument("prompt"); p.add_argument("--output", default="FINAL.pptx"); args = p.parse_args()
    root = Path(__file__).resolve().parent.parent; out_dir = root / "savingfolder_output"; out_dir.mkdir(exist_ok=True)
    f_path = out_dir / Path(args.output).name; c = 1
    while f_path.exists(): f_path = out_dir / f"{Path(args.output).stem}_v{c}{Path(args.output).suffix}"; c += 1
    asyncio.run(AutonomousPresenter(args.prompt, str(f_path.resolve())).execute())

if __name__ == "__main__": main()
