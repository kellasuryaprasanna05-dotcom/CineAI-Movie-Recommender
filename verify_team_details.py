import os, re, docx, pptx

base = r"c:\Users\LENOVO\.gemini\antigravity\scratch\AI-Movie-Recommendation-System\CineAI_College_Submission\Final_Deliverables"

docs = {
    "Report": os.path.join(base, "CineAI_Final_Project_Report.docx"),
    "Presentation": os.path.join(base, "CineAI_Project_Presentation.pptx"),
    "Synopsis": os.path.join(base, "CineAI_Project_Synopsis.docx"),
    "Viva": os.path.join(base, "CineAI_Viva_Questions_and_Answers.docx"),
    "Demo Guide": os.path.join(base, "CineAI_Project_Demonstration_Guide.docx")
}

def get_docx_text(path):
    d = docx.Document(path)
    paras = [p.text for p in d.paragraphs]
    tables = [c.text for t in d.tables for row in t.rows for c in row.cells]
    return " \n ".join(paras + tables)

def get_pptx_text(path):
    prs = pptx.Presentation(path)
    slides = []
    for s in prs.slides:
        for sh in s.shapes:
            if sh.has_text_frame:
                slides.append(sh.text_frame.text)
    return " \n ".join(slides)

print("="*70)
print("VERIFICATION OF TEAM DETAILS ACROSS DELIVERABLES")
print("="*70)

students = [
    ("Nella Navven", "12510519"),
    ("Kella Suryaprasanna", "12516522"),
    ("Charanya Bhandari", "12512578")
]
guide = "Abhikesh"

# 1. Check Report
print("\n1. CineAI_Final_Project_Report.docx:")
rep_text = get_docx_text(docs["Report"])
for name, roll in students:
    assert name in rep_text, f"Missing name {name} in Report"
    assert roll in rep_text, f"Missing roll {roll} in Report"
    print(f"  [PASS] Found {name} (Roll: {roll})")
assert guide in rep_text, f"Missing guide {guide} in Report"
print(f"  [PASS] Found Project Guide: {guide}")

# Check plural phrasing
assert "We hereby declare" in rep_text, "Declaration should use plural 'We hereby declare'"
print("  [PASS] Candidate declaration uses plural 'We hereby declare'")
assert "our own" in rep_text, "Declaration should use 'our own'"
print("  [PASS] Certificate/Declaration uses team wording ('our own')")

# Check images & tables in report
rep_doc = docx.Document(docs["Report"])
img_count = sum(1 for p in rep_doc.paragraphs for r in p.runs if 'graphic' in r._r.xml)
print(f"  [PASS] Embedded Screenshots in Report: {img_count} (Expected: 9)")
assert img_count == 9, f"Expected 9 images, found {img_count}"
print(f"  [PASS] Tables in Report: {len(rep_doc.tables)}")

# 2. Check Presentation
print("\n2. CineAI_Project_Presentation.pptx:")
ppt_prs = pptx.Presentation(docs["Presentation"])
slide_count = len(ppt_prs.slides)
print(f"  [PASS] Slide Count: {slide_count} (Expected: 18)")
assert slide_count == 18, f"Expected 18 slides, found {slide_count}"
ppt_text = get_pptx_text(docs["Presentation"])
for name, roll in students:
    assert name in ppt_text, f"Missing name {name} in Presentation"
    assert roll in ppt_text, f"Missing roll {roll} in Presentation"
    print(f"  [PASS] Found {name} (Roll: {roll})")
assert guide in ppt_text, f"Missing guide {guide} in Presentation"
print(f"  [PASS] Found Project Guide: {guide}")

# Check slide 1 and slide 18
s1_text = " ".join(sh.text_frame.text for sh in ppt_prs.slides[0].shapes if sh.has_text_frame)
for name, roll in students:
    assert name in s1_text and roll in s1_text, f"Slide 1 missing {name}"
print("  [PASS] Title Slide 1 contains all 3 team members and roll numbers")

s18_text = " ".join(sh.text_frame.text for sh in ppt_prs.slides[17].shapes if sh.has_text_frame)
for name, roll in students:
    assert name in s18_text and roll in s18_text, f"Slide 18 missing {name}"
print("  [PASS] Concluding Slide 18 contains all 3 team members and guide")

# 3. Check Synopsis
print("\n3. CineAI_Project_Synopsis.docx:")
syn_text = get_docx_text(docs["Synopsis"])
for name, roll in students:
    assert name in syn_text, f"Missing name {name} in Synopsis"
    assert roll in syn_text, f"Missing roll {roll} in Synopsis"
    print(f"  [PASS] Found {name} (Roll: {roll})")
assert guide in syn_text, f"Missing guide {guide} in Synopsis"
print(f"  [PASS] Found Project Guide: {guide}")

# 4. Check for old placeholders in all docs
old_placeholders = [
    "[Student Name 1]", "[Student Name 2]", "[Student Name 3]", "[Student Name(s)]",
    "[Your Name]", "[Roll No 1]", "[Roll No 2]", "[Roll No 3]", "[Roll Number]",
    "[Roll No(s)]", "[Guide Name]", "[Project Supervisor / Guide Name]"
]

print("\n4. Scanning for unreplaced student/roll/guide placeholders across all 5 documents:")
total_old = 0
for dname, dpath in docs.items():
    text = get_docx_text(dpath) if dpath.endswith(".docx") else get_pptx_text(dpath)
    found_in_doc = [p for p in old_placeholders if p.lower() in text.lower()]
    if found_in_doc:
        print(f"  [FAIL] {dname} contains: {found_in_doc}")
        total_old += len(found_in_doc)
    else:
        print(f"  [PASS] {dname}: 0 old student/roll/guide placeholders remaining.")

assert total_old == 0, f"Found {total_old} unreplaced student/guide placeholders!"

print("\n" + "="*70)
print("ALL TEAM DETAILS VERIFIED SUCCESSFULLY!")
print("="*70)
