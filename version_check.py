"""
version_check.py — Startup version check against GitHub main branch.
Uses git to compare local HEAD against origin/main.
"""
 
import os
import subprocess
import threading
 
_ROOT = os.path.dirname(os.path.abspath(__file__))
 
 
def check_for_update(on_update_available: callable):
    """
    Spawns a daemon thread. Calls on_update_available() if local HEAD
    is behind origin/main. Silent on failure — bad connections, no git, etc.
    """
    def _run():
        try:
            # Update remote refs without touching working files
            subprocess.run(
                ["git", "fetch", "--quiet"],
                cwd=_ROOT, capture_output=True, timeout=10
            )
 
            local = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=_ROOT, capture_output=True, text=True
            ).stdout.strip()
 
            remote = subprocess.run(
                ["git", "rev-parse", "origin/main"],
                cwd=_ROOT, capture_output=True, text=True
            ).stdout.strip()
 
            if local and remote and local != remote:
                on_update_available()
 
        except Exception:
            pass
 
    threading.Thread(target=_run, daemon=True).start()