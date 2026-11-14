"""Manually refresh public metadata for the fixed curated GitHub registry.

Run: python website/refresh_popular.py
No token, account, external dependency, installation, scheduler or publication.
Only content/popular-snapshot.json is written. Requests are serial and bounded.
"""
import json
import re
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).resolve().parent
REGISTRY = BASE / "content" / "popular-registry.json"
SNAPSHOT = BASE / "content" / "popular-snapshot.json"
REPO = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]*/[A-Za-z0-9][A-Za-z0-9_.-]*\Z")


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def load_registry():
    data = json.loads(REGISTRY.read_text(encoding="utf-8"))
    repos, ids = set(), set()
    for item in data["items"]:
        repo = item["repository"]
        if not REPO.fullmatch(repo) or ".." in repo or repo.lower() in repos or item["id"] in ids:
            raise ValueError("Invalid or duplicate registry repository/id")
        repos.add(repo.lower())
        ids.add(item["id"])
    if not 1 <= len(data["items"]) <= 20:
        raise ValueError("Registry must contain 1–20 curated repositories")
    return data


def refresh():
    registry = load_registry()
    previous = json.loads(SNAPSHOT.read_text(encoding="utf-8")) if SNAPSHOT.exists() else {}
    old = {item["id"]: item for item in previous.get("items", [])}
    items, blocked = [], None
    for source in registry["items"]:
        cached = old.get(source["id"], {})
        item = {**source, "url": "https://github.com/" + source["repository"],
                "description": cached.get("description"), "stars": cached.get("stars"),
                "starsCheckedAt": cached.get("starsCheckedAt"),
                "upstreamPushedAt": cached.get("upstreamPushedAt"), "license": cached.get("license"),
                "fetchStatus": "unavailable", "error": None, "attemptedAt": now()}
        try:
            if blocked:
                raise RuntimeError(blocked)
            headers = {"User-Agent": "SkillLantern-manual-metadata-refresh", "Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
            if cached.get("etag"):
                headers["If-None-Match"] = cached["etag"]
            request = urllib.request.Request("https://api.github.com/repos/" + source["repository"], headers=headers)
            with urllib.request.urlopen(request, timeout=15) as response:
                data = json.load(response)
                if not REPO.fullmatch(data["full_name"]):
                    raise ValueError("Invalid canonical repository from GitHub")
                stars = data["stargazers_count"]
                if type(stars) is not int or stars < 0:
                    raise ValueError("Invalid GitHub star count")
                item.update(repository=data["full_name"], url="https://github.com/" + data["full_name"],
                            description=data.get("description"), stars=stars, starsCheckedAt=now(),
                            upstreamPushedAt=data.get("pushed_at"), license=(data.get("license") or {}).get("spdx_id"),
                            fetchStatus="fresh", etag=response.headers.get("ETag"))
        except urllib.error.HTTPError as error:
            if error.code == 304 and cached.get("stars") is not None:
                item.update(fetchStatus="fresh", starsCheckedAt=now(), etag=cached.get("etag"))
            else:
                item["error"] = "GitHub HTTP " + str(error.code)
                if error.code in (403, 429):
                    blocked = "Refresh stopped after GitHub rate/access limit; retry manually later."
                    item["error"] += "; retry-after=" + str(error.headers.get("Retry-After")) + "; reset=" + str(error.headers.get("X-RateLimit-Reset"))
        except (OSError, ValueError, KeyError, RuntimeError) as error:
            item["error"] = str(error)
        if item["fetchStatus"] != "fresh":
            item["fetchStatus"] = "stale" if item["stars"] is not None else "unavailable"
        items.append(item)
        print(f'{item["repository"]}: {item["stars"]} ({item["fetchStatus"]})')
    items.sort(key=lambda item: (item["stars"] is None, -(item["stars"] or 0), item["name"].lower()))
    snapshot = {"schemaVersion": 1, "generatedAt": now(), "scope": registry["scope"],
                "sort": "stars-desc-null-last", "refreshMode": "manual snapshot; optional reader-triggered public GitHub refresh; no recurring job or live stream", "items": items}
    temporary = SNAPSHOT.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(SNAPSHOT)
    return snapshot


if __name__ == "__main__":
    refresh()
