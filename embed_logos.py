#!/usr/bin/env python3
"""
embed_logos.py  -  downloads every online logo (logo:"https://...") found in your
HTML file and embeds it inside the file as a small round-ready image.

Result: ONE self-contained file. No logos folder, and the logos never expire.

How to use (on your own computer, while the Facebook image links still work):
    1. Put this script in the same folder as  marketing-sites-fixed.html
    2. (Recommended) pip install pillow
    3. python embed_logos.py
    4. Open  marketing-sites-final.html
Optional:  python embed_logos.py input.html output.html
"""
import base64, io, re, sys, urllib.request

SRC = sys.argv[1] if len(sys.argv) > 1 else "marketing-sites-fixed.html"
DST = sys.argv[2] if len(sys.argv) > 2 else "marketing-sites-final.html"
SIZE = 168  # px, a bit larger than the 84px circle so it stays sharp on phones

try:
    from PIL import Image
except ImportError:
    Image = None
    print("Note: Pillow is not installed, so images will be embedded at full size.\n"
          "      Run  pip install pillow  for much smaller files.\n")

def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read(), (r.headers.get_content_type() or "image/jpeg")

def to_data_uri(raw, mime):
    if Image is not None:
        im = Image.open(io.BytesIO(raw)).convert("RGB")
        w, h = im.size
        side = min(w, h)
        im = im.crop(((w - side) // 2, (h - side) // 2, (w + side) // 2, (h + side) // 2))
        im = im.resize((SIZE, SIZE), Image.LANCZOS)
        buf = io.BytesIO()
        im.save(buf, "JPEG", quality=85, optimize=True)
        raw, mime = buf.getvalue(), "image/jpeg"
    return "data:%s;base64,%s" % (mime, base64.b64encode(raw).decode())

html = open(SRC, encoding="utf-8").read()
pattern = re.compile(r'logo:"((?:https?|file)://[^"]+)"')
ok = bad = 0

def repl(m):
    global ok, bad
    url = m.group(1)
    try:
        raw, mime = fetch(url)
        uri = to_data_uri(raw, mime)
        ok += 1
        print("OK   ", url[:70] + "...")
        return 'logo:"%s"' % uri
    except Exception as e:
        bad += 1
        print("FAIL ", url[:70] + "...", "->", e)
        return m.group(0)

html = pattern.sub(repl, html)
open(DST, "w", encoding="utf-8").write(html)
print("\nDone: %d embedded, %d failed. Saved as %s" % (ok, bad, DST))
if bad:
    print("Failed logos keep their old link. Re-copy a fresh image address for those and run again.")
