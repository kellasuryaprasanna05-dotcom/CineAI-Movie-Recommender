"""
Builds the complete CineAI_Project_Synopsis.docx from PROJECT_SYNOPSIS.md.
"""
import os
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

BASE_DIR = r"c:\Users\LENOVO\.gemini\antigravity\scratch\AI-Movie-Recommendation-System"
SUB_DIR = os.path.join(BASE_DIR, "CineAI_College_Submission")
OUT_DIR = os.path.join(SUB_DIR, "Final_Deliverables")
DOCX_PATH = os.path.join(OUT_DIR, "CineAI_Project_Synopsis.docx")

def set_cell_background(cell, color_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{color_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=80, bottom=80, left=120, right=120):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
    tcPr.append(tcMar)

def add_header_footer(doc):
    for s in doc.sections:
        s.top_margin = Inches(0.8)
        s.bottom_margin = Inches(0.8)
        s.left_margin = Inches(0.8)
        s.right_margin = Inches(0.8)
        
        # Header
        header = s.header
        hp = header.paragraphs[0]
        hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        hrun = hp.add_run("CineAI: Official Major Project Synopsis  •  Department of CSE")
        hrun.font.name = "Calibri"
        hrun.font.size = Pt(8.5)
        hrun.font.color.rgb = RGBColor(120, 144, 156)
        
        # Footer
        footer = s.footer
        fp = footer.paragraphs[0]
        fp.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        frun = fp.add_run("B.Tech / B.S. Major Project Review Committee  •  Session 2025–2026")
        frun.font.name = "Calibri"
        frun.font.size = Pt(8.5)
        frun.font.color.rgb = RGBColor(120, 144, 156)

def format_p(p, space_before=0, space_after=4, line_spacing=1.15):
    p.paragraph_format.space_before = Pt(space_before)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = line_spacing

def add_heading_1(doc, text):
    p = doc.add_paragraph()
    format_p(p, space_before=12, space_after=4)
    run = p.add_run(text)
    run.font.name = "Arial"
    run.font.size = Pt(13)
    run.font.bold = True
    run.font.color.rgb = RGBColor(26, 54, 93)
    return p

def add_body(doc, text, bold_prefix=None):
    p = doc.add_paragraph()
    format_p(p, space_before=0, space_after=4, line_spacing=1.15)
    if bold_prefix:
        r_pre = p.add_run(bold_prefix)
        r_pre.font.name = "Calibri"
        r_pre.font.size = Pt(10.5)
        r_pre.font.bold = True
        r_pre.font.color.rgb = RGBColor(30, 41, 59)
    r = p.add_run(text)
    r.font.name = "Calibri"
    r.font.size = Pt(10.5)
    r.font.color.rgb = RGBColor(51, 65, 85)
    return p

def add_bullet(doc, text, bold_prefix=None):
    p = doc.add_paragraph(style='List Bullet')
    format_p(p, space_before=1, space_after=2, line_spacing=1.15)
    if bold_prefix:
        r_pre = p.add_run(bold_prefix)
        r_pre.font.name = "Calibri"
        r_pre.font.size = Pt(10.5)
        r_pre.font.bold = True
        r_pre.font.color.rgb = RGBColor(30, 41, 59)
    r = p.add_run(text)
    r.font.name = "Calibri"
    r.font.size = Pt(10.5)
    r.font.color.rgb = RGBColor(51, 65, 85)
    return p

def add_styled_table(doc, headers, rows, col_widths=None):
    tbl = doc.add_table(rows=len(rows) + 1, cols=len(headers))
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False
    
    # Header row
    for col_idx, h_text in enumerate(headers):
        cell = tbl.cell(0, col_idx)
        if col_widths and col_idx < len(col_widths):
            cell.width = Inches(col_widths[col_idx])
        set_cell_background(cell, "1E3A8A")
        set_cell_margins(cell, top=80, bottom=80, left=100, right=100)
        p = cell.paragraphs[0]
        format_p(p, space_before=0, space_after=0)
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(h_text)
        r.font.name = "Arial"
        r.font.size = Pt(9.5)
        r.font.bold = True
        r.font.color.rgb = RGBColor(255, 255, 255)
        
    # Data rows
    for row_idx, row_data in enumerate(rows):
        bg = "FFFFFF" if row_idx % 2 == 0 else "F8FAFC"
        for col_idx, val in enumerate(row_data):
            cell = tbl.cell(row_idx + 1, col_idx)
            if col_widths and col_idx < len(col_widths):
                cell.width = Inches(col_widths[col_idx])
            set_cell_background(cell, bg)
            set_cell_margins(cell, top=60, bottom=60, left=100, right=100)
            p = cell.paragraphs[0]
            format_p(p, space_before=0, space_after=0)
            if col_idx == 0:
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            else:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            r = p.add_run(str(val))
            r.font.name = "Calibri"
            r.font.size = Pt(9.5)
            if col_idx == 0:
                r.font.bold = True
                r.font.color.rgb = RGBColor(30, 41, 59)
            else:
                r.font.color.rgb = RGBColor(51, 65, 85)
                
    doc.add_paragraph()

def main():
    print("Building Synopsis Document...")
    doc = Document()
    add_header_footer(doc)

    # Title
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    format_p(p_title, space_before=4, space_after=2)
    r_title = p_title.add_run("OFFICIAL PROJECT SYNOPSIS")
    r_title.font.name = "Arial"
    r_title.font.size = Pt(18)
    r_title.font.bold = True
    r_title.font.color.rgb = RGBColor(229, 9, 20)

    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    format_p(p_sub, space_before=2, space_after=16)
    r_sub = p_sub.add_run("CineAI: AI-Powered Multi-Algorithmic Movie Recommendation System\nWith Dynamic Cold-Start Mitigation & Explainable AI")
    r_sub.font.name = "Arial"
    r_sub.font.size = Pt(12)
    r_sub.font.bold = True
    r_sub.font.color.rgb = RGBColor(30, 41, 59)

    # Meta Table
    meta_headers = ["Project Detail", "Specification / Candidate Record"]
    meta_rows = [
        ["Project Title", "CineAI: AI-Powered Multi-Algorithmic Movie Recommendation System"],
        ["Candidate Name(s)", "1. Nella Navven\n2. Kella Suryaprasanna\n3. Charanya Bhandari"],
        ["Roll Number(s)", "1. 12510519\n2. 12516522\n3. 12512578"],
        ["Degree & Branch", "Bachelor of Technology (B.Tech) in Computer Science & Engineering"],
        ["Project Supervisor", "Abhikesh, Department of Computer Science & Engineering"],
        ["Academic Session", "2025–2026"]
    ]
    add_styled_table(doc, meta_headers, meta_rows, col_widths=[2.0, 4.5])

    # 1. Introduction & Motivation
    add_heading_1(doc, "1. INTRODUCTION & MOTIVATION")
    add_body(doc, "With over 50,000 titles distributed across Over-The-Top (OTT) streaming providers (Netflix, Amazon Prime Video, Disney+, Apple TV+), consumers frequently suffer from choice paralysis, spending upwards of 18 minutes searching rather than viewing content. Recommender systems have become foundational infrastructure. However, traditional standalone systems suffer from critical flaws: Collaborative Filtering fails for new users (the Cold-Start Problem) and suffers under 98.3% matrix sparsity, while Content-Based systems create narrow filter bubbles lacking serendipity. CineAI was developed to overcome these limitations through a unified, production-grade hybrid architecture trained on the genuine MovieLens dataset.")

    # 2. Problem Statement
    add_heading_1(doc, "2. PROBLEM STATEMENT")
    add_body(doc, "To design, develop, evaluate, and deploy an end-to-end, multi-algorithmic movie recommendation platform that dynamically mitigates the new-user cold-start bottleneck, handles extreme rating matrix sparsity, attaches Explainable AI justification badges to every recommendation, persists ratings transactionally in SQLite, and provides an interactive streaming web application with an examiner playground.")

    # 3. Objectives
    add_heading_1(doc, "3. OBJECTIVES")
    add_bullet(doc, "Train Content-Based TF-IDF, Item-Item Collaborative Filtering, and TruncatedSVD models on MovieLens.", bold_prefix="• Multi-Algorithmic Core: ")
    add_bullet(doc, "Implement dynamic alpha arbitration (0.00 -> 0.35 -> 0.60) to eliminate cold-start failures.", bold_prefix="• Dynamic Cold-Start Mitigation: ")
    add_bullet(doc, "Generate transparent Explainable AI badges for all recommendations.", bold_prefix="• Explainable AI (XAI): ")
    add_bullet(doc, "Provide ACID-compliant SQLite3 relational persistence for users, ratings, and preferences.", bold_prefix="• State Persistence: ")
    add_bullet(doc, "Deploy a modern dark-themed Streamlit interface with visual Plotly dashboards and model playground.", bold_prefix="• Full-Stack UI: ")
    add_bullet(doc, "Empirically evaluate accuracy achieving RMSE <= 0.95 and pass 100% of automated tests.", bold_prefix="• Empirical Validation: ")

    # 4. Methodology & Machine Learning Formulations
    add_heading_1(doc, "4. METHODOLOGY & MACHINE LEARNING FORMULATIONS")
    add_body(doc, "1. Content-Based TF-IDF: Constructs composite metadata soups (clean title + genres + crowd tags) mapped to a 5,000-dimensional TF-IDF space with Cosine Similarity.", bold_prefix="• ")
    add_body(doc, "2. Dynamic User Profiling: Weights movie vectors by rating deviation around neutral 2.5 stars: u_profile = sum((r_uj - 2.5) * v_j) / sum(|r_uj - 2.5|).", bold_prefix="• ")
    add_body(doc, "3. Item-Item Collaborative Filtering: Compares item rating vectors across common co-raters, predicting ratings via weighted correlation over significant neighbors (s_ij > 0.05).", bold_prefix="• ")
    add_body(doc, "4. TruncatedSVD Matrix Factorization: Factors sparse matrix R approx U_k * Sigma_k * V_k^T (k = 20 latent factors) to capture latent thematic concepts.", bold_prefix="• ")
    add_body(doc, "5. Bayesian IMDB Weighted Rating: WR = (v/(v+m))*R + (m/(v+m))*C (m=10, C=3.50) to prevent small-sample rating bias.", bold_prefix="• ")
    add_body(doc, "6. Dynamic Hybrid Blending: Score = alpha(u)*CF + (1 - alpha(u))*CB + Genre_Boost, where alpha is 0.00 for cold-start (0 ratings), 0.35 for warm-up (1-3 ratings), and 0.60 for mature users.", bold_prefix="• ")

    # 5. Experimental Results
    add_heading_1(doc, "5. EXPERIMENTAL RESULTS & EVALUATION")
    res_headers = ["Metric", "Baseline Benchmark", "CineAI Measured Value", "Status"]
    res_rows = [
        ["Root Mean Squared Error (RMSE)", "1.0500", "0.9094", "Superior Predictive Accuracy"],
        ["Mean Absolute Error (MAE)", "0.8200", "0.7015", "Low Average Error (~0.7 stars)"],
        ["Precision@10", "0.0050", "0.0072", "Accurate Top-10 Retrieval"],
        ["Recall@10", "0.0035", "0.0056", "High Target Retrieval Under Sparsity"],
        ["Catalog Coverage", "0.0080", "0.0157", "Healthy Exploration of Long Tail"],
        ["Automated Test Suite", "100%", "14 / 14 Tests Passing", "Complete System Verification"]
    ]
    add_styled_table(doc, res_headers, res_rows, col_widths=[2.5, 1.3, 1.4, 1.8])

    # 6. Conclusion
    add_heading_1(doc, "6. CONCLUSION")
    add_body(doc, "CineAI successfully bridges academic recommendation theory and software engineering practice. It solves the cold-start problem, manages 98.30% matrix sparsity, delivers verified predictive fidelity (RMSE 0.9094), and provides transparent Explainable AI badges within a streaming-grade web interface.")

    # Signatures
    p_sig = doc.add_paragraph()
    format_p(p_sig, space_before=16, space_after=0)
    p_sig.add_run("Candidate Signatures:\n1. Nella Navven (Roll No: 12510519): ________________________\n2. Kella Suryaprasanna (Roll No: 12516522): ________________________\n3. Charanya Bhandari (Roll No: 12512578): ________________________\n\nProject Supervisor / Guide Signature:\nAbhikesh, Department of Computer Science & Engineering: ________________________").font.size = Pt(9.5)

    print(f"Saving Synopsis document to {DOCX_PATH}...")
    doc.save(DOCX_PATH)
    print("Synopsis document generated successfully!")

if __name__ == "__main__":
    main()
