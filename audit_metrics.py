import os, docx, pptx

base = r'c:\Users\LENOVO\.gemini\antigravity\scratch\AI-Movie-Recommendation-System\CineAI_College_Submission\Final_Deliverables'

def get_text_docx(path):
    d = docx.Document(path)
    p_text = " ".join(p.text for p in d.paragraphs)
    t_text = " ".join(c.text for t in d.tables for row in t.rows for c in row.cells)
    return p_text + " " + t_text

def get_text_pptx(path):
    p = pptx.Presentation(path)
    t = []
    for s in p.slides:
        for sh in s.shapes:
            if sh.has_text_frame:
                t.append(sh.text_frame.text)
    return " ".join(t)

docs = {
    "Report.docx": get_text_docx(os.path.join(base, "CineAI_Final_Project_Report.docx")),
    "Presentation.pptx": get_text_pptx(os.path.join(base, "CineAI_Project_Presentation.pptx")),
    "Viva.docx": get_text_docx(os.path.join(base, "CineAI_Viva_Questions_and_Answers.docx")),
    "Demo_Guide.docx": get_text_docx(os.path.join(base, "CineAI_Project_Demonstration_Guide.docx")),
    "Synopsis.docx": get_text_docx(os.path.join(base, "CineAI_Project_Synopsis.docx"))
}

metrics = {
    "0.9094 (RMSE)": "0.9094",
    "0.7015 (MAE)": "0.7015",
    "0.0072 (Precision@10)": "0.0072",
    "0.0056 (Recall@10)": "0.0056",
    "0.0157 (Coverage)": "0.0157",
    "14 (Automated Tests)": "14",
    "100,836 or 100k (Ratings)": "100",
    "9,742 or 9.7k (Movies)": "9,742"
}

print("=== METRIC CONSISTENCY CHECK ===")
for m_name, val in metrics.items():
    found_in = [doc_name for doc_name, text in docs.items() if val in text]
    print(f"Metric {m_name:26s} -> Found in {len(found_in)}/5 documents: {found_in}")
