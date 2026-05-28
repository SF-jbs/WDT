"""
version_check.py — Startup version check against GitHub main branch.
Uses git to compare local HEAD against origin/main.
"""
 
import os
import subprocess
import threading
import json
from tkinter import messagebox
 
_ROOT = os.path.dirname(os.path.abspath(__file__))
 
def _get_repo_url():
    try:
        with open(os.path.join(_ROOT, "settings.json"), "r") as f:
            data = json.load(f)
            return data.get("version_check_repo")
    except Exception:
        return None

 
def check_for_update(on_update_available: callable):
    """
    Spawns a daemon thread. Calls on_update_available() if local HEAD
    is behind origin/main. Silent on failure — bad connections, no git, etc.
    """
    def _run():
        try:
            repo_url = _get_repo_url()

            # If no repo specified, fall back to current behavior
            if not repo_url:
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

            else:
                # Fetch the target repo's main branch without changing remotes
                subprocess.run(
                    ["git", "fetch", "--quiet", repo_url, "main"],
                    cwd=_ROOT, capture_output=True, timeout=10
                )

                local = subprocess.run(
                    ["git", "rev-parse", "HEAD"],
                    cwd=_ROOT, capture_output=True, text=True
                ).stdout.strip()

                remote = subprocess.run(
                    ["git", "rev-parse", "FETCH_HEAD"],
                    cwd=_ROOT, capture_output=True, text=True
                ).stdout.strip()

            print(f"[VersionCheck] local:  {local}")
            print(f"[VersionCheck] remote: {remote}")

            if local and remote:
                print(f"[VersionCheck] match: {local == remote}")
            else:
                print("[VersionCheck] missing values")

            if local and remote and local != remote:
                print("[VersionCheck] UPDATE AVAILABLE")
                messagebox.showwarning("UPDATE AVAILABLE",
                                   "Pull from your teams main to get the latest version.")
                on_update_available()
            else:
                print("[VersionCheck] up to date or unable to compare")

        except Exception:
            pass

    threading.Thread(target=_run, daemon=True).start()
