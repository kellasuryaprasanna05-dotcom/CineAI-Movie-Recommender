import os, re, docx, pptx

base = r'c:\Users\LENOVO\.gemini\antigravity\scratch\AI-Movie-Recommendation-System\CineAI_College_Submission\Final_Deliverables'

docs = {
    "1. CineAI_Final_Project_Report.docx": os.path.join(base, "CineAI_Final_Project_Report.docx"),
    "2. CineAI_Project_Presentation.pptx": os.path.join(base, "CineAI_Project_Presentation.pptx"),
    "3. CineAI_Viva_Questions_and_Answers.docx": os.path.join(base, "CineAI_Viva_Questions_and_Answers.docx"),
    "4. CineAI_Project_Demonstration_Guide.docx": os.path.join(base, "CineAI_Project_Demonstration_Guide.docx"),
    "5. CineAI_Project_Synopsis.docx": os.path.join(base, "CineAI_Project_Synopsis.docx")
}

def extract_docx(p):
    d = docx.Document(p)
    text = " ".join(para.text for para in d.paragraphs)
    text += " " + " ".join(c.text for t in d.tables for row in t.rows for c in row.cells)
    return text

def extract_pptx(p):
    prs = pptx.Presentation(p)
    text = " ".join(sh.text_frame.text for s in prs.slides for sh in s.shapes if sh.has_text_frame)
    return text

# Targeted regex for personal information brackets
pattern = re.compile(r'\[(Student Name[^\]]*|Roll No[^\]]*|Guide Name[^\]]*|Candidate Name[^\]]*|Project Supervisor[^\]]*|Designation[^\]]*)\]', re.IGNORECASE)

print("="*65)
print("AUDITING PERSONAL-INFORMATION PLACEHOLDERS IN OFFICE DOCUMENTS")
print("="*65)

total_found = 0
for name, path in docs.items():
    text = extract_docx(path) if path.endswith('.docx') else extract_pptx(path)
    matches = pattern.findall(text)
    total_found += len(matches)
    print(f"\n{name}:")
    if matches:
        print(f"  Found {len(matches)} personal information placeholders:")
        for m in sorted(set(matches)):
            count = matches.count(m)
            print(f"    • [{m}] (occurrences: {count})")
    else:
        print("  Zero personal information placeholders found. Clean!")

print("\n" + "="*65)
print(f"TOTAL PERSONAL INFORMATION PLACEHOLDERS IDENTIFIED: {total_found}")
print("="*65)
