#!/usr/bin/env python3
"""Build a small, source-linked public recruiting-tech news snapshot."""
import html
import json
import re
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "updates.json"
FEEDS = [
    {"name": "HR Dive", "url": "https://www.hrdive.com/feeds/news/", "home": "https://www.hrdive.com/", "region": "US"},
    {"name": "HR Tech Feed", "url": "https://hrtechfeed.com/feed/", "home": "https://hrtechfeed.com/", "region": "Global"},
]
TERMS = {
    "AI & automation": ["ai", "artificial intelligence", "agentic", "automation", "machine learning", "generative"],
    "Talent acquisition": ["recruit", "talent acquisition", "applicant tracking", "ats", "candidate", "hiring"],
    "Compliance": ["compliance", "regulation", "law", "legislation", "bias", "privacy", "eu ai act"],
    "Market moves": ["acquisition", "acquires", "merger", "funding", "launch", "partnership", "product"],
    "Product releases": ["launch", "launched", "release", "released", "introduces", "introduced", "new feature", "product update", "version"],
    "Adoption & buying": ["adoption", "adopted", "buyer intent", "buying intent", "deploy", "deployed", "rollout", "customer use", "usage", "implementation"],
    "Implementation": ["implementation", "go-live", "go live", "rollout", "deployment", "migration", "time to value"],
    "Candidate experience": ["candidate experience", "job seeker", "applicant experience", "candidate sentiment", "candidate satisfaction", "csat", "employee experience"],
}
VENDORS = ["Workday", "Greenhouse", "iCIMS", "Ashby", "SmartRecruiters", "Lever", "Oracle", "SAP", "Phenom", "Avature", "Paradox", "Eightfold", "Beamery", "Bullhorn", "Workable", "Jobvite", "UKG", "Darwinbox"]

def clean(value):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", value or ""))).strip()

def parse_date(value):
    if not value:
        return ""
    value = value.strip()
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        try:
            dt = parsedate_to_datetime(value)
        except Exception:
            return ""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")

def child_text(node, *names):
    for name in names:
        found = node.find(name)
        if found is not None and found.text:
            return found.text
    return ""

def parse_feed(feed):
    req = urllib.request.Request(feed["url"], headers={"User-Agent": "TalentSignal/1.0 (+public RSS aggregator)"})
    with urllib.request.urlopen(req, timeout=20) as response:
        payload = response.read(3_000_000)
    root = ET.fromstring(payload)
    entries = root.findall(".//item")
    atom = False
    if not entries:
        atom = True
        entries = root.findall(".//{http://www.w3.org/2005/Atom}entry")
    rows = []
    for item in entries[:50]:
        if atom:
            title = child_text(item, "{http://www.w3.org/2005/Atom}title")
            summary = child_text(item, "{http://www.w3.org/2005/Atom}summary", "{http://www.w3.org/2005/Atom}content")
            link_el = item.find("{http://www.w3.org/2005/Atom}link")
            link = link_el.get("href", "") if link_el is not None else ""
            date = child_text(item, "{http://www.w3.org/2005/Atom}published", "{http://www.w3.org/2005/Atom}updated")
        else:
            title = child_text(item, "title")
            summary = child_text(item, "description", "{http://purl.org/rss/1.0/modules/content/}encoded")
            link = child_text(item, "link")
            date = child_text(item, "pubDate", "{http://purl.org/dc/elements/1.1/}date")
        title, summary, link = clean(title), clean(summary)[:500], html.unescape(link.strip())
        if not title or not link:
            continue
        text = (title + " " + summary).lower()
        categories = [name for name, words in TERMS.items() if any(word in text for word in words)]
        if not categories:
            continue
        vendors = [name for name in VENDORS if name.lower() in text]
        rows.append({"title": title, "summary": summary, "url": link, "published": parse_date(date), "source": feed["name"], "sourceHome": feed["home"], "region": feed["region"], "categories": categories, "vendors": vendors})
    return rows

EVENT_SOURCES = [
    {"name": "HR Tech", "url": "https://www.hrtechnologyconference.com/faq"},
    {"name": "UNLEASH", "url": "https://www.unleash.ai/events/"},
    {"name": "Gartner HR", "url": "https://www.gartner.com/en/conferences/hr-conferences"},
    {"name": "SHRM HR-X Live", "url": "https://annual.shrm.org/hrxlive"},
]

def walk_event_objects(value):
    if isinstance(value, dict):
        kind = value.get("@type", [])
        kinds = [kind] if isinstance(kind, str) else kind
        if any("event" in str(item).lower() for item in kinds) and value.get("name") and value.get("startDate"):
            yield value
        for child in value.values():
            yield from walk_event_objects(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk_event_objects(child)

def event_date(value):
    normalized = parse_date(value)
    return normalized[:10] if normalized else ""

def event_fields(obj, source):
    location = obj.get("location", {})
    if isinstance(location, list):
        location = location[0] if location else {}
    if not isinstance(location, dict):
        location = {"name": str(location)}
    address = location.get("address", {})
    if isinstance(address, str):
        address = {"streetAddress": address}
    address = address if isinstance(address, dict) else {}
    url = obj.get("url", "")
    if not isinstance(url, str) or not url.startswith("https://"):
        url = source["url"]
    return {
        "name": clean(obj.get("name", "")),
        "startDate": event_date(obj.get("startDate", "")),
        "endDate": event_date(obj.get("endDate", obj.get("startDate", ""))),
        "venue": clean(location.get("name", "")),
        "city": clean(address.get("addressLocality", "")),
        "country": clean(address.get("addressCountry", "")),
        "theme": clean(obj.get("about", "") if isinstance(obj.get("about"), str) else ""),
        "summary": clean(obj.get("description", ""))[:450],
        "url": url,
        "source": source["name"],
        "sourcePage": source["url"],
    }

def refresh_events():
    path = ROOT / "data" / "events.json"
    data = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {"upcoming": [], "recent": []}
    now = datetime.now(timezone.utc)
    checks, errors, candidates = [], [], []
    for source in EVENT_SOURCES:
        try:
            request = urllib.request.Request(source["url"], headers={"User-Agent": "TalentSignal/1.0 (+public event page monitor)"})
            with urllib.request.urlopen(request, timeout=25) as response:
                page = response.read(4_000_000).decode("utf-8", "replace")
            scripts = re.findall(r"<script[^>]*type=[\"']application/ld\+json[\"'][^>]*>(.*?)</script>", page, re.I | re.S)
            found = 0
            for raw in scripts:
                try:
                    parsed = json.loads(html.unescape(raw.strip()))
                except Exception:
                    continue
                for obj in walk_event_objects(parsed):
                    event = event_fields(obj, source)
                    if event["name"] and event["startDate"]:
                        candidates.append(event)
                        found += 1
            checks.append({"name": source["name"], "url": source["url"], "ok": True, "eventsFound": found})
        except Exception as exc:
            checks.append({"name": source["name"], "url": source["url"], "ok": False, "eventsFound": 0})
            errors.append({"source": source["name"], "reason": str(exc)[:160]})
    for event in candidates:
        pool = data.get("upcoming", []) + data.get("recent", [])
        best = None
        best_score = 0
        candidate_words = set(re.findall(r"[a-z0-9]+", event["name"].lower()))
        for existing in pool:
            existing_words = set(re.findall(r"[a-z0-9]+", existing.get("name", "").lower()))
            score = len(candidate_words & existing_words) / max(1, len(candidate_words | existing_words))
            if event.get("city") and event["city"].lower() == existing.get("city", "").lower():
                score += 0.4
            if event.get("startDate", "")[:4] == existing.get("startDate", "")[:4]:
                score += 0.2
            if event.get("sourcePage") == existing.get("sourcePage"):
                score += 0.1
            if score > best_score:
                best, best_score = existing, score
        if best and best_score >= 0.45:
            for key in ("startDate", "endDate", "venue", "city", "country", "summary", "url"):
                if event.get(key):
                    best[key] = event[key]
            if event.get("theme"):
                best["theme"] = event["theme"]
            best["lastVerifiedAt"] = now.isoformat(timespec="seconds").replace("+00:00", "Z")
    # Make publisher verification status visible even when a page lacks Event schema.
    data["generatedAt"] = now.isoformat(timespec="seconds").replace("+00:00", "Z")
    data["sourceTotal"] = len(EVENT_SOURCES)
    data["sourceCount"] = sum(1 for item in checks if item["ok"])
    data["sources"] = checks
    data["sourceErrors"] = errors
    feed_path = ROOT / "data" / "updates.json"
    try:
        feed_data = json.loads(feed_path.read_text(encoding="utf-8"))
        event_terms = ("conference", "symposium", "summit", "expo", "event", "unleash", "shrm26", "hr tech")
        data["coverage"] = [item for item in feed_data.get("items", []) if any(term in (item.get("title", "") + " " + item.get("summary", "")).lower() for term in event_terms)][:12]
    except Exception:
        data["coverage"] = []
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Checked {data['sourceCount']}/{data['sourceTotal']} event pages; {len(candidates)} structured events found")

def main():
    rows, errors = [], []
    for feed in FEEDS:
        try:
            rows.extend(parse_feed(feed))
        except Exception as exc:
            errors.append({"source": feed["name"], "reason": str(exc)[:180]})
    unique = {}
    for row in rows:
        key = row["url"].split("#", 1)[0].rstrip("/")
        if key not in unique or (row["published"] and row["published"] > unique[key]["published"]):
            unique[key] = row
    ordered = sorted(unique.values(), key=lambda row: row["published"], reverse=True)[:60]
    data = {"generatedAt": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"), "sourceCount": len(FEEDS) - len(errors), "sourceTotal": len(FEEDS), "itemCount": len(ordered), "sources": [{"name": feed["name"], "url": feed["home"], "region": feed["region"]} for feed in FEEDS], "errors": errors, "items": ordered}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(ordered)} items from {data['sourceCount']}/{data['sourceTotal']} public feeds")
    refresh_events()

if __name__ == "__main__":
    main()
