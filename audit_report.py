import docx

path = r'c:\Users\LENOVO\.gemini\antigravity\scratch\AI-Movie-Recommendation-System\CineAI_College_Submission\Final_Deliverables\CineAI_Final_Project_Report.docx'
doc = docx.Document(path)

print("Major Headings:")
for p in doc.paragraphs:
    if p.text.startswith("CHAPTER") or p.text in ["CERTIFICATE OF ORIGINALITY", "CANDIDATE'S DECLARATION", "ACKNOWLEDGMENTS", "ABSTRACT", "TABLE OF CONTENTS", "REFERENCES & BIBLIOGRAPHY"]:
        print("  •", p.text)

print("\nFormulas:")
for t in doc.tables:
    for row in t.rows:
        for cell in row.cells:
            for p in cell.paragraphs:
                txt = p.text.strip()
                if "Eq." in txt or "Soup_i" in txt or "TF-IDF" in txt or "WR =" in txt or "Score_hybrid" in txt or "u_profile" in txt or "Sim_" in txt:
                    print("  fx:", txt)

img_count = 0
for p in doc.paragraphs:
    for r in p.runs:
        if "graphic" in r._r.xml:
            img_count += 1
print(f"\nTotal Embedded Images found: {img_count}")
