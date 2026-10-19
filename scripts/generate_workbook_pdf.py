"""Trustwire Complete Project Mastery & Defence Workbook PDF Generator
Compiles all 17 markdown modules in docs/project_mastery/ into a publication-grade,
beautifully styled HTML document with MathJax, Mermaid diagrams, typography,
and converts it via Microsoft Edge headless into docs/Trustwire_Project_Mastery_Workbook.pdf.
"""

import os
import re
import sys
import time
import subprocess
from pathlib import Path
from markdown_it import MarkdownIt

WORKSPACE = Path(__file__).resolve().parent.parent
DOCS_DIR = WORKSPACE / "docs" / "project_mastery"
OUTPUT_HTML = WORKSPACE / "docs" / "Trustwire_Workbook.html"
OUTPUT_PDF = WORKSPACE / "docs" / "Trustwire_Project_Mastery_Workbook.pdf"
EDGE_EXE = Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe")
if not EDGE_EXE.exists():
    EDGE_EXE = Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe")

MODULE_TITLES = {
    "00": "Project Overview & Architectural Mission",
    "01": "Code-Grounded Implementation Audit",
    "02": "Complete System Architecture & Concurrency",
    "03": "Audio Deepfake Detection Deep Dive (Wav2Vec2)",
    "04": "Video Deepfake Detection Deep Dive (ViT)",
    "05": "Mathematical Foundations & Derivations",
    "06": "Exhaustive File-by-File Codebase Walkthrough",
    "07": "Financial Scam Risk & Context-Aware Engine",
    "08": "Live Capture, Privacy & Retention Lifecycle",
    "09": "Dependencies, Setup & Troubleshooting",
    "10": "Testing Suite & Evaluation Benchmarks",
    "11": "Performance Profiling & Big-O Complexity",
    "12": "Evaluator Live Demonstration Guide",
    "13": "Presentation Script & Slide-by-Slide Defence",
    "14": "Viva Voce Question Bank (86 Technical Questions)",
    "15": "Technical Glossary & 4-Phase Learning Syllabus",
    "16": "Limitations, Adversarial Evasion & Future Work",
}

CSS_STYLES = """
@page {
  size: A4 portrait;
  margin: 18mm 16mm 20mm 16mm;
  @bottom-right {
    content: "Page " counter(page);
    font-size: 8pt;
    color: #64748b;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  }
  @bottom-left {
    content: "Trustwire: Technical Mastery & Project Defence Workbook";
    font-size: 8pt;
    color: #64748b;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  }
}

* {
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  color: #1e293b;
  background: #ffffff;
  line-height: 1.55;
  font-size: 9.8pt;
  margin: 0;
  padding: 0;
}

/* ================== COVER PAGE ================== */
.cover-page {
  page-break-before: avoid;
  page-break-after: always;
  break-after: page;
  height: 96vh;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 40px 20px;
  border: 2px solid #0f172a;
  background: linear-gradient(180deg, #f8fafc 0%, #ffffff 100%);
  border-radius: 8px;
}

.cover-header {
  border-bottom: 3px solid #0284c7;
  padding-bottom: 20px;
}

.cover-badge {
  display: inline-block;
  background: #0284c7;
  color: #ffffff;
  font-size: 9pt;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 1.5px;
  padding: 4px 12px;
  border-radius: 4px;
  margin-bottom: 12px;
}

.cover-title {
  font-size: 34pt;
  font-weight: 900;
  color: #0f172a;
  letter-spacing: -0.5px;
  margin: 0 0 10px 0;
  line-height: 1.1;
}

.cover-subtitle {
  font-size: 14pt;
  color: #334155;
  font-weight: 600;
  margin: 0 0 8px 0;
}

.cover-description {
  font-size: 10pt;
  color: #64748b;
  max-width: 650px;
  margin: 0;
}

.cover-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin: 30px 0;
}

.stat-card {
  background: #f1f5f9;
  border-left: 4px solid #0284c7;
  padding: 12px 16px;
  border-radius: 0 6px 6px 0;
}

.stat-number {
  font-size: 18pt;
  font-weight: 800;
  color: #0f172a;
  line-height: 1.1;
}

.stat-label {
  font-size: 8.5pt;
  color: #475569;
  text-transform: uppercase;
  font-weight: 600;
  letter-spacing: 0.5px;
}

.cover-meta {
  border-top: 1px solid #cbd5e1;
  padding-top: 16px;
  font-size: 8.5pt;
  color: #64748b;
  display: flex;
  justify-content: space-between;
}

/* ================== TABLE OF CONTENTS ================== */
.toc-page {
  page-break-before: always;
  page-break-after: always;
  break-before: page;
  break-after: page;
  padding: 20px 0;
}

.toc-title {
  font-size: 20pt;
  font-weight: 800;
  color: #0f172a;
  border-bottom: 2px solid #0284c7;
  padding-bottom: 8px;
  margin-bottom: 20px;
}

.toc-grid {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.toc-item {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  text-decoration: none;
  color: #1e293b;
  padding: 6px 10px;
  background: #f8fafc;
  border-radius: 4px;
  border: 1px solid #e2e8f0;
}

.toc-item:hover {
  background: #f1f5f9;
}

.toc-module-num {
  font-weight: 700;
  color: #0284c7;
  width: 90px;
}

.toc-module-name {
  font-weight: 600;
  flex: 1;
}

/* ================== MODULE SECTIONS ================== */
.workbook-module {
  page-break-before: always;
  break-before: page;
  margin-top: 10px;
}

.module-header-box {
  background: #0f172a;
  color: #ffffff;
  padding: 14px 18px;
  border-radius: 6px;
  margin-bottom: 20px;
  border-left: 6px solid #0284c7;
}

.module-tag {
  font-size: 8pt;
  font-weight: 700;
  text-transform: uppercase;
  color: #38bdf8;
  letter-spacing: 1px;
}

.module-title {
  font-size: 16pt;
  font-weight: 800;
  color: #ffffff;
  margin: 4px 0 0 0;
}

h1 {
  font-size: 16pt;
  font-weight: 800;
  color: #0f172a;
  border-bottom: 2px solid #e2e8f0;
  padding-bottom: 6px;
  margin-top: 24px;
  margin-bottom: 12px;
  page-break-after: avoid;
}

h2 {
  font-size: 13pt;
  font-weight: 700;
  color: #1e293b;
  margin-top: 18px;
  margin-bottom: 8px;
  border-left: 3px solid #0284c7;
  padding-left: 8px;
  page-break-after: avoid;
}

h3 {
  font-size: 11pt;
  font-weight: 600;
  color: #334155;
  margin-top: 14px;
  margin-bottom: 6px;
  page-break-after: avoid;
}

p {
  margin: 0 0 10px 0;
}

/* ================== TABLES ================== */
table {
  width: 100%;
  border-collapse: collapse;
  margin: 14px 0;
  font-size: 8.8pt;
  page-break-inside: avoid;
}

th {
  background: #1e293b;
  color: #ffffff;
  text-align: left;
  padding: 8px 10px;
  font-weight: 600;
  border: 1px solid #334155;
}

td {
  padding: 6px 10px;
  border: 1px solid #cbd5e1;
  vertical-align: top;
}

tr:nth-child(even) {
  background: #f8fafc;
}

/* ================== CODE BLOCKS ================== */
pre {
  background: #0f172a;
  color: #e2e8f0;
  padding: 10px 14px;
  border-radius: 6px;
  font-family: "JetBrains Mono", Consolas, "Courier New", monospace;
  font-size: 8.2pt;
  line-height: 1.45;
  overflow-x: auto;
  border: 1px solid #334155;
  page-break-inside: avoid;
  margin: 12px 0;
}

code {
  font-family: "JetBrains Mono", Consolas, "Courier New", monospace;
  font-size: 8.5pt;
  background: #f1f5f9;
  color: #0f172a;
  padding: 1px 4px;
  border-radius: 3px;
  border: 1px solid #e2e8f0;
}

pre code {
  background: transparent;
  color: inherit;
  padding: 0;
  border: none;
}

/* ================== BLOCKQUOTES & CALLOUTS ================== */
blockquote {
  border-left: 4px solid #0284c7;
  background: #f0f9ff;
  color: #0369a1;
  padding: 8px 14px;
  margin: 12px 0;
  border-radius: 0 4px 4px 0;
  font-size: 9.2pt;
}

blockquote p {
  margin: 0;
}

/* ================== VIVA QUESTIONS CARDS ================== */
.viva-question {
  border: 1px solid #e2e8f0;
  background: #ffffff;
  border-radius: 6px;
  padding: 12px;
  margin: 12px 0;
  page-break-inside: avoid;
}

.viva-q-title {
  font-weight: 700;
  color: #0f172a;
  font-size: 10pt;
  margin-bottom: 6px;
}

.viva-answer-short {
  background: #f8fafc;
  border-left: 3px solid #10b981;
  padding: 6px 10px;
  font-size: 9pt;
  margin-bottom: 6px;
  border-radius: 0 4px 4px 0;
}

.viva-answer-deep {
  font-size: 8.8pt;
  color: #334155;
  margin-bottom: 6px;
}

.viva-trap {
  background: #fff1f2;
  border-left: 3px solid #e11d48;
  color: #9f1239;
  padding: 6px 10px;
  font-size: 8.6pt;
  border-radius: 0 4px 4px 0;
}

/* ================== MERMAID & MATH ================== */
.mermaid {
  display: flex;
  justify-content: center;
  background: #f8fafc;
  padding: 14px;
  border-radius: 6px;
  border: 1px solid #e2e8f0;
  margin: 12px 0;
  page-break-inside: avoid;
}

.math-display {
  display: block;
  text-align: center;
  margin: 12px 0;
}
"""

def process_markdown(content: str) -> str:
    """Pre-processes markdown to wrap mermaid blocks, math expressions, and viva questions."""
    # Convert ```mermaid ... ``` to <div class="mermaid">...</div>
    def replace_mermaid(match):
        graph = match.group(1).strip()
        return f'<div class="mermaid">\n{graph}\n</div>'

    content = re.sub(r'```mermaid\s*\n(.*?)\n```', replace_mermaid, content, flags=re.DOTALL)
    
    # Pre-render callout syntax like > [!NOTE]
    content = re.sub(r'>\s*\[!(NOTE|TIP|IMPORTANT|WARNING|CAUTION)\]\s*(.*?)(?=\n\n|\n[^\>]|$)', 
                     r'<blockquote><strong>\1:</strong> \2</blockquote>', content, flags=re.DOTALL)

    return content

def compile_workbook_html() -> Path:
    print("[1/3] Reading and compiling markdown modules into unified HTML...")
    md_parser = MarkdownIt("gfm-like").disable("linkify").enable("table")

    modules_html = []
    
    # Get all 17 markdown files in order
    files = sorted([f for f in DOCS_DIR.glob("*.md") if f.name[:2].isdigit()])
    
    # Table of Contents Items
    toc_items = []
    for f in files:
        prefix = f.name[:2]
        title = MODULE_TITLES.get(prefix, f.stem)
        toc_items.append(f'''
        <a class="toc-item" href="#module-{prefix}">
          <span class="toc-module-num">Module {prefix}</span>
          <span class="toc-module-name">{title}</span>
        </a>
        ''')

    for f in files:
        prefix = f.name[:2]
        title = MODULE_TITLES.get(prefix, f.stem)
        raw_text = f.read_text(encoding="utf-8")
        
        # Strip redundant first h1 if it matches module title
        lines = raw_text.splitlines()
        if lines and lines[0].startswith("# "):
            raw_text = "\n".join(lines[1:])
            
        processed_md = process_markdown(raw_text)
        rendered_body = md_parser.render(processed_md)
        
        module_block = f"""
        <section class="workbook-module" id="module-{prefix}">
          <div class="module-header-box">
            <div class="module-tag">Trustwire Technical Mastery — Module {prefix}</div>
            <div class="module-title">{title}</div>
          </div>
          <div class="module-content">
            {rendered_body}
          </div>
        </section>
        """
        modules_html.append(module_block)

    full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Trustwire: Technical Mastery & Project Defence Workbook</title>
  
  <!-- MathJax for KaTeX/LaTeX vector math rendering -->
  <script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js" id="MathJax-script"></script>
  
  <!-- Mermaid for architectural vector flowcharts -->
  <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
  <script>
    mermaid.initialize({{
      startOnLoad: true,
      theme: 'default',
      flowchart: {{ useMaxWidth: true, htmlLabels: true, curve: 'basis' }}
    }});
  </script>
  
  <style>
    {CSS_STYLES}
  </style>
</head>
<body>

  <!-- COVER PAGE -->
  <div class="cover-page">
    <div class="cover-header">
      <div class="cover-badge">Official Technical Defence & Engineering Dossier</div>
      <div class="cover-title">TRUSTWIRE</div>
      <div class="cover-subtitle">Real-Time Client-Side Synthetic Media Detection Workstation</div>
      <p class="cover-description">
        Comprehensive Engineering Audit, Signal Processing Derivations, Vision Transformer Pipeline,
        Wav2Vec2 Neural Vocoder Analysis, Concurrency Model, and 86-Question Technical Viva Bank.
      </p>
    </div>

    <div class="cover-stats">
      <div class="stat-card">
        <div class="stat-number">17 Modules</div>
        <div class="stat-label">Complete Coverage</div>
      </div>
      <div class="stat-card">
        <div class="stat-number">22 / 22 Tests</div>
        <div class="stat-label">Automated Pass Rate</div>
      </div>
      <div class="stat-card">
        <div class="stat-number">86 Questions</div>
        <div class="stat-label">Technical Viva Bank</div>
      </div>
    </div>

    <div class="cover-meta">
      <div>
        <strong>System Target:</strong> Windows 10/11 x86_64<br>
        <strong>Backend Stack:</strong> Python 3.11, FastAPI, ONNX Runtime, PyTorch<br>
        <strong>Frontend Stack:</strong> Electron 30, React 18, Tailwind CSS
      </div>
      <div style="text-align: right;">
        <strong>Version:</strong> 1.0.0 (Release Edition)<br>
        <strong>Date:</strong> October 2026<br>
        <strong>Privacy Posture:</strong> 100% On-Device / 900s Rolling Ceiling
      </div>
    </div>
  </div>

  <!-- TABLE OF CONTENTS -->
  <div class="toc-page">
    <div class="toc-title">Workbook Contents & Module Navigation</div>
    <div class="toc-grid">
      {''.join(toc_items)}
    </div>
  </div>

  <!-- ALL 17 MODULES -->
  {''.join(modules_html)}

</body>
</html>
"""
    OUTPUT_HTML.write_text(full_html, encoding="utf-8")
    print(f"HTML workbook generated: {OUTPUT_HTML} ({OUTPUT_HTML.stat().st_size:,} bytes)")
    return OUTPUT_HTML

def convert_html_to_pdf(html_path: Path):
    print("[2/3] Rendering PDF with Microsoft Edge headless (rendering vector math and flowcharts)...")
    if not EDGE_EXE.exists():
        raise FileNotFoundError(f"Microsoft Edge executable not found at: {EDGE_EXE}")

    cmd = [
        str(EDGE_EXE),
        "--headless=new",
        "--disable-gpu",
        "--no-pdf-header-footer",
        "--run-all-compositor-stages-before-draw",
        "--virtual-time-budget=12000",
        f"--print-to-pdf={OUTPUT_PDF.resolve()}",
        str(html_path.resolve())
    ]
    
    t0 = time.time()
    res = subprocess.run(cmd, capture_output=True, text=True)
    duration = time.time() - t0
    
    if res.returncode != 0:
        print("Edge error:", res.stderr)
        raise RuntimeError(f"Edge PDF generation failed with code {res.returncode}")

    if not OUTPUT_PDF.exists() or OUTPUT_PDF.stat().st_size == 0:
        raise RuntimeError("PDF was not created or has 0 bytes.")

    print(f"[3/3] Workbook PDF successfully generated in {duration:.1f}s!")
    print(f"Output File: {OUTPUT_PDF}")
    print(f"File Size: {OUTPUT_PDF.stat().st_size:,} bytes ({OUTPUT_PDF.stat().st_size / (1024*1024):.2f} MB)")

    # Optional inspection with PyMuPDF
    try:
        import fitz
        doc = fitz.open(str(OUTPUT_PDF))
        print(f"Total Page Count: {len(doc)} pages")
        doc.close()
    except Exception as e:
        print(f"PyMuPDF check bypassed: {e}")

if __name__ == "__main__":
    html_file = compile_workbook_html()
    convert_html_to_pdf(html_file)
