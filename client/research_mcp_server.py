"""
MCP Server — lightweight topic facts for bullet content.

This server uses a simple Wikipedia summary endpoint (best effort) and
returns plausible fallback bullets when the lookup fails, so the agent
never crashes on missing data (per assignment robustness requirement).
"""

import logging  # Quiet MCP/httpx INFO when spawned as stdio subprocess.
import re  # Used to strip noisy suffixes from slide titles before lookup.
from typing import List  # Type hints for tool IO.
from urllib.parse import quote  # Encode topic for dictionary API paths.

import httpx  # HTTP client for fetching a short page summary.

logging.getLogger("mcp").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)
from mcp.server.fastmcp import FastMCP  # FastMCP provides the MCP server wrapper.

# Wikipedia often returns 403 without a descriptive User-Agent; required for reliable demos.
_HTTP_HEADERS = {
    "User-Agent": "AutoPPT-MCPAssignment/1.0 (educational assignment; python-httpx)",
    "Accept": "application/json",
}


mcp = FastMCP("research-mcp-server")


def _fallback_points(query: str) -> List[str]:
    # No hardcoded topic facts — return empty so callers rely on live sources or retry.
    return []


def _primary_topic_for_wikipedia(query: str) -> str:
    """Use the real article title (e.g. subject), not 'Topic + slide title + facts biology'."""
    q = query.strip()
    for suffix in (" facts biology", " facts", " overview"):
        if q.lower().endswith(suffix):
            q = q[: -len(suffix)].strip()
    low = q.lower()
    cut = len(q)
    for m in (
        " origins and taxonomy",
        " physiological",
        " biological growth",
        " ecological",
        " industrial",
        " future research",
        " structural features",
        " structural morphology",
        " lifecycle",
    ):
        i = low.find(m)
        if i > 0:
            cut = min(cut, i)
    base = q[:cut].strip()
    return base if base else q


def _word_balance_chunks(text: str, n: int) -> List[str]:
    """Split plain text into n readable chunks on word boundaries (for long ledes)."""
    words = text.split()
    if not words:
        return []
    n = max(1, min(n, len(words)))
    base, rem = divmod(len(words), n)
    out: List[str] = []
    i = 0
    for k in range(n):
        take = base + (1 if k < rem else 0)
        if take <= 0:
            break
        out.append(" ".join(words[i : i + take]))
        i += take
    return out


def _bullets_from_wikipedia_extract(extract: str, query: str) -> List[str]:
    """
    Wikipedia REST `extract` is often 1–2 sentences; requiring 3+ sentences always
    triggered generic fallbacks. Use real text first, then word-chunk to fill slides.
    """
    extract = (extract or "").strip()
    if len(extract) < 40:
        return []

    parts = re.split(r"(?<=[.!?])\s+", extract)
    sentences = [p.strip() for p in parts if len(p.strip()) > 18]
    # Pull in clause-like units if the lede is semicolon-heavy
    expanded: List[str] = []
    for s in sentences:
        if "; " in s and len(sentences) < 4:
            expanded.extend([c.strip() for c in s.split(";") if len(c.strip()) > 18])
        else:
            expanded.append(s)
    seen: set[str] = set()
    bullets: List[str] = []
    for b in expanded:
        key = b.lower()
        if key in seen:
            continue
        seen.add(key)
        bullets.append(b)

    if len(bullets) >= 6:
        return bullets[:12]
    # Short ledes: add word-balanced slices so we still return real article text (not templates)
    n_chunks = 12 if len(extract) > 320 else 6
    balanced = _word_balance_chunks(extract, n_chunks)
    if not bullets:
        return balanced
    # Keep sentence-first ordering, then chunks; dedupe exact matches
    merged = bullets + balanced
    seen2: set[str] = set()
    out: List[str] = []
    for x in merged:
        k = x.lower()
        if k in seen2:
            continue
        seen2.add(k)
        out.append(x)
    return out[:12]


def _extract_from_wikipedia_text(extract: str, query: str) -> dict:
    """Build bullet points from a plain-text extract."""
    points = _bullets_from_wikipedia_extract(extract, query)
    return {"ok": True, "points": points or [], "source": "wikipedia"}


def _mediawiki_fallback(q: str, query: str) -> dict | None:
    """
    If REST summary is blocked (403) or misses the title, try opensearch + extracts API.
    """
    try:
        from urllib.parse import quote

        search_url = (
            "https://en.wikipedia.org/w/api.php?"
            f"action=opensearch&search={quote(q)}&limit=1&namespace=0&format=json"
        )
        r = httpx.get(search_url, headers=_HTTP_HEADERS, timeout=8.0)
        if r.status_code != 200:
            return None
        payload = r.json()
        if not isinstance(payload, list) or len(payload) < 2 or not payload[1]:
            return None
        title = payload[1][0]
        extract_url = (
            "https://en.wikipedia.org/w/api.php?"
            "action=query&format=json&prop=extracts&exintro=1&explaintext=1&"
            f"titles={quote(title)}"
        )
        r2 = httpx.get(extract_url, headers=_HTTP_HEADERS, timeout=8.0)
        if r2.status_code != 200:
            return None
        data = r2.json()
        pages = data.get("query", {}).get("pages", {})
        for _pid, page in pages.items():
            extract = page.get("extract", "") if isinstance(page, dict) else ""
            if extract:
                return _extract_from_wikipedia_text(extract, query)
    except Exception:
        return None
    return None


def _extract_from_text(text: str, query: str) -> List[str]:
    return _bullets_from_wikipedia_extract(text, query)


def _fetch_wikipedia_exchars(page_title: str) -> str:
    """Longer plain-text extract from MediaWiki (same article, more than REST intro)."""
    if not page_title.strip():
        return ""
    try:
        url = (
            "https://en.wikipedia.org/w/api.php?action=query&format=json&prop=extracts"
            "&explaintext=1&exsectionformat=plain&exchars=12000&titles="
            + quote(page_title, safe="")
        )
        r = httpx.get(url, headers=_HTTP_HEADERS, timeout=15.0)
        if r.status_code != 200:
            return ""
        data = r.json()
        pages = data.get("query", {}).get("pages", {})
        for _pid, page in pages.items():
            if not isinstance(page, dict):
                continue
            if page.get("missing"):
                continue
            ex = page.get("extract", "") or ""
            if ex:
                return ex
    except Exception:
        pass
    return ""


def _sentences_from_extract(text: str) -> List[str]:
    if not (text or "").strip():
        return []
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [p.strip() for p in parts if len(p.strip()) > 22]


_SLIDE_TITLE_STOP = frozenset(
    """origins taxonomy structural physiological features biological environmental
    industrial societal directions conservation research future growth lifecycle
    roles impact with from that this their""".split()
)


def _score_sentence_for_slide(sentence: str, topic: str, slide_title: str) -> int:
    s = sentence.lower()
    score = 0
    for w in set(re.findall(r"[a-z]{4,}", (slide_title or "").lower())):
        if w in _SLIDE_TITLE_STOP and len(w) < 6:
            continue
        if w in s:
            score += 3
    for w in re.findall(r"[a-z]+", (topic or "").lower()):
        if len(w) >= 4 and w in s:
            score += 1
    return score


def _ranked_bullets_for_slide(full_text: str, topic: str, slide_title: str) -> List[str]:
    """Pick sentences from long Wikipedia text that match this slide heading (dynamic, no hardcoded facts)."""
    sentences = _sentences_from_extract(full_text)
    if not sentences:
        return []
    scored = [(_score_sentence_for_slide(s, topic, slide_title), s) for s in sentences]
    scored.sort(key=lambda x: -x[0])
    seen: set[str] = set()
    out: List[str] = []
    for sc, s in scored:
        if sc <= 0:
            break
        k = s.lower()
        if k in seen:
            continue
        seen.add(k)
        out.append(s if s.endswith(".") else s + ".")
        if len(out) >= 18:
            break
    if len(out) >= 4:
        return out
    # Not enough keyword overlap: fall back to neutral chunking of the same internet text
    return _bullets_from_wikipedia_extract(full_text[:8000], topic)


def _wiki_plain_extract_via_search(search_phrase: str) -> str:
    """OpenSearch + extracts → plain text (one merged string)."""
    try:
        search_url = (
            "https://en.wikipedia.org/w/api.php?"
            f"action=opensearch&search={quote(search_phrase)}&limit=1&namespace=0&format=json"
        )
        r = httpx.get(search_url, headers=_HTTP_HEADERS, timeout=10.0)
        if r.status_code != 200:
            return ""
        payload = r.json()
        if not isinstance(payload, list) or len(payload) < 2 or not payload[1]:
            return ""
        title = payload[1][0]
        return _fetch_wikipedia_exchars(title)
    except Exception:
        return ""


def _supplement_points_from_web(topic: str, slide_title: str) -> List[str]:
    """Extra Wikipedia searches: topic + salient words from the slide title (still dynamic)."""
    hints = list(
        dict.fromkeys(
            w
            for w in re.findall(r"[a-z]{4,}", (slide_title or "").lower())
            if w not in _SLIDE_TITLE_STOP or len(w) >= 6
        )
    )[:5]
    if not hints:
        hints = ["overview"]
    seen: set[str] = set()
    merged: List[str] = []
    for h in hints:
        blob = _wiki_plain_extract_via_search(f"{topic} {h}")
        if not blob:
            continue
        for line in _ranked_bullets_for_slide(blob, topic, slide_title):
            k = line.lower()
            if k not in seen:
                seen.add(k)
                merged.append(line)
        if len(merged) >= 18:
            break
    return merged[:18]


_DICT_SLANG = re.compile(
    r"\b(slang|informal|figurative|offensive|vulgar|pejorative|dated)\b|"
    r"\blookit\b|!|attractive woman|legs on|hot tomato|pelt with|shade of red|colour of|color of\b",
    re.I,
)
_DICT_VERB_DEF = re.compile(r"^\s*to\s+", re.I)
# Encyclopedic / descriptive — filters out color-slang senses and verb "to pelt / to add"
_DICT_EDU = re.compile(
    r"\b(plant|species|genus|family|fruit|vegetable|berry|crop|edible|cultivar|tree|shrub|herb|"
    r"native|grow|grown|leaf|seed|flower|root|stem|contain|rich|vitamin|mineral|nutrient|"
    r"protein|starch|acid|sugar|fiber|antioxidant|lycopene|caroten|source|food|origin|region|"
    r"climate|harvest|annual|perennial|biology|anatomy|structure|cell|tissue|animal|organism|"
    r"person|people|human|teacher|student|school|education|machine|device|computer|instrument|"
    r"building|organization|system|process|material|element|chemical|energy|force|theory)\b",
    re.I,
)


def _dictionary_definition_ok(defn: str, topic: str) -> bool:
    low = defn.lower()
    if len(low) < 20 or _DICT_SLANG.search(defn):
        return False
    if _DICT_VERB_DEF.search(defn.strip()):
        return False
    tw = topic.lower().strip()
    if tw and tw not in low and not any(
        len(w) >= 4 and w in low for w in re.findall(r"[a-z]+", tw)
    ):
        return False
    return bool(_DICT_EDU.search(defn))


def _dictionaryapi_bullets(topic: str) -> List[str] | None:
    """
    Free dictionary API — only **noun** senses that read like encyclopedia lines (no slang, verbs, or examples).
    """
    slug = re.sub(r"[^a-zA-Z0-9 ]+", " ", topic).strip().lower()
    if not slug or len(slug) > 64:
        return None
    candidates: List[str] = []
    if " " not in slug:
        candidates.append(slug)
    else:
        for w in slug.split():
            if len(w) > 2:
                candidates.append(w)
        candidates.append(slug.split()[0])
    seen: set[str] = set()
    bullets: List[str] = []
    for c in candidates:
        if len(bullets) >= 8:
            break
        url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{quote(c, safe='')}"
        try:
            r = httpx.get(url, headers=_HTTP_HEADERS, timeout=12.0)
            if r.status_code != 200:
                continue
            data = r.json()
            if not isinstance(data, list):
                continue
        except Exception:
            continue
        for entry in data:
            for meaning in entry.get("meanings", []) or []:
                pos = (meaning.get("partOfSpeech") or "").strip().lower()
                if pos != "noun":
                    continue
                for d in meaning.get("definitions", []) or []:
                    defn = (d.get("definition") or "").strip()
                    if not _dictionary_definition_ok(defn, topic):
                        continue
                    key = defn.lower()
                    if key in seen:
                        continue
                    seen.add(key)
                    line = defn[0].upper() + defn[1:] if defn else defn
                    if not line.endswith("."):
                        line += "."
                    bullets.append(line)
                    if len(bullets) >= 8:
                        break
                if len(bullets) >= 8:
                    break
            if len(bullets) >= 8:
                break
        if bullets:
            break
    if not bullets:
        return None

    def _topic_score(line: str) -> int:
        roots = {topic.lower()} | {w for w in topic.lower().split() if len(w) > 2}
        bl = line.lower()
        return sum(1 for r in roots if r in bl)

    bullets = sorted(bullets, key=_topic_score, reverse=True)

    if len(bullets) < 6 and bullets:
        primary = bullets[0].strip()
        if len(primary.split()) >= 28:
            bullets = _word_balance_chunks(primary, 6)
    return bullets[:12]


@mcp.tool()
async def search_topic(query: str, slide_title: str = "", supplement: bool = False) -> dict:
    """Fetch facts from Wikipedia (and dictionary only if Wikipedia fails). All topical text is from live APIs.

    **Required Tool Name:** search_topic.

    **Parameters:**
        query: Subject / search phrase (may include slide context; primary topic is parsed out).
        slide_title: When set, sentences are ranked so bullets match this heading (dynamic).
        supplement: When true, run extra Wikipedia searches (topic + words from the slide title).

    **Returns:**
        dict with ``ok``, ``points``, ``thumbnail``.
    """
    q = re.sub(r"\s+(Stage|Part|Phase|Process|Overview|Introduction|Cycle)\b", "", query, flags=re.IGNORECASE).strip()
    q = re.sub(r"\d+", "", q).strip() or query
    topic_phrase = _primary_topic_for_wikipedia(q)
    wiki_title = topic_phrase.replace(" ", "_")
    topic_display = topic_phrase.strip()

    if supplement:
        pts = _supplement_points_from_web(topic_display, slide_title)
        if not pts:
            pts = _fallback_points(topic_display)
        return {"ok": True, "points": pts, "thumbnail": "", "source": "wikipedia_supplement"}

    try:
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{wiki_title}"
        async with httpx.AsyncClient(headers=_HTTP_HEADERS, timeout=10.0, follow_redirects=True) as client:
            resp = await client.get(url)
            if resp.status_code == 200:
                data = resp.json()
                api_title = (data.get("title") or topic_display).strip()
                extract_short = (data.get("extract", "") or "").strip()
                extract_long = _fetch_wikipedia_exchars(api_title)
                full = (extract_long + "\n\n" + extract_short).strip()
                thumb = data.get("thumbnail", {}).get("source", "")
                if slide_title.strip() and len(full) > 80:
                    points = _ranked_bullets_for_slide(full, topic_display, slide_title)
                else:
                    points = _extract_from_text(extract_short or extract_long, api_title)
                if not points:
                    points = _extract_from_text(extract_short or extract_long, api_title)
                return {"ok": True, "points": points, "thumbnail": thumb, "source": "wikipedia"}
    except Exception:
        pass

    mw = _mediawiki_fallback(wiki_title.replace("_", " "), query)
    if mw:
        long_blob = _fetch_wikipedia_exchars(topic_display)
        if len(long_blob) < 200:
            long_blob = _wiki_plain_extract_via_search(topic_display)
        if slide_title.strip() and len(long_blob) > 80:
            points = _ranked_bullets_for_slide(long_blob, topic_display, slide_title)
        else:
            points = mw.get("points") or []
        if not points:
            points = mw.get("points") or []
        return {"ok": True, "points": points, "thumbnail": "", "source": mw.get("source", "wikipedia")}

    dict_pts = _dictionaryapi_bullets(topic_display)
    if dict_pts:
        return {
            "ok": True,
            "points": dict_pts,
            "thumbnail": "",
            "source": "dictionaryapi.dev",
        }

    return {"ok": True, "points": _fallback_points(topic_display), "thumbnail": "", "source": "fallback"}


if __name__ == "__main__":
    # `transport="stdio"` matches the agent's stdio MCP client setup.
    mcp.run(transport="stdio")
