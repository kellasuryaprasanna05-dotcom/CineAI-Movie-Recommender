import os
import zipfile

folder = r"C:\Users\LENOVO\.gemini\antigravity\scratch\AI-Movie-Recommendation-System\CineAI_COMPLETE_PROJECT_HANDOVER"
print("=== HANDOVER FOLDER CONTENTS ===")
for f in sorted(os.listdir(folder)):
    p = os.path.join(folder, f)
    sz = os.path.getsize(p)
    if f.endswith(".pdf"):
        with open(p, "rb") as fp:
            hdr = fp.read(8).decode("latin1", errors="ignore").strip()
            print(f"{f:<35} | {sz:>10} B | {sz/1024:>7.1f} KB | Header: {hdr}")
    elif f.endswith(".zip"):
        with zipfile.ZipFile(p) as zf:
            corrupt = zf.testzip()
            print(f"{f:<35} | {sz:>10} B | {sz/(1024*1024):>7.2f} MB | {len(zf.infolist())} entries | Corrupt: {corrupt}")
    else:
        print(f"{f:<35} | {sz:>10} B | {sz/1024:>7.1f} KB")

master_zip = r"C:\Users\LENOVO\.gemini\antigravity\scratch\AI-Movie-Recommendation-System\CineAI_COMPLETE_PROJECT_HANDOVER.zip"
print("\n=== MASTER ZIP ARCHIVE ===")
if os.path.exists(master_zip):
    sz = os.path.getsize(master_zip)
    with zipfile.ZipFile(master_zip) as zf:
        corrupt = zf.testzip()
        print(f"{os.path.basename(master_zip):<35} | {sz:>10} B | {sz/(1024*1024):>7.2f} MB | {len(zf.infolist())} entries | Corrupt: {corrupt}")
