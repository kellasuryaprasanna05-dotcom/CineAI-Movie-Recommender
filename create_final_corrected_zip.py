"""
Packages CineAI_FINAL_CORRECTED_SUBMISSION.zip and verifies its contents.
"""

import os
import zipfile

BASE_DIR = r"C:\Users\LENOVO\.gemini\antigravity\scratch\AI-Movie-Recommendation-System"
FINAL_ZIP_PATH = os.path.join(BASE_DIR, "CineAI_FINAL_CORRECTED_SUBMISSION.zip")
DELIV_DIR = os.path.join(BASE_DIR, "CineAI_College_Submission", "Final_Deliverables")
HANDOVER_DIR = os.path.join(BASE_DIR, "CineAI_COMPLETE_PROJECT_HANDOVER")
SCREENSHOTS_DIR = os.path.join(DELIV_DIR, "screenshots")

print(f"Creating master corrected submission package: {FINAL_ZIP_PATH}...")

with zipfile.ZipFile(FINAL_ZIP_PATH, "w", zipfile.ZIP_DEFLATED) as zf:
    # 1. Add Office Deliverables
    office_files = [
        "CineAI_Final_Project_Report.docx",
        "CineAI_Project_Presentation.pptx",
        "CineAI_Project_Synopsis.docx",
        "CineAI_Viva_Questions_and_Answers.docx",
        "CineAI_Project_Demonstration_Guide.docx",
        "TEAM_DETAILS_VERIFICATION.md",
        "FINAL_SUBMISSION_CHECKLIST.md"
    ]
    for f in office_files:
        src = os.path.join(DELIV_DIR, f)
        if os.path.exists(src):
            zf.write(src, arcname=f"College_Deliverables/{f}")
            print(f"  + Added College Deliverable: {f} ({os.path.getsize(src):,} bytes)")

    # 2. Add Handover Technical PDFs and Markdown
    handover_files = [
        "INSTALLATION_GUIDE.pdf",
        "PROJECT_ARCHITECTURE.pdf",
        "DATASET_DOCUMENTATION.pdf",
        "MACHINE_LEARNING_DOCUMENTATION.pdf",
        "MODEL_EVALUATION_REPORT.pdf",
        "API_AND_DATABASE_DOCUMENTATION.pdf",
        "VIVA_QUICK_REVISION.pdf",
        "PROJECT_HANDOVER_README.md",
        "FINAL_HANDOVER_CHECKLIST.md",
        "PROJECT_BACKUP.zip"
    ]
    for f in handover_files:
        src = os.path.join(HANDOVER_DIR, f)
        if os.path.exists(src):
            zf.write(src, arcname=f"Handover_Package/{f}")
            print(f"  + Added Handover Deliverable: {f} ({os.path.getsize(src):,} bytes)")

    # 3. Add Source of Truth Audit
    audit_file = os.path.join(BASE_DIR, "FINAL_TECHNICAL_CONSISTENCY_AUDIT.md")
    if os.path.exists(audit_file):
        zf.write(audit_file, arcname="FINAL_TECHNICAL_CONSISTENCY_AUDIT.md")
        print(f"  + Added Source of Truth: FINAL_TECHNICAL_CONSISTENCY_AUDIT.md ({os.path.getsize(audit_file):,} bytes)")

    # 4. Add UI Screenshots
    if os.path.exists(SCREENSHOTS_DIR):
        for img in sorted(os.listdir(SCREENSHOTS_DIR)):
            if img.endswith(".png"):
                src = os.path.join(SCREENSHOTS_DIR, img)
                zf.write(src, arcname=f"screenshots/{img}")
                print(f"  + Added Screenshot: {img}")

# Verify Master Corrected ZIP
print("\nVerifying archive integrity...")
with zipfile.ZipFile(FINAL_ZIP_PATH, "r") as zf:
    bad_file = zf.testzip()
    if bad_file:
        raise RuntimeError(f"Corrupt entry detected: {bad_file}")
    entries = zf.infolist()

sz = os.path.getsize(FINAL_ZIP_PATH)
print(f"\n[OK] Archive verified successfully!")
print(f"Location: {FINAL_ZIP_PATH}")
print(f"Size: {sz:,} bytes ({sz/(1024*1024):.2f} MB)")
print(f"Total Entries: {len(entries)}")
