#!/usr/bin/env python3
"""Entry point for the 27 November 2026 one-page news poster.

The artwork ships beside this file as entry.png (produced by render.py).
Running this module copies that image into the directory named by the
MAKEFUN_OUTPUT_DIR environment variable, defaulting to /output, so the
harness can collect it as the entry's single output image.
"""

import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.join(HERE, "entry.png")
FALLBACK_DIR = "/output"


def output_path():
    folder = os.environ.get("MAKEFUN_OUTPUT_DIR") or FALLBACK_DIR
    return os.path.join(folder, "entry.png")


def main():
    target = output_path()
    folder = os.path.dirname(target)
    if folder:
        os.makedirs(folder, exist_ok=True)
    shutil.copyfile(SOURCE, target)
    size = os.path.getsize(target)
    print(f"entry.png -> {target} ({size} bytes)")


# Kept importable so a checker can call main() without a shell.


if __name__ == "__main__":
    main()
