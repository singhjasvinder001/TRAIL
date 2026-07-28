import subprocess
import os
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict

TRAIL_DIR = Path.home() / ".trail"
BOOKMARKS_FILE = TRAIL_DIR / "bookmarks.json"
CACHE_FILE = TRAIL_DIR / "cache.json"
CONFIG_FILE = TRAIL_DIR / "config.json"

def ensure_trail_dir():
    TRAIL_DIR.mkdir(parents=True, exist_ok=True)

def parse_zsh_history():
    history_path = Path.home() / ".zsh_history"
    if not history_path.exists():
        return []
    
    entries = []
    mtime = history_path.stat().st_mtime
    now = time.time()
    
    try:
        content = history_path.read_text(encoding="utf-8", errors="replace")
        lines = content.splitlines()
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            ts, cmd = None, line
            
            # Extended history format: ": 1234567890:0;command"
            if line.startswith(": "):
                parts = line[2:].split(";", 1)
                if len(parts) == 2:
                    meta_parts = parts[0].split(":")
                    try:
                        ts = int(meta_parts[0])
                    except (ValueError, IndexError):
                        ts = None
                    cmd = parts[1].strip()
            
            if cmd:
                if ts is None:
                    # Approximate: spread commands evenly across file modification time
                    ratio = i / max(len(lines) - 1, 1)
                    ts = mtime - ((len(lines) - i) * 5)
                entries.append({"timestamp": ts, "command": cmd, "source": "history"})
    except Exception:
        pass
    return entries

def get_recent_files(days=1, limit=50):
    try:
        query = f"kMDItemLastUsedDate >= $time.today(-{days})"
        result = subprocess.run(
            ["mdfind", query],
            capture_output=True, text=True, timeout=15
        )
        files = []
        for path in result.stdout.strip().split("\n"):
            path = path.strip()
            if not path or len(files) >= limit:
                continue
            p = Path(path)
            try:
                stat = p.stat()
                files.append({
                    "path": path,
                    "name": p.name,
                    "dir": str(p.parent),
                    "size": stat.st_size,
                    "modified": stat.st_mtime,
                    "source": "files"
                })
            except OSError:
                pass
        files.sort(key=lambda f: f["modified"], reverse=True)
        return files[:limit]
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return []

def get_project_from_path(path):
    parts = Path(path).parts
    for i in range(len(parts) - 1, 0, -1):
        if (Path(*parts[:i+1]) / ".git").exists():
            return parts[i]
    return None

def get_timeline(days=1, history_lines=200):
    files = get_recent_files(days=days)
    history = parse_zsh_history()[-history_lines:]
    
    timeline = defaultdict(list)
    now = datetime.now()
    
    for f in files:
        dt = datetime.fromtimestamp(f["modified"])
        label = _time_label(dt, now)
        f["project"] = get_project_from_path(f["path"])
        f["ext"] = Path(f["path"]).suffix.lower()
        f["time_label"] = label
        timeline[label].append(f)
    
    for h in history:
        if h["timestamp"]:
            dt = datetime.fromtimestamp(h["timestamp"])
            label = _time_label(dt, now)
        else:
            label = "Unknown"
        timeline[label].append(h)
    
    return dict(timeline)

def _time_label(dt, now):
    diff = now - dt
    if diff.days == 0:
        return "Today"
    elif diff.days == 1:
        return "Yesterday"
    elif diff.days < 7:
        return "This Week"
    elif diff.days < 14:
        return "Last Week"
    elif diff.days < 30:
        return "This Month"
    else:
        return "Older"

def search_history(query, max_results=50):
    history = parse_zsh_history()
    query_lower = query.lower()
    results = []
    for h in history:
        if query_lower in h["command"].lower():
            results.append(h)
            if len(results) >= max_results:
                break
    return results

def search_files(query, max_results=30):
    files = get_recent_files(days=7, limit=200)
    query_lower = query.lower()
    results = []
    for f in files:
        if query_lower in f["name"].lower() or query_lower in f["path"].lower():
            results.append(f)
    return results[:max_results]

class BookmarkManager:
    def __init__(self):
        ensure_trail_dir()
        self.bookmarks = self._load()
    
    def _load(self):
        if BOOKMARKS_FILE.exists():
            try:
                return json.loads(BOOKMARKS_FILE.read_text())
            except (json.JSONDecodeError, OSError):
                return {}
        return {}
    
    def save(self):
        BOOKMARKS_FILE.write_text(json.dumps(self.bookmarks, indent=2))
    
    def add(self, name, path=None):
        name = name.strip()
        if not name:
            return False, "Name cannot be empty"
        if not path:
            path = os.getcwd()
        path = os.path.abspath(path)
        if not os.path.exists(path):
            return False, f"Path does not exist: {path}"
        self.bookmarks[name] = {
            "path": path,
            "added": time.time(),
        }
        self.save()
        return True, f"Bookmarked '{name}' → {path}"
    
    def remove(self, name):
        if name in self.bookmarks:
            del self.bookmarks[name]
            self.save()
            return True, f"Removed bookmark '{name}'"
        return False, f"Bookmark '{name}' not found"
    
    def list(self):
        return dict(sorted(self.bookmarks.items(), key=lambda x: x[1]["added"], reverse=True))
    
    def get(self, name):
        return self.bookmarks.get(name)
    
    def search(self, query):
        query_lower = query.lower()
        return {k: v for k, v in self.bookmarks.items() if query_lower in k.lower() or query_lower in v["path"].lower()}
