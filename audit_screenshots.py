import os
from PIL import Image

base = r'c:\Users\LENOVO\.gemini\antigravity\scratch\AI-Movie-Recommendation-System\CineAI_College_Submission\Final_Deliverables\screenshots'
files = sorted([f for f in os.listdir(base) if f.endswith('.png')])

print(f"=== AUDITING {len(files)} SCREENSHOTS ===")
for f in files:
    path = os.path.join(base, f)
    size = os.path.getsize(path)
    im = Image.open(path)
    w, h = im.size
    colors = len(im.getcolors(maxcolors=1000000) or [])
    
    # Verify non-trivial rendering
    assert size > 50000, f"Screenshot {f} is suspiciously small: {size} bytes"
    assert w >= 1200 and h >= 700, f"Unexpected dimensions: {w}x{h}"
    assert colors > 500, f"Too few colors ({colors}), likely blank"
    
    print(f"[PASS] {f:38s} | {size:7,d} bytes | {w}x{h} | {colors:,} unique colors")
