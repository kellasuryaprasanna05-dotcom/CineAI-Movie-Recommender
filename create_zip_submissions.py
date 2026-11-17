"""
Creates the two official CineAI college submission ZIP packages:
1. CineAI_Final_Submission.zip
2. CineAI_Source_Code.zip

Excludes __pycache__, .pyc, and temporary files.
Verifies ZIP integrity and lists archive contents.
"""
import os
import zipfile
import sys

BASE_DIR = r"c:\Users\LENOVO\.gemini\antigravity\scratch\AI-Movie-Recommendation-System"
DELIVERABLES_DIR = os.path.join(BASE_DIR, "CineAI_College_Submission", "Final_Deliverables")
ZIP_OUTPUT_DIR = os.path.join(BASE_DIR, "Final_ZIP_Submission")

os.makedirs(ZIP_OUTPUT_DIR, exist_ok=True)

FINAL_SUBMISSION_ZIP = os.path.join(ZIP_OUTPUT_DIR, "CineAI_Final_Submission.zip")
SOURCE_CODE_ZIP = os.path.join(ZIP_OUTPUT_DIR, "CineAI_Source_Code.zip")

def build_final_submission_zip():
    print(f"\nBuilding {FINAL_SUBMISSION_ZIP}...")
    files_to_add = [
        "CineAI_Final_Project_Report.docx",
        "CineAI_Project_Presentation.pptx",
        "CineAI_Project_Synopsis.docx",
        "CineAI_Viva_Questions_and_Answers.docx",
        "CineAI_Project_Demonstration_Guide.docx",
        "TEAM_DETAILS_VERIFICATION.md",
        "FINAL_SUBMISSION_CHECKLIST.md"
    ]
    
    with zipfile.ZipFile(FINAL_SUBMISSION_ZIP, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
        # Add root deliverables
        for fname in files_to_add:
            fpath = os.path.join(DELIVERABLES_DIR, fname)
            if os.path.exists(fpath):
                zf.write(fpath, arcname=fname)
                print(f"  + Added: {fname} ({os.path.getsize(fpath):,} bytes)")
            else:
                print(f"  ! Missing file: {fname}")
                
        # Add screenshots folder
        screenshots_dir = os.path.join(DELIVERABLES_DIR, "screenshots")
        if os.path.exists(screenshots_dir):
            for sname in sorted(os.listdir(screenshots_dir)):
                if sname.endswith(".png"):
                    spath = os.path.join(screenshots_dir, sname)
                    arc_name = os.path.join("screenshots", sname)
                    zf.write(spath, arcname=arc_name)
                    print(f"  + Added: {arc_name} ({os.path.getsize(spath):,} bytes)")

    size = os.path.getsize(FINAL_SUBMISSION_ZIP)
    print(f"[OK] {FINAL_SUBMISSION_ZIP} created successfully ({size:,} bytes / {size/(1024*1024):.2f} MB)")

def build_source_code_zip():
    print(f"\nBuilding {SOURCE_CODE_ZIP}...")
    
    # Specific inclusion folders and root files
    include_root_files = [
        "app.py",
        "train_model.py",
        "download_data.py",
        "verify_system.py",
        "requirements.txt",
        "README.md"
    ]
    
    include_folders = [
        ".streamlit",
        "assets",
        "src",
        "models",
        "data",
        "database",
        "docs",
        "tests"
    ]
    
    exclude_extensions = {".pyc", ".pyo", ".tmp", ".log"}
    exclude_dirs = {"__pycache__", ".git", ".pytest_cache", "Final_ZIP_Submission", "Original_Backups"}
    
    with zipfile.ZipFile(SOURCE_CODE_ZIP, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
        # 1. Add root files
        for fname in include_root_files:
            fpath = os.path.join(BASE_DIR, fname)
            if os.path.exists(fpath):
                zf.write(fpath, arcname=fname)
                print(f"  + Added: {fname}")
                
        # 2. Add folders
        for folder in include_folders:
            folder_path = os.path.join(BASE_DIR, folder)
            if not os.path.exists(folder_path):
                continue
                
            for root, dirs, files in os.walk(folder_path):
                # Filter out excluded directories in-place
                dirs[:] = [d for d in dirs if d not in exclude_dirs]
                
                for file in files:
                    _, ext = os.path.splitext(file)
                    if ext.lower() in exclude_extensions:
                        continue
                    if file.startswith(".~"): # temp office lock files
                        continue
                    
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, BASE_DIR)
                    zf.write(full_path, arcname=rel_path)
                    print(f"  + Added: {rel_path}")

    size = os.path.getsize(SOURCE_CODE_ZIP)
    print(f"[OK] {SOURCE_CODE_ZIP} created successfully ({size:,} bytes / {size/(1024*1024):.2f} MB)")

def verify_zip_archives():
    print("\n" + "="*60)
    print("VERIFYING GENERATED ZIP ARCHIVES")
    print("="*60)
    
    archives = [FINAL_SUBMISSION_ZIP, SOURCE_CODE_ZIP]
    for arch in archives:
        print(f"\nInspecting: {arch}")
        assert os.path.exists(arch), f"Archive missing: {arch}"
        with zipfile.ZipFile(arch, 'r') as zf:
            # testzip returns None on success, or the name of first corrupt file
            corrupt = zf.testzip()
            assert corrupt is None, f"Corrupt file found in {arch}: {corrupt}"
            
            infolist = zf.infolist()
            total_uncompressed = sum(info.file_size for info in infolist)
            compressed_size = os.path.getsize(arch)
            print(f"  Status: Integrity Test PASSED [OK]")
            print(f"  Total Files in Archive: {len(infolist)}")
            print(f"  Compressed Size: {compressed_size:,} bytes ({compressed_size/(1024*1024):.2f} MB)")
            print(f"  Uncompressed Size: {total_uncompressed:,} bytes ({total_uncompressed/(1024*1024):.2f} MB)")
            print("  Archive Contents Sample:")
            for item in infolist[:15]:
                print(f"    - {item.filename:45s} ({item.file_size:,} bytes)")
            if len(infolist) > 15:
                print(f"    ... and {len(infolist) - 15} more files.")

if __name__ == "__main__":
    build_final_submission_zip()
    build_source_code_zip()
    verify_zip_archives()
