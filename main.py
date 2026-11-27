"""Entry program for make.fun bounty news-image-20261127.

"Sum up 27 November's world news in one image": the poster was rendered
ahead of time by render.py into entry.png, which sits next to this
file. This program copies that image to the output directory the
grader reads: $MAKEFUN_OUTPUT_DIR/entry.png when the variable is set,
else /output/entry.png.

Python 3 standard library only. No network access. Deterministic: the
output bytes are exactly the bytes of the bundled entry.png.
"""

import os
import shutil
import sys


def resolve_output_dir() -> str:
    return os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"


def main() -> int:
    here = os.path.dirname(os.path.abspath(__file__))
    source = os.path.join(here, "entry.png")
    if not os.path.isfile(source):
        print("entry.png is missing beside main.py", file=sys.stderr)
        return 1
    out_dir = resolve_output_dir()
    os.makedirs(out_dir, exist_ok=True)
    target = os.path.join(out_dir, "entry.png")
    shutil.copyfile(source, target)
    # The grader runs the program twice and compares bytes: fail loudly
    # rather than hand over a truncated copy.
    if os.path.getsize(target) != os.path.getsize(source):
        print("copied entry.png has the wrong size", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
