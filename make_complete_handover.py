"""
CineAI Complete Project Handover Builder
Generates all 7 PDFs, Markdown guides, Backup ZIP, Checklist, and Handover ZIP.
"""

import os
import sys
import json
import shutil
import zipfile
import subprocess
from datetime import datetime

BASE_DIR = r"C:\Users\LENOVO\.gemini\antigravity\scratch\AI-Movie-Recommendation-System"
HANDOVER_DIR = os.path.join(BASE_DIR, "CineAI_COMPLETE_PROJECT_HANDOVER")
CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

os.makedirs(HANDOVER_DIR, exist_ok=True)

TEAM_INFO = {
    "project_name": "AI-Powered Movie Recommendation System (CineAI)",
    "students": [
        {"name": "Nella Navven", "roll": "12510519"},
        {"name": "Kella Suryaprasanna", "roll": "12516522"},
        {"name": "Charanya Bhandari", "roll": "12512578"}
    ],
    "guide": "Abhikesh",
    "department": "Department of Computer Science & Engineering",
    "date": "November 2026"
}

def get_base_css():
    return """
    @page {
        size: A4;
        margin: 16mm 14mm 16mm 14mm;
    }
    *, *:before, *:after { box-sizing: border-box; }
    body {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        color: #1e293b;
        background: #ffffff;
        line-height: 1.5;
        font-size: 9.5pt;
        margin: 0;
        padding: 0;
    }
    .page-header {
        border-bottom: 2.5px solid #e11d48;
        padding-bottom: 8px;
        margin-bottom: 14px;
    }
    .badge {
        display: inline-block;
        padding: 2px 7px;
        background: #ffe4e6;
        color: #be123c;
        border-radius: 4px;
        font-weight: 700;
        font-size: 7.5pt;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 4px;
    }
    .badge-blue { background: #dbeafe; color: #1d4ed8; }
    .badge-green { background: #dcfce7; color: #15803d; }
    .badge-purple { background: #f3e8ff; color: #7e22ce; }
    h1 {
        color: #0f172a;
        margin: 0 0 3px 0;
        font-size: 17pt;
        font-weight: 800;
        letter-spacing: -0.4px;
    }
    .doc-subtitle {
        color: #64748b;
        font-size: 9pt;
        margin: 0;
    }
    .meta-box {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 5px;
        padding: 7px 11px;
        margin-bottom: 14px;
        font-size: 8.2pt;
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 5px;
    }
    .meta-item strong { color: #334155; }
    h2 {
        color: #0f172a;
        font-size: 11.5pt;
        font-weight: 700;
        border-bottom: 1px solid #e2e8f0;
        padding-bottom: 3px;
        margin-top: 16px;
        margin-bottom: 6px;
        page-break-after: avoid;
    }
    h3 {
        color: #1e293b;
        font-size: 10pt;
        font-weight: 600;
        margin-top: 10px;
        margin-bottom: 4px;
        page-break-after: avoid;
    }
    p { margin: 0 0 7px 0; text-align: justify; }
    ul, ol { margin: 0 0 8px 0; padding-left: 18px; }
    li { margin-bottom: 2px; }
    table {
        width: 100%;
        border-collapse: collapse;
        margin: 10px 0 14px 0;
        font-size: 8.5pt;
        page-break-inside: avoid;
    }
    th, td {
        border: 1px solid #cbd5e1;
        padding: 5px 8px;
        text-align: left;
    }
    th {
        background: #0f172a;
        color: #ffffff;
        font-weight: 600;
    }
    tr:nth-child(even) td { background: #f8fafc; }
    .code-block {
        background: #0f172a;
        color: #f8fafc;
        padding: 8px 11px;
        border-radius: 4px;
        font-family: Consolas, "Courier New", monospace;
        font-size: 8.2pt;
        line-height: 1.35;
        margin: 8px 0;
        white-space: pre-wrap;
        word-break: break-all;
        page-break-inside: avoid;
    }
    .inline-code {
        font-family: Consolas, "Courier New", monospace;
        background: #f1f5f9;
        color: #0f172a;
        padding: 1px 4px;
        border-radius: 3px;
        font-size: 8.5pt;
        border: 1px solid #e2e8f0;
    }
    .callout {
        border-left: 3.5px solid #e11d48;
        background: #fff1f2;
        padding: 8px 11px;
        margin: 10px 0;
        border-radius: 0 4px 4px 0;
        font-size: 8.8pt;
        page-break-inside: avoid;
    }
    .callout-info { border-left-color: #0284c7; background: #f0f9ff; }
    .callout-success { border-left-color: #16a34a; background: #f0fdf4; }
    .callout-title { font-weight: 700; color: #0f172a; margin-bottom: 2px; }
    .metrics-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 7px;
        margin: 10px 0;
        page-break-inside: avoid;
    }
    .metric-card {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-top: 2.5px solid #e11d48;
        padding: 7px;
        border-radius: 4px;
        text-align: center;
    }
    .metric-val {
        font-size: 13pt;
        font-weight: 800;
        color: #0f172a;
        margin: 2px 0;
    }
    .metric-lbl {
        font-size: 7pt;
        color: #64748b;
        font-weight: 600;
        text-transform: uppercase;
    }
    .qa-box {
        margin-bottom: 9px;
        padding: 6px 10px;
        background: #f8fafc;
        border-left: 3px solid #3b82f6;
        border-radius: 0 4px 4px 0;
        page-break-inside: avoid;
    }
    .qa-q {
        font-weight: 700;
        color: #1e3a8a;
        margin-bottom: 2px;
        font-size: 9pt;
    }
    .qa-a { color: #334155; font-size: 8.5pt; margin: 0; }
    .page-break { page-break-before: always; }
    .footer-note {
        margin-top: 18px;
        border-top: 1px solid #e2e8f0;
        padding-top: 5px;
        font-size: 7.2pt;
        color: #94a3b8;
        display: flex;
        justify-content: space-between;
    }
    .diagram-box {
        background: #f8fafc;
        border: 1px solid #cbd5e1;
        border-radius: 5px;
        padding: 10px;
        margin: 10px 0;
        text-align: center;
        page-break-inside: avoid;
    }
    """

def html_document(title, subtitle, badge_text, badge_class, content):
    meta_html = f"""
    <div class="meta-box">
        <div class="meta-item"><strong>Project:</strong> {TEAM_INFO['project_name']}</div>
        <div class="meta-item"><strong>Guide:</strong> {TEAM_INFO['guide']} ({TEAM_INFO['department']})</div>
        <div class="meta-item"><strong>Team Members:</strong> {', '.join([s['name'] + ' (' + s['roll'] + ')' for s in TEAM_INFO['students']])}</div>
        <div class="meta-item"><strong>Deliverable Type:</strong> Engineering Handover &amp; Backup Documentation</div>
    </div>
    """
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>{title}</title>
    <style>{get_base_css()}</style>
</head>
<body>
    <div class="page-header">
        <div>
            <span class="badge {badge_class}">{badge_text}</span>
            <h1>{title}</h1>
            <p class="doc-subtitle">{subtitle}</p>
        </div>
    </div>
    {meta_html}
    {content}
    <div class="footer-note">
        <span>CineAI System Handover Documentation | Academic Project Deliverable</span>
        <span>Students: Nella Navven, Kella Suryaprasanna, Charanya Bhandari | Guide: Abhikesh</span>
    </div>
</body>
</html>"""

def convert_html_to_pdf(html_content, pdf_path):
    temp_html = pdf_path.replace(".pdf", "_temp.html")
    with open(temp_html, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    cmd = [
        CHROME_PATH,
        "--headless=new",
        "--no-sandbox",
        "--disable-gpu",
        "--no-pdf-header-footer",
        f"--print-to-pdf={pdf_path}",
        temp_html
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if os.path.exists(temp_html):
        os.remove(temp_html)
    
    if res.returncode != 0 or not os.path.exists(pdf_path):
        raise RuntimeError(f"Failed to generate {pdf_path}: Exit code {res.returncode}\n{res.stderr}")
    return os.path.getsize(pdf_path)

print("HTML/PDF generator framework loaded.")
