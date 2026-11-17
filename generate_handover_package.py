"""
CineAI Complete Handover & Backup Generator
Generates all 7 PDFs, Markdown files, Backup ZIP, Checklist, and Master ZIP.
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
        margin: 18mm 16mm 18mm 16mm;
        @bottom-right {
            content: counter(page);
        }
    }
    *, *:before, *:after { box-sizing: border-box; }
    body {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        color: #1e293b;
        background: #ffffff;
        line-height: 1.55;
        font-size: 10pt;
        margin: 0;
        padding: 0;
    }
    .page-header {
        border-bottom: 2.5px solid #e11d48;
        padding-bottom: 10px;
        margin-bottom: 16px;
    }
    .badge {
        display: inline-block;
        padding: 3px 8px;
        background: #ffe4e6;
        color: #be123c;
        border-radius: 4px;
        font-weight: 700;
        font-size: 8pt;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 5px;
    }
    .badge-blue { background: #dbeafe; color: #1d4ed8; }
    .badge-green { background: #dcfce7; color: #15803d; }
    .badge-purple { background: #f3e8ff; color: #7e22ce; }
    h1 {
        color: #0f172a;
        margin: 0 0 4px 0;
        font-size: 18pt;
        font-weight: 800;
        letter-spacing: -0.4px;
    }
    .doc-subtitle {
        color: #64748b;
        font-size: 9.5pt;
        margin: 0;
    }
    .meta-box {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 6px;
        padding: 8px 12px;
        margin-bottom: 18px;
        font-size: 8.5pt;
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 6px;
    }
    .meta-item strong { color: #334155; }
    h2 {
        color: #0f172a;
        font-size: 12.5pt;
        font-weight: 700;
        border-bottom: 1.5px solid #e2e8f0;
        padding-bottom: 4px;
        margin-top: 20px;
        margin-bottom: 8px;
        page-break-after: avoid;
    }
    h3 {
        color: #1e293b;
        font-size: 10.5pt;
        font-weight: 600;
        margin-top: 12px;
        margin-bottom: 5px;
        page-break-after: avoid;
    }
    p { margin: 0 0 9px 0; text-align: justify; }
    ul, ol { margin: 0 0 10px 0; padding-left: 20px; }
    li { margin-bottom: 3px; }
    table {
        width: 100%;
        border-collapse: collapse;
        margin: 12px 0 16px 0;
        font-size: 9pt;
        page-break-inside: avoid;
    }
    th, td {
        border: 1px solid #cbd5e1;
        padding: 6px 9px;
        text-align: left;
    }
    th {
        background: #0f172a;
        color: #ffffff;
        font-weight: 600;
        font-size: 8.8pt;
    }
    tr:nth-child(even) td { background: #f8fafc; }
    .code-block {
        background: #0f172a;
        color: #f8fafc;
        padding: 9px 12px;
        border-radius: 5px;
        font-family: Consolas, "Courier New", monospace;
        font-size: 8.5pt;
        line-height: 1.4;
        margin: 10px 0;
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
        font-size: 8.8pt;
        border: 1px solid #e2e8f0;
    }
    .callout {
        border-left: 4px solid #e11d48;
        background: #fff1f2;
        padding: 9px 13px;
        margin: 12px 0;
        border-radius: 0 5px 5px 0;
        font-size: 9.2pt;
        page-break-inside: avoid;
    }
    .callout-info { border-left-color: #0284c7; background: #f0f9ff; }
    .callout-success { border-left-color: #16a34a; background: #f0fdf4; }
    .callout-title { font-weight: 700; color: #0f172a; margin-bottom: 3px; }
    .metrics-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 8px;
        margin: 12px 0;
        page-break-inside: avoid;
    }
    .metric-card {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-top: 3px solid #e11d48;
        padding: 8px;
        border-radius: 4px;
        text-align: center;
    }
    .metric-val {
        font-size: 14pt;
        font-weight: 800;
        color: #0f172a;
        margin: 2px 0;
    }
    .metric-lbl {
        font-size: 7.5pt;
        color: #64748b;
        font-weight: 600;
        text-transform: uppercase;
    }
    .qa-box {
        margin-bottom: 10px;
        padding: 7px 11px;
        background: #f8fafc;
        border-left: 3px solid #3b82f6;
        border-radius: 0 4px 4px 0;
        page-break-inside: avoid;
    }
    .qa-q {
        font-weight: 700;
        color: #1e3a8a;
        margin-bottom: 3px;
        font-size: 9.3pt;
    }
    .qa-a { color: #334155; font-size: 8.8pt; margin: 0; }
    .page-break { page-break-before: always; }
    .footer-note {
        margin-top: 20px;
        border-top: 1px solid #e2e8f0;
        padding-top: 6px;
        font-size: 7.5pt;
        color: #94a3b8;
        display: flex;
        justify-content: space-between;
    }
    .diagram-box {
        background: #f8fafc;
        border: 1px solid #cbd5e1;
        border-radius: 6px;
        padding: 12px;
        margin: 12px 0;
        text-align: center;
        page-break-inside: avoid;
    }
    """

def html_document(title, subtitle, badge_text, badge_class, content):
    meta_html = f"""
    <div class="meta-box">
        <div class="meta-item"><strong>Project:</strong> {TEAM_INFO['project_name']}</div>
        <div class="meta-item"><strong>Guide:</strong> {TEAM_INFO['guide']} ({TEAM_INFO['department']})</div>
        <div class="meta-item"><strong>Team:</strong> {', '.join([s['name'] + ' (' + s['roll'] + ')' for s in TEAM_INFO['students']])}</div>
        <div class="meta-item"><strong>Status:</strong> Engineering Handover &amp; Backup Specification</div>
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

print("Setup completed successfully.")
