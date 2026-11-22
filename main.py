"""Entry point: copy the pre-rendered poster to the output directory.

The poster itself is drawn by render.py (pure stdlib) and stored in the
repository as poster.png; this program only copies those exact bytes to
$MAKEFUN_OUTPUT_DIR/entry.png (default /output), so repeated runs are
byte-identical.
"""

import os
import shutil


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(here, "poster.png")
    if not os.path.isfile(src):
        raise FileNotFoundError("poster.png missing next to main.py: %s" % src)
    dst = os.path.join(out_dir, "entry.png")
    shutil.copyfile(src, dst)
    print("wrote %s (%d bytes)" % (dst, os.path.getsize(dst)))


if __name__ == "__main__":
    main()
