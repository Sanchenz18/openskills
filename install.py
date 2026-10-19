#!/usr/bin/env python3
"""Install skills from this repo into ~/.agents/skills.

Works on Windows and Linux, no matter where the repo was cloned.
Usage:
    python install.py              install (symlink preferred, copy fallback)
    python install.py --copy       force copy instead of symlink
    python install.py --uninstall  remove this repo's skills from ~/.agents/skills
"""

import argparse
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
SKILLS_DIR = REPO_ROOT / "skills"
TARGET_DIR = Path.home() / ".agents" / "skills"


def skill_names():
    if not SKILLS_DIR.is_dir():
        return []
    return sorted(p.name for p in SKILLS_DIR.iterdir() if not p.name.startswith("."))


def clear(dst: Path):
    if dst.is_symlink() or dst.is_file():
        dst.unlink()
    elif dst.is_dir():
        shutil.rmtree(dst)


def install_one(name: str, force_copy: bool) -> str:
    src = SKILLS_DIR / name
    dst = TARGET_DIR / name
    clear(dst)
    if not force_copy:
        try:
            dst.symlink_to(src, target_is_directory=src.is_dir())
            return "linked"
        except OSError:
            pass  # e.g. Windows without Developer Mode: fall back to copy
    if src.is_dir():
        shutil.copytree(src, dst)
    else:
        shutil.copy2(src, dst)
    return "copied (re-run install.py after git pull to update)"


def uninstall_one(name: str) -> str:
    dst = TARGET_DIR / name
    if not dst.exists() and not dst.is_symlink():
        return "not installed"
    clear(dst)
    return "removed"


def main() -> int:
    ap = argparse.ArgumentParser(description="Install openskills into ~/.agents/skills")
    ap.add_argument("--copy", action="store_true", help="copy files instead of symlinking")
    ap.add_argument("--uninstall", action="store_true", help="remove this repo's skills")
    args = ap.parse_args()

    names = skill_names()
    if not names:
        print("No skills found in", SKILLS_DIR)
        return 1
    TARGET_DIR.mkdir(parents=True, exist_ok=True)

    for name in names:
        if args.uninstall:
            print(f"{name}: {uninstall_one(name)}")
        else:
            print(f"{name}: {install_one(name, args.copy)}")
    print("done ->", TARGET_DIR)
    return 0


if __name__ == "__main__":
    sys.exit(main())
