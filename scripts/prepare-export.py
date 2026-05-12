#!/usr/bin/env python3
"""
Pre-process an Obsidian markdown file before obsidian-export:
- Replace ![[name.excalidraw]] with ![[name.excalidraw.png]] or .svg
  if a matching file exists in the same directory.
- Copy patched file + referenced assets into a temp directory.
- Run obsidian-export from the temp directory.
- Original files are never modified; temp dir is cleaned up on exit.
"""

import re
import sys
import os
import shutil
import tempfile
import subprocess
from pathlib import Path


EXCALIDRAW_RE = re.compile(r"!\[\[([^\]]+\.excalidraw)\]\]")


def fix_excalidraw_refs(content: str, source_dir: Path) -> tuple[str, list[Path], list[str]]:
    """
    Returns (fixed_content, resolved_asset_paths, unresolved_warnings).
    """
    assets: list[Path] = []
    warnings: list[str] = []

    def replace(m):
        ref = m.group(1)  # e.g. "阶段.excalidraw"
        for ext in (".png", ".svg"):
            candidate = source_dir / (ref + ext)
            if candidate.exists():
                assets.append(candidate)
                return f"![[{ref}{ext}]]"
        warnings.append(ref)
        return m.group(0)

    fixed = EXCALIDRAW_RE.sub(replace, content)
    return fixed, assets, warnings


def main():
    if len(sys.argv) < 3:
        print("Usage: prepare-export.py <source.md> <destination>")
        sys.exit(1)

    source = Path(sys.argv[1]).resolve()
    destination = Path(sys.argv[2])

    if not source.exists():
        print(f"Error: source file not found: {source}", file=sys.stderr)
        sys.exit(1)

    content = source.read_text(encoding="utf-8")
    fixed, assets, warnings = fix_excalidraw_refs(content, source.parent)

    if warnings:
        print("Note: no .png/.svg found for these excalidraw embeds (left as-is):")
        for w in warnings:
            print(f"  {w}")

    tmpdir = Path(tempfile.mkdtemp(prefix="obsidian-export-"))
    try:
        # Write patched markdown with original filename
        tmp_md = tmpdir / source.name
        tmp_md.write_text(fixed, encoding="utf-8")

        # Copy referenced assets next to the markdown
        for asset in assets:
            shutil.copy2(asset, tmpdir / asset.name)

        obsidian_export = Path(os.path.expandvars("$HOME/.cargo/bin/obsidian-export"))
        if not obsidian_export.exists():
            obsidian_export = Path("obsidian-export")

        dest_dir = destination.parent
        dest_dir.mkdir(parents=True, exist_ok=True)

        # Use tmpdir as vault + --start-at so obsidian-export can resolve
        # assets (PNG/SVG) that sit next to the patched markdown file.
        result = subprocess.run(
            [str(obsidian_export), str(tmpdir), "--start-at", str(tmp_md), str(dest_dir)],
            capture_output=True,
            text=True,
        )
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)

        if result.returncode == 0:
            # obsidian-export writes <dest_dir>/<source.name>; rename if destination differs
            produced = dest_dir / source.name
            if produced != destination and produced.exists():
                produced.rename(destination)
            # Copy assets to destination directory
            for asset in assets:
                shutil.copy2(asset, dest_dir / asset.name)
            print(f"Exported: {destination}")
            if assets:
                print(f"Assets copied: {[a.name for a in assets]}")

        sys.exit(result.returncode)

    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


if __name__ == "__main__":
    main()
