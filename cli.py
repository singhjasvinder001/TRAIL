import sys
import os
import argparse

from trail.core import get_timeline, search_history, search_files, BookmarkManager
from trail.display import (
    show_timeline_display, show_search_results, show_bookmarks,
    show_bookmark_added, show_bookmark_removed, show_tip, show_jump
)
from trail import __version__

def main():
    parser = argparse.ArgumentParser(
        prog="trail",
        description="Your activity trail — never lose your context again.",
        add_help=False,
    )
    parser.add_argument("--version", action="store_true", help="Show version")
    parser.add_argument("--help", action="store_true", help="Show this help message")
    parser.add_argument("--markdown", action="store_true", help=argparse.SUPPRESS)
    
    subparsers = parser.add_subparsers(dest="command", metavar="")
    
    find_parser = subparsers.add_parser("find", help="Search your activity")
    find_parser.add_argument("query", nargs="?", help="Search term")
    
    mark_parser = subparsers.add_parser("mark", help="Bookmark a directory")
    mark_parser.add_argument("name", nargs="?", help="Bookmark name")
    mark_parser.add_argument("path", nargs="?", help="Path to bookmark (default: current dir)")
    
    rm_parser = subparsers.add_parser("rm", help="Remove a bookmark")
    rm_parser.add_argument("name", help="Bookmark name to remove")
    
    marks_parser = subparsers.add_parser("marks", help="List all bookmarks")
    
    go_parser = subparsers.add_parser("go", help="Print bookmark path for shell navigation")
    go_parser.add_argument("name", help="Bookmark name")
    
    args, extra = parser.parse_known_args()
    
    if args.help:
        show_tip()
        return
    
    if args.version:
        print(f"trail v{__version__}")
        return
    
    bm = BookmarkManager()
    
    if args.command == "find":
        query = args.query or " ".join(extra)
        if not query:
            print("Please provide a search term: trail find <query>")
            return
        results_files = search_files(query)
        results_history = search_history(query)
        results_bookmarks = bm.search(query)
        show_search_results(query, results_files, results_history, results_bookmarks)
    
    elif args.command == "mark":
        if args.name:
            success, msg = bm.add(args.name, args.path or os.getcwd())
            show_bookmark_added(args.name, msg, success)
        else:
            show_bookmarks(bm.list())
    
    elif args.command == "marks":
        show_bookmarks(bm.list())
    
    elif args.command == "rm":
        if args.name:
            success, msg = bm.remove(args.name)
            show_bookmark_removed(args.name, msg, success)
        else:
            show_bookmarks(bm.list())
    
    elif args.command == "go":
        info = bm.get(args.name)
        if info:
            show_jump(args.name, info["path"], markdown=args.markdown)
        else:
            show_jump(args.name, None)
    
    else:
        timeline = get_timeline(days=1, history_lines=300)
        show_timeline_display(timeline)

if __name__ == "__main__":
    main()
