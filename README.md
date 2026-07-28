# trail

**Your developer activity trail — never lose your context again.**

Stop wasting mental energy reconstructing what you were doing, searching through shell history, or navigating deep directory trees. `trail` remembers for you.

## The Problem

Every developer loses hours each week to context-switching overhead:

- You switch between projects and spend minutes figuring out where you left off
- You vaguely remember running a specific command "last week" but can't find it
- You have important directories scattered everywhere with no quick way to reach them
- At end of day, you struggle to remember what you actually accomplished

These are tiny friction points — but they compound across hundreds of switches per day, costing **hours of lost flow state every week**.

## Three Major Quality-of-Life Improvements

### 1. `trail` — Activity Timeline (Stop Asking "What Was I Doing?")

One command shows you everything you've touched today: recent files grouped by time period, file types at a glance, project context, and your most recent shell commands. Context-switch with zero ramp-up.

```
$ trail
╔══════════════════════════════════════╗
║ trail — your activity at a glance    ║
╚══════════════════════════════════════╝

  Today  (7 files)
  ────────────────────────────────────────────
    🐍 run.py          [project-x]  856.0B
        ~/project-x/run.py
    📜 build.sh        [project-x]  4.1K
        ~/project-x/build.sh
    📝 design.md       [project-x]  2.3K
        ~/project-x/docs/design.md
    ...

  Recent Commands
  ────────────────────────────────────────────
    ⌨️  git push origin main
    ⌨️  npm run build
    ⌨️  curl -X POST https://api.example.com/deploy
```

**Why this matters:** Your brain has limited context capacity. Offload the "what was I doing?" question to a tool so you can focus on what's next.

### 2. `trail find <query>` — Universal Search (Stop Digging)

Search across your recent files, shell command history, and bookmarks from one place. Results are ranked and grouped by category — no more digging through three different tools to find what you need.

```
$ trail find deploy
  Found 5 results

  COMMANDS
    ⌨️  ./deploy.sh staging
    ⌨️  kubectl apply -f deployment.yaml
    ⌨️  npm run deploy

  FILES
    🐍 deploy.py  [project-x]
        ~/project-x/deploy.py
```

**Why this matters:** Finding something you've worked with recently should be instant. Your shell history knows what you did, Spotlight knows what files you touched — `trail` brings them together.

### 3. `trail mark <name>` — Smart Bookmarks (Stop Typing Long Paths)

Bookmark directories with memorable names and jump to them with a single command. No more `cd ~/path/to/some/deeply/nested/project/build/scripts`.

```
$ trail mark my-project
  ✅ Bookmarked 'my-project' → /Users/you/work/project-x/build/scripts

$ trail go my-project
  /Users/you/work/project-x/build/scripts
```

Add the shell function to your `~/.zshrc` for instant navigation:
```bash
function go() {
  local target=$(trail go --markdown "$1" 2>/dev/null)
  if [ -n "$target" ]; then
    cd "$target"
  fi
}
```

**Why this matters:** Directory navigation is one of the most frequent actions in a terminal. Saving 2 seconds per navigation × 50 navigations per day = 40+ hours saved per year.

## Quick Start

```bash
# Install
pip install rich
pip install -e .

# See your activity
trail

# Search everything
trail find <query>

# Bookmark a directory
trail mark <name>

# List bookmarks
trail marks

# Navigate (with shell function)
go <name>

# Remove bookmark
trail rm <name>
```

## How It Works

| Component | Technology |
|-----------|-----------|
| Recent files | macOS Spotlight (`mdfind`) — zero-config, already indexed |
| Command history | Parses `~/.zsh_history` with reverse-chronological ordering |
| Bookmarks | JSON store at `~/.trail/bookmarks.json` |
| Terminal UI | `rich` library — colors, tables, panels, emoji icons |

For better history tracking, add to `~/.zshrc`:
```bash
setopt EXTENDED_HISTORY
export HISTFILE="$HOME/.zsh_history"
export HISTSIZE=10000
export SAVEHIST=10000
```

## Requirements

- Python 3.10+
- macOS (uses Spotlight file indexing)
- `rich` library (`pip install rich`)

## License

MIT

---

> *"The most profound technologies are those that disappear. They weave themselves into the fabric of everyday life until they are indistinguishable from it."* — Mark Weiser
