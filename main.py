#!/usr/bin/env python3
"""Entry point for the news-image-20261127 entry (v3, 48 stories).

Copies the pre-rendered poster (entry.png, produced by render.py) into the
output directory the harness designates via MAKEFUN_OUTPUT_DIR, falling back
to /output/entry.png. The poster is deterministic: render.py run twice
yields a byte-identical entry.png.
"""

import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "entry.png")
MAX_BYTES = 1_048_576


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    dst = os.path.join(out_dir, "entry.png")
    size = os.path.getsize(SRC)
    if size > MAX_BYTES:
        print(f"entry.png too large: {size} bytes > {MAX_BYTES}", file=sys.stderr)
        return 1
    shutil.copyfile(SRC, dst)
    written = os.path.getsize(dst)
    if written != size:
        print(f"copy mismatch: source {size} bytes, wrote {written}", file=sys.stderr)
        return 1
    print(f"wrote {dst} ({written} bytes, verified)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
