import os
from pathlib import Path
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.text import Text
from rich.columns import Columns
from rich import box
from rich.syntax import Syntax

console = Console()

HOME = Path.home()

def shorten_path(path, max_len=60):
    p = str(path)
    if p.startswith(str(HOME)):
        p = "~" + p[len(str(HOME)):]
    if len(p) > max_len:
        parts = p.split(os.sep)
        if len(parts) > 3:
            p = os.sep.join(["…"] + parts[-(3):])
    return p

def format_size(size_bytes):
    for unit in ["", "K", "M", "G"]:
        if size_bytes < 1024:
            return f"{size_bytes:.1f}{unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f}T"

def file_icon(ext):
    icons = {
        ".py": "🐍", ".js": "⬡", ".ts": "⬡", ".tsx": "⚛", ".jsx": "⚛",
        ".html": "🌐", ".css": "🎨", ".json": "📋", ".md": "📝",
        ".go": "🔵", ".rs": "🦀", ".rb": "💎", ".swift": "🐦",
        ".java": "☕", ".c": "⚙", ".cpp": "⚙", ".h": "📐",
        ".sql": "🗄", ".yaml": "📋", ".yml": "📋", ".toml": "📋",
        ".sh": "📜", ".zsh": "📜", ".bash": "📜",
        ".png": "🖼", ".jpg": "🖼", ".jpeg": "🖼", ".gif": "🖼", ".svg": "🖼",
        ".pdf": "📄", ".txt": "📄", ".csv": "📊",
        ".zip": "🗜", ".tar": "🗜", ".gz": "🗜",
        ".mp3": "🎵", ".mp4": "🎬", ".mov": "🎬",
        ".dmg": "💿", ".app": "📦",
    }
    return icons.get(ext, "📄")

SKIP_NAMES = {
    "DS_Store", ".DS_Store", "Shared", "Users",
    "Applications", "Desktop", "Documents", "Downloads", "Library",
}

SKIP_SUFFIXES = {".localized"}
SKIP_EXTENSIONS = {".app"}

SKIP_PREFIXES = (
    "/System/", "/Library/",
)

def _is_useful_file(f):
    name = f.get("name", "")
    path = f.get("path", "")
    ext = f.get("ext", "")
    
    if name in SKIP_NAMES:
        return False
    
    for suffix in SKIP_SUFFIXES:
        if name.endswith(suffix):
            return False
    
    for skip_ext in SKIP_EXTENSIONS:
        if ext == skip_ext:
            return False
    
    if path.startswith(SKIP_PREFIXES):
        return False
    
    if not ext and not name.startswith("."):
        return False
    
    return True

def show_timeline_display(timeline):
    console.print()
    title = Text("trail", style="bold cyan")
    subtitle = Text(" — your activity at a glance", style="dim")
    console.print(Panel(Text.assemble(title, subtitle), box=box.DOUBLE_EDGE))
    console.print()

    total_files = sum(1 for items in timeline.values() for i in items if i.get("source") == "files" and _is_useful_file(i))
    total_cmds = sum(1 for items in timeline.values() for i in items if i.get("source") == "history")
    stats = Text(f"📁 {total_files} files  ")
    stats.append(f"⌨️  {total_cmds} commands", style="dim")
    console.print(Panel(stats, box=box.SQUARE, style="dim"))
    console.print()

    all_commands = []
    for items in timeline.values():
        for i in items:
            if i["source"] == "history":
                all_commands.append(i)
    recent_commands = sorted(all_commands, key=lambda x: x.get("timestamp", 0), reverse=True)[:15]

    time_order = ["Today", "Yesterday", "This Week", "Last Week", "This Month", "Older"]
    
    for label in time_order:
        if label not in timeline:
            continue
        items = timeline[label]
        files_only = [i for i in items if i["source"] == "files" and _is_useful_file(i)]
        if not files_only:
            continue
        
        header = Text(f"  {label}", style="bold cyan")
        header.append(f"  ({len(files_only)} files)", style="dim")
        console.print(header)
        console.print("  " + "─" * 60)

        for item in files_only[:5]:
            ext = item.get("ext", "")
            icon = file_icon(ext)
            name = item["name"]
            size = format_size(item.get("size", 0))
            path = shorten_path(item["path"], 50)
            project = item.get("project")
            
            line = Text(f"    {icon} ", style="bold")
            line.append(f"{name}", style="white")
            if project:
                line.append(f"  [{project}]", style="blue")
            line.append(f"  {size}", style="dim")
            line.append(f"\n        {path}", style="dim")
            console.print(line)
        
        if len(files_only) > 5:
            console.print(f"    … and {len(files_only) - 5} more files", style="dim italic")
        
        console.print()

    if recent_commands:
        console.print(Text("  Recent Commands", style="bold yellow underline"))
        console.print("  " + "─" * 60)
        shown = 0
        for cmd_entry in recent_commands:
            cmd = cmd_entry["command"]
            cmd = cmd.split("\\\n")[0].split("\n")[0].strip()
            if not cmd or cmd in ("\\", "\"", "'", "`"):
                continue
            if len(cmd) > 90:
                cmd = cmd[:87] + "…"
            line = Text("    ⌨️  ", style="dim")
            line.append(f"{cmd}", style="yellow")
            console.print(line)
            shown += 1
            if shown >= 10:
                break
        console.print()

    console.print(Panel(
        "[bold]Quick tips:[/bold]\n"
        "  trail find <query>   — Search your activity\n"
        "  trail mark <name>    — Bookmark this directory\n"
        "  trail marks          — List all bookmarks",
        box=box.SQUARE, style="dim"
    ))

def show_search_results(query, files, history, bookmarks=None):
    console.print()
    title = Text(f"🔍  Searching for ", style="bold")
    title.append(f"'{query}'", style="cyan bold")
    console.print(Panel(title, box=box.DOUBLE_EDGE))
    console.print()
    
    total = len(files) + len(history) + (len(bookmarks) if bookmarks else 0)
    if total == 0:
        console.print(Panel("  No results found. Try a different search term.", style="yellow"))
        return
    
    console.print(f"  Found [bold]{total}[/bold] results\n")
    
    if bookmarks:
        console.print(Text("  BOOKMARKS", style="bold green underline"))
        for name, info in bookmarks.items():
            path = shorten_path(info["path"], 50)
            console.print(f"    🔖  [bold]{name}[/bold]  →  {path}")
        console.print()
    
    if files:
        console.print(Text("  FILES", style="bold blue underline"))
        for f in files[:10]:
            icon = file_icon(f.get("ext", ""))
            name = f["name"]
            path = shorten_path(f["path"], 50)
            project = f.get("project")
            line = Text(f"    {icon} ", style="bold")
            line.append(f"{name}", style="white")
            if project:
                line.append(f"  [{project}]", style="blue")
            line.append(f"\n        {path}", style="dim")
            console.print(line)
        if len(files) > 10:
            console.print(f"    … and {len(files) - 10} more files", style="dim italic")
        console.print()
    
    if history:
        console.print(Text("  COMMANDS", style="bold yellow underline"))
        for h in history[:10]:
            cmd = h["command"]
            if len(cmd) > 100:
                cmd = cmd[:97] + "…"
            console.print(f"    ⌨️  {cmd}")
        if len(history) > 10:
            console.print(f"    … and {len(history) - 10} more commands", style="dim italic")
        console.print()

def show_bookmarks(bookmarks):
    console.print()
    title = Text("🔖  Bookmarks", style="bold")
    console.print(Panel(title, box=box.DOUBLE_EDGE))
    console.print()
    
    if not bookmarks:
        console.print(Panel("  No bookmarks yet. Use [bold]trail mark <name>[/bold] to add one.", style="yellow"))
        return
    
    table = Table(box=box.SIMPLE)
    table.add_column("Name", style="cyan bold")
    table.add_column("Path", style="dim")
    table.add_column("Added", style="white")
    
    for name, info in bookmarks.items():
        added = datetime.fromtimestamp(info["added"]).strftime("%b %d")
        path = shorten_path(info["path"], 60)
        table.add_row(name, path, added)
    
    console.print(table)
    console.print()
    console.print(Panel(
        "[dim]Tip: Use [bold]trail go <name>[/bold] in your shell to jump to a bookmark\n"
        "      Add this to your shell: [bold]alias go='cd $(trail jump'[/bold]",
        box=box.SQUARE, style="dim"
    ))

def show_bookmark_added(name, message, success):
    if success:
        console.print(f"  ✅  [bold green]{message}[/bold green]")
    else:
        console.print(f"  ❌  [bold red]{message}[/bold red]")

def show_bookmark_removed(name, message, success):
    if success:
        console.print(f"  🗑  [bold]{message}[/bold]")
    else:
        console.print(f"  ❌  [bold red]{message}[/bold red]")

def show_tip():
    console.print()
    console.print(Panel(
        "  [bold cyan]trail[/bold cyan] — Your activity trail\n"
        "\n"
        "  [bold]trail[/bold]              Show your activity timeline\n"
        "  [bold]trail find[/bold] <query>  Search across files, commands, and bookmarks\n"
        "  [bold]trail mark[/bold] <name>   Bookmark the current directory\n"
        "  [bold]trail marks[/bold]         List all bookmarks\n"
        "  [bold]trail rm[/bold] <name>     Remove a bookmark\n"
        "  [bold]trail go[/bold] <name>     Print a bookmark's path (use with shell function)\n"
        "  [bold]trail --help[/bold]        Show this help",
        title="Usage", box=box.DOUBLE_EDGE
    ))
    console.print()

def show_jump(name, path, markdown=False):
    if path:
        text = str(path)
        if markdown:
            print(text, end="")
        else:
            console.print(f"  ➡  {text}")
    else:
        console.print(f"  ❌  Bookmark '{name}' not found")
