import os, re, docx, pptx

base = r'c:\Users\LENOVO\.gemini\antigravity\scratch\AI-Movie-Recommendation-System\CineAI_College_Submission\Final_Deliverables'

def find_placeholders(text):
    return re.findall(r'\[[A-Za-z0-9\s/–—]+\]', text)

docs = {
    "Report.docx": r"c:\Users\LENOVO\.gemini\antigravity\scratch\AI-Movie-Recommendation-System\CineAI_College_Submission\Final_Deliverables\CineAI_Final_Project_Report.docx",
    "Presentation.pptx": r"c:\Users\LENOVO\.gemini\antigravity\scratch\AI-Movie-Recommendation-System\CineAI_College_Submission\Final_Deliverables\CineAI_Project_Presentation.pptx",
    "Viva.docx": r"c:\Users\LENOVO\.gemini\antigravity\scratch\AI-Movie-Recommendation-System\CineAI_College_Submission\Final_Deliverables\CineAI_Viva_Questions_and_Answers.docx",
    "Demo_Guide.docx": r"c:\Users\LENOVO\.gemini\antigravity\scratch\AI-Movie-Recommendation-System\CineAI_College_Submission\Final_Deliverables\CineAI_Project_Demonstration_Guide.docx",
    "Synopsis.docx": r"c:\Users\LENOVO\.gemini\antigravity\scratch\AI-Movie-Recommendation-System\CineAI_College_Submission\Final_Deliverables\CineAI_Project_Synopsis.docx"
}

for name, path in docs.items():
    if name.endswith('.docx'):
        d = docx.Document(path)
        txt = " ".join(p.text for p in d.paragraphs) + " " + " ".join(c.text for t in d.tables for r in t.rows for c in r.cells)
    else:
        p = pptx.Presentation(path)
        txt = " ".join(sh.text_frame.text for s in p.slides for sh in s.shapes if sh.has_text_frame)
    
    matches = set(find_placeholders(txt))
    print(f"\n{name} Placeholders ({len(matches)}):")
    for m in sorted(matches):
        print(f"  • {m}")
