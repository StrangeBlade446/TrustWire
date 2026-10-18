"""Trustwire Reforged '26 Presentation Generator
Builds a high-impact, professional PowerPoint pitch deck using the exact Reforged '26 template,
customized for team 'the omniscient' and project 'Trust Wire'.
Includes slide transitions and entrance animations.
"""

import os
import glob
from pathlib import Path
import pymupdf
import pptx
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml import parse_xml

# Color Palette
COLOR_REFORGED_RED = RGBColor(200, 35, 44)       # #C8232C (Template Red)
COLOR_TRUSTWIRE_TEAL = RGBColor(13, 148, 136)     # #0D9488 (Trustwire Teal)
COLOR_DARK_TEXT = RGBColor(30, 41, 59)            # #1E293B (Slate 800)
COLOR_BODY_TEXT = RGBColor(51, 65, 85)            # #334155 (Slate 700)
COLOR_MUTED_TEXT = RGBColor(100, 116, 139)        # #64748B (Slate 500)
COLOR_CARD_BG = RGBColor(248, 250, 252)           # #F8FAFC (Card fill)
COLOR_CARD_BORDER = RGBColor(226, 232, 240)       # #E2E8F0 (Border)
COLOR_WHITE = RGBColor(255, 255, 255)
COLOR_ACCENT_BG = RGBColor(254, 242, 242)         # #FEF2F2 (Soft Red tint)
COLOR_TEAL_TINT = RGBColor(240, 253, 250)         # #F0FDFA (Soft Teal tint)

def extract_template_backgrounds(pdf_path: str, output_dir: str):
    """Extract high-resolution rendered backgrounds from the PDF template with redactions."""
    os.makedirs(output_dir, exist_ok=True)
    doc = pymupdf.open(pdf_path)
    
    # 7 slides (Page 6 - Mentorship is omitted)
    pages_to_extract = [
        (0, "slide1_title.png", [pymupdf.Rect(150, 220, 1300, 750)]), # Redact placeholder texts
        (1, "slide2_idea.png", []),
        (2, "slide3_architecture.png", []),
        (3, "slide4_workflows.png", []),
        (4, "slide5_usp.png", []),
        (6, "slide6_references.png", [pymupdf.Rect(110, 220, 750, 360)]), # Redact placeholder prompt
        (7, "slide7_thankyou.png", [])
    ]
    
    bg_paths = []
    for page_idx, filename, redactions in pages_to_extract:
        p = doc[page_idx]
        for r in redactions:
            p.add_redact_annot(r, fill=(1, 1, 1))
        if redactions:
            p.apply_redactions()
        pix = p.get_pixmap(dpi=150)
        out_path = os.path.join(output_dir, filename)
        pix.save(out_path)
        bg_paths.append(out_path)
        print(f"Rendered {filename} ({pix.width}x{pix.height})")
        
    return bg_paths

def add_transition(slide, transition_type: str = "fade", duration_ms: int = 500, direction: str = "l"):
    """Inject standard OpenXML slide transition."""
    if transition_type == "fade":
        t_xml = '<p:transition xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" spd="med" advClick="1"><p:fade/></p:transition>'
    elif transition_type == "push":
        t_xml = f'<p:transition xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" spd="med" advClick="1"><p:push dir="{direction}"/></p:transition>'
    elif transition_type == "wipe":
        t_xml = f'<p:transition xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" spd="med" advClick="1"><p:wipe dir="{direction}"/></p:transition>'
    elif transition_type == "split":
        t_xml = '<p:transition xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" spd="med" advClick="1"><p:split dir="out"/></p:transition>'
    else:
        t_xml = '<p:transition xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" spd="med" advClick="1"><p:fade/></p:transition>'
    
    slide._element.append(parse_xml(t_xml))

def add_slide_animations(slide, shape_ids):
    """Inject standard OpenXML build entrance animations for shapes on the slide."""
    if not shape_ids:
        return
        
    par_elements = []
    c_tn_counter = 3
    
    for shape_id in shape_ids:
        par_xml = f'''
        <p:par xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
          <p:cTn id="{c_tn_counter}" fill="hold">
            <p:stCondLst><p:cond delay="0"/></p:stCondLst>
            <p:childTnLst>
              <p:par>
                <p:cTn id="{c_tn_counter+1}" fill="hold">
                  <p:stCondLst><p:cond delay="0"/></p:stCondLst>
                  <p:childTnLst>
                    <p:set>
                      <p:cBhvr>
                        <p:cTn id="{c_tn_counter+2}" dur="1" fill="hold"/>
                        <p:tgtEl><p:spTgt spid="{shape_id}"/></p:tgtEl>
                        <p:attrNameLst><p:attrName>style.visibility</p:attrName></p:attrNameLst>
                      </p:cBhvr>
                      <p:to><p:strVal val="visible"/></p:to>
                    </p:set>
                    <p:animEffect transition="in" filter="fade">
                      <p:cBhvr>
                        <p:cTn id="{c_tn_counter+3}" dur="400"/>
                        <p:tgtEl><p:spTgt spid="{shape_id}"/></p:tgtEl>
                      </p:cBhvr>
                    </p:animEffect>
                  </p:childTnLst>
                </p:cTn>
              </p:par>
            </p:childTnLst>
          </p:cTn>
        </p:par>
        '''
        par_elements.append(par_xml)
        c_tn_counter += 4
        
    timing_xml = f'''
    <p:timing xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
      <p:tnLst>
        <p:par>
          <p:cTn id="1" dur="indefinite" restart="always" nodeType="tmRoot">
            <p:childTnLst>
              <p:seq concurrent="1" nextAc="seek">
                <p:cTn id="2" dur="indefinite" nodeType="mainSeq">
                  <p:childTnLst>
                    {''.join(par_elements)}
                  </p:childTnLst>
                </p:cTn>
              </p:seq>
            </p:childTnLst>
          </p:cTn>
        </p:par>
      </p:tnLst>
    </p:timing>
    '''
    slide._element.append(parse_xml(timing_xml))

def build_presentation(bg_images, output_pptx_paths):
    prs = pptx.Presentation()
    prs.slide_width = Inches(13.333333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6] # Blank slide
    
    # ==========================================
    # SLIDE 1: TITLE SLIDE
    # ==========================================
    s1 = prs.slides.add_slide(blank_layout)
    s1.shapes.add_picture(bg_images[0], 0, 0, prs.slide_width, prs.slide_height)
    
    # Project Title Box
    title_box = s1.shapes.add_textbox(Inches(1.5), Inches(2.2), Inches(10.33), Inches(1.3))
    tf1 = title_box.text_frame
    tf1.word_wrap = True
    p1 = tf1.paragraphs[0]
    p1.text = "TRUST WIRE"
    p1.font.size = Pt(56)
    p1.font.bold = True
    p1.font.color.rgb = COLOR_REFORGED_RED
    p1.font.name = "Segoe UI"
    p1.alignment = PP_ALIGN.CENTER
    
    # Subtitle Box
    sub_box = s1.shapes.add_textbox(Inches(1.5), Inches(3.55), Inches(10.33), Inches(0.6))
    tf_sub = sub_box.text_frame
    tf_sub.word_wrap = True
    p_sub = tf_sub.paragraphs[0]
    p_sub.text = "Autonomous Local AI Deception Defense & Forensic Deepfake Shield"
    p_sub.font.size = Pt(20)
    p_sub.font.bold = True
    p_sub.font.color.rgb = COLOR_DARK_TEXT
    p_sub.font.name = "Segoe UI"
    p_sub.alignment = PP_ALIGN.CENTER
    
    # Team Info Container Card
    team_card = s1.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE, Inches(2.2), Inches(4.35), Inches(8.93), Inches(2.4)
    )
    team_card.fill.solid()
    team_card.fill.fore_color.rgb = COLOR_CARD_BG
    team_card.line.color.rgb = COLOR_CARD_BORDER
    team_card.line.width = Pt(1.5)
    
    tf_team = team_card.text_frame
    tf_team.word_wrap = True
    
    p_t1 = tf_team.paragraphs[0]
    p_t1.text = "TEAM: THE OMNISCIENT"
    p_t1.font.size = Pt(18)
    p_t1.font.bold = True
    p_t1.font.color.rgb = COLOR_TRUSTWIRE_TEAL
    p_t1.font.name = "Segoe UI"
    p_t1.alignment = PP_ALIGN.CENTER
    
    p_t2 = tf_team.add_paragraph()
    p_t2.text = "Rudra Veer Singh   •   Daksh Pratap Singh   •   Shivaksh Arya   •   Suhel Khan"
    p_t2.font.size = Pt(16)
    p_t2.font.bold = True
    p_t2.font.color.rgb = COLOR_DARK_TEXT
    p_t2.font.name = "Segoe UI"
    p_t2.alignment = PP_ALIGN.CENTER
    
    p_t3 = tf_team.add_paragraph()
    p_t3.text = "TRACK: AI/ML, CYBERSECURITY & DIGITAL TRUST"
    p_t3.font.size = Pt(13)
    p_t3.font.bold = True
    p_t3.font.color.rgb = COLOR_REFORGED_RED
    p_t3.font.name = "Segoe UI"
    p_t3.alignment = PP_ALIGN.CENTER
    
    add_transition(s1, "fade")
    add_slide_animations(s1, [title_box.shape_id, sub_box.shape_id, team_card.shape_id])
    
    # ==========================================
    # SLIDE 2: IDEA (The Problem & The Solution)
    # ==========================================
    s2 = prs.slides.add_slide(blank_layout)
    s2.shapes.add_picture(bg_images[1], 0, 0, prs.slide_width, prs.slide_height)
    
    # Subtitle Lead
    lead_box = s2.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(11.33), Inches(0.5))
    tf_lead = lead_box.text_frame
    p_lead = tf_lead.paragraphs[0]
    p_lead.text = "On-Premises Real-Time Deception Defense Against Generative Deepfakes & Synthetic Voice Cloning"
    p_lead.font.size = Pt(15)
    p_lead.font.bold = True
    p_lead.font.color.rgb = COLOR_MUTED_TEXT
    p_lead.font.name = "Segoe UI"
    
    # Left Box: The Threat Landscape (Problem)
    box_prob = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.0), Inches(2.4), Inches(5.4), Inches(4.4))
    box_prob.fill.solid()
    box_prob.fill.fore_color.rgb = COLOR_ACCENT_BG
    box_prob.line.color.rgb = COLOR_REFORGED_RED
    box_prob.line.width = Pt(1.5)
    
    tf_p = box_prob.text_frame
    tf_p.word_wrap = True
    p = tf_p.paragraphs[0]
    p.text = "THE DECEPTION THREAT"
    p.font.size = Pt(17)
    p.font.bold = True
    p.font.color.rgb = COLOR_REFORGED_RED
    p.font.name = "Segoe UI"
    
    prob_points = [
        ("Hyper-Realistic AI Media", "Diffusion models (Veo, Sora, Gemini, DeepFaceLab) generate photorealistic visual manipulations indistinguishable to the human eye."),
        ("Voice Cloning Vulnerability", "Neural vocoders (ElevenLabs, Bark) synthesize convincing voice timbre, cadence, and emotion from brief reference audio."),
        ("Cloud Privacy Violations", "Commercial detectors require uploading sensitive executive calls and proprietary recordings to 3rd-party servers, breaching enterprise confidentiality.")
    ]
    for title, desc in prob_points:
        p_pt = tf_p.add_paragraph()
        p_pt.text = f"•  {title}: "
        p_pt.font.bold = True
        p_pt.font.size = Pt(12)
        p_pt.font.color.rgb = COLOR_DARK_TEXT
        p_pt.font.name = "Segoe UI"
        
        p_desc = tf_p.add_paragraph()
        p_desc.text = f"    {desc}"
        p_desc.font.size = Pt(11)
        p_desc.font.color.rgb = COLOR_BODY_TEXT
        p_desc.font.name = "Segoe UI"
        
    # Right Box: The Trust Wire Solution
    box_sol = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(2.4), Inches(5.5), Inches(4.4))
    box_sol.fill.solid()
    box_sol.fill.fore_color.rgb = COLOR_TEAL_TINT
    box_sol.line.color.rgb = COLOR_TRUSTWIRE_TEAL
    box_sol.line.width = Pt(1.5)
    
    tf_s = box_sol.text_frame
    tf_s.word_wrap = True
    p = tf_s.paragraphs[0]
    p.text = "THE TRUSTWIRE INNOVATION"
    p.font.size = Pt(17)
    p.font.bold = True
    p.font.color.rgb = COLOR_TRUSTWIRE_TEAL
    p.font.name = "Segoe UI"
    
    sol_points = [
        ("100% On-Device Local Processing", "Zero external network calls or cloud dependencies. All neural networks execute locally with strict 15-minute ephemeral memory purging."),
        ("Dual-Modal Deep Learning Shield", "Vision Transformer (ViT) face forensic scoring paired with INT8 Quantized Wav2Vec2 audio acoustic spoofing detection."),
        ("Generative Watermark Provenance", "Multi-scale Canny edge correlation for SynthID/Gemini watermarks and container encoder verification (100% precision on Gemini AI)."),
        ("Strict Architectural Decoupling", "Independent offline media analysis and real-time live system loopback monitoring prevent unwanted cross-interference.")
    ]
    for title, desc in sol_points:
        p_pt = tf_s.add_paragraph()
        p_pt.text = f"✔  {title}: "
        p_pt.font.bold = True
        p_pt.font.size = Pt(12)
        p_pt.font.color.rgb = COLOR_DARK_TEXT
        p_pt.font.name = "Segoe UI"
        
        p_desc = tf_s.add_paragraph()
        p_desc.text = f"    {desc}"
        p_desc.font.size = Pt(11)
        p_desc.font.color.rgb = COLOR_BODY_TEXT
        p_desc.font.name = "Segoe UI"
        
    add_transition(s2, "push", direction="l")
    add_slide_animations(s2, [box_prob.shape_id, box_sol.shape_id])
    
    # ==========================================
    # SLIDE 3: TECHNICAL ARCHITECTURE
    # ==========================================
    s3 = prs.slides.add_slide(blank_layout)
    s3.shapes.add_picture(bg_images[2], 0, 0, prs.slide_width, prs.slide_height)
    
    # Lead subtitle positioned cleanly to the right of "TECHNICAL ARCHITECTURE" title
    lead_s3 = s3.shapes.add_textbox(Inches(5.4), Inches(1.2), Inches(6.9), Inches(1.0))
    tf_l3 = lead_s3.text_frame
    tf_l3.word_wrap = True
    p_l3 = tf_l3.paragraphs[0]
    p_l3.text = "Four-Tier Modular Pipeline: Low-Latency Ingestion, Dual Neural Cores, and Native Desktop Alerts"
    p_l3.font.size = Pt(14)
    p_l3.font.bold = True
    p_l3.font.color.rgb = COLOR_MUTED_TEXT
    p_l3.font.name = "Segoe UI"
    
    # 4 Architecture Columns
    col_width = Inches(2.65)
    gap = Inches(0.24)
    left_start = Inches(1.0)
    top_pos = Inches(2.55)
    card_height = Inches(4.35)
    
    arch_tiers = [
        ("TIER 1: CAPTURE & INGEST", COLOR_REFORGED_RED, [
            ("Screen Capture", "mss worker with 1-element queue to prevent lag; samples active monitors at 1fps."),
            ("Audio Loopback", "soundcard WASAPI Loopback recording system speaker audio in float32 chunks."),
            ("File Ingestion", "PyAV multi-stream demuxing supporting MP4, MOV, WAV, FLAC, MKV.")
        ]),
        ("TIER 2: PREPROCESSING", COLOR_TRUSTWIRE_TEAL, [
            ("Face Crop Engine", "Multi-cascade Haar with adaptive 70px minSize to eliminate false clutter faces."),
            ("Acoustic Prep", "16 kHz mono resampling, sliding 3.0s window, zero-mean unit-variance norm."),
            ("Watermark ROI", "Bottom-right 28% frame isolation and Canny edge map extraction.")
        ]),
        ("TIER 3: NEURAL CORES", COLOR_DARK_TEXT, [
            ("Vision Transformer", "ViT Deepfake Classifier (224x224 RGB, SIMD/AVX2 CPU execution, ~205ms)."),
            ("Acoustic Spoofing", "INT8 Quantized Wav2Vec2 Large XLSR (355 MB, ~140ms latency on CPU)."),
            ("Watermark Match", "Multi-scale Canny correlation against Google Gemini SynthID template.")
        ]),
        ("TIER 4: DISPATCH & HUD", COLOR_TRUSTWIRE_TEAL, [
            ("Central Alert Hub", "Thread-safe broker with cooldown deduplication and metadata persistence."),
            ("Strict Decoupling", "Live monitoring broadcasts over WebSocket; offline uploads update report."),
            ("Native Shell & HUD", "Electron desktop shell + floating Windows toolbar overlay + React 18 UI.")
        ]),
    ]
    
    tier_shape_ids = []
    for idx, (tier_title, header_col, items) in enumerate(arch_tiers):
        card_left = left_start + idx * (col_width + gap)
        card = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, card_left, top_pos, col_width, card_height)
        card.fill.solid()
        card.fill.fore_color.rgb = COLOR_CARD_BG
        card.line.color.rgb = header_col
        card.line.width = Pt(1.5)
        tier_shape_ids.append(card.shape_id)
        
        tf = card.text_frame
        tf.word_wrap = True
        p_h = tf.paragraphs[0]
        p_h.text = tier_title
        p_h.font.size = Pt(12)
        p_h.font.bold = True
        p_h.font.color.rgb = header_col
        p_h.font.name = "Segoe UI"
        
        for item_t, item_d in items:
            p_it = tf.add_paragraph()
            p_it.text = f"▸ {item_t}"
            p_it.font.size = Pt(11)
            p_it.font.bold = True
            p_it.font.color.rgb = COLOR_DARK_TEXT
            p_it.font.name = "Segoe UI"
            
            p_id = tf.add_paragraph()
            p_id.text = item_d
            p_id.font.size = Pt(9.5)
            p_id.font.color.rgb = COLOR_BODY_TEXT
            p_id.font.name = "Segoe UI"
            
    add_transition(s3, "wipe", direction="r")
    add_slide_animations(s3, tier_shape_ids)
    
    # ==========================================
    # SLIDE 4: WORKFLOWS
    # ==========================================
    s4 = prs.slides.add_slide(blank_layout)
    s4.shapes.add_picture(bg_images[3], 0, 0, prs.slide_width, prs.slide_height)
    
    lead_s4 = s4.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(11.33), Inches(0.4))
    tf_l4 = lead_s4.text_frame
    p_l4 = tf_l4.paragraphs[0]
    p_l4.text = "Two Independent Operating Modes: Complete Decoupling Between Offline Media and Live System Monitoring"
    p_l4.font.size = Pt(14)
    p_l4.font.bold = True
    p_l4.font.color.rgb = COLOR_MUTED_TEXT
    p_l4.font.name = "Segoe UI"
    
    # Column 1: Offline Forensic Media Analysis
    wf_left = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.0), Inches(2.35), Inches(5.4), Inches(4.4))
    wf_left.fill.solid()
    wf_left.fill.fore_color.rgb = COLOR_CARD_BG
    wf_left.line.color.rgb = COLOR_REFORGED_RED
    wf_left.line.width = Pt(1.5)
    
    tf_wl = wf_left.text_frame
    tf_wl.word_wrap = True
    p = tf_wl.paragraphs[0]
    p.text = "WORKFLOW A: OFFLINE MEDIA ANALYSIS"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = COLOR_REFORGED_RED
    p.font.name = "Segoe UI"
    
    offline_steps = [
        ("Step 1: Ingestion & Integrity", "User drops recorded video or audio clip (up to 500MB). PyAV verifies container streams and checks AI encoder metadata."),
        ("Step 2: Stream Decomposition", "Video frames sampled at configurable intervals (0.5s–1.0s); audio demuxed into 16kHz mono chunks."),
        ("Step 3: Deep Multi-Modal Scanning", "Vision Transformer evaluates face crops; watermark matcher checks Canny star correlation; Wav2Vec2 classifies acoustic spoofing."),
        ("Step 4: Forensic Assessment Report", "Generates overall verdict ('Suspicious Video', 'Suspicious Audio', or 'Authentic'), peak fake scores, timestamps, and evidence summary.")
    ]
    for s_title, s_desc in offline_steps:
        p_t = tf_wl.add_paragraph()
        p_t.text = f"▸  {s_title}"
        p_t.font.bold = True
        p_t.font.size = Pt(11)
        p_t.font.color.rgb = COLOR_DARK_TEXT
        p_t.font.name = "Segoe UI"
        
        p_d = tf_wl.add_paragraph()
        p_d.text = f"    {s_desc}"
        p_d.font.size = Pt(10)
        p_d.font.color.rgb = COLOR_BODY_TEXT
        p_d.font.name = "Segoe UI"
        
    # Column 2: Live Screen & Audio Monitoring
    wf_right = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(2.35), Inches(5.5), Inches(4.4))
    wf_right.fill.solid()
    wf_right.fill.fore_color.rgb = COLOR_CARD_BG
    wf_right.line.color.rgb = COLOR_TRUSTWIRE_TEAL
    wf_right.line.width = Pt(1.5)
    
    tf_wr = wf_right.text_frame
    tf_wr.word_wrap = True
    p = tf_wr.paragraphs[0]
    p.text = "WORKFLOW B: REAL-TIME LIVE MONITORING"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = COLOR_TRUSTWIRE_TEAL
    p.font.name = "Segoe UI"
    
    live_steps = [
        ("Step 1: Source Initialization", "Select display monitor and audio loopback output. Monitoring can be toggled from app UI or floating Windows HUD toolbar."),
        ("Step 2: Low-Latency Inference", "Background worker captures active screen frames and speaker loopback audio; drops stale frames immediately to ensure sub-second response."),
        ("Step 3: Autonomous Threat Triggering", "Triggers immediate alerts on suspicious facial generation (>=0.52), generative watermarks (>=0.85), or synthetic voice cues (>=0.65)."),
        ("Step 4: Real-Time HUD & Disparity Modal", "Pushes real-time WebSocket alert. Disparity modal pops up over video calls with suggested actions (e.g., secondary verification).")
    ]
    for s_title, s_desc in live_steps:
        p_t = tf_wr.add_paragraph()
        p_t.text = f"▸  {s_title}"
        p_t.font.bold = True
        p_t.font.size = Pt(11)
        p_t.font.color.rgb = COLOR_DARK_TEXT
        p_t.font.name = "Segoe UI"
        
        p_d = tf_wr.add_paragraph()
        p_d.text = f"    {s_desc}"
        p_d.font.size = Pt(10)
        p_d.font.color.rgb = COLOR_BODY_TEXT
        p_d.font.name = "Segoe UI"
        
    add_transition(s4, "push", direction="l")
    add_slide_animations(s4, [wf_left.shape_id, wf_right.shape_id])
    
    # ==========================================
    # SLIDE 5: USP (Unique Selling Propositions)
    # ==========================================
    s5 = prs.slides.add_slide(blank_layout)
    s5.shapes.add_picture(bg_images[4], 0, 0, prs.slide_width, prs.slide_height)
    
    lead_s5 = s5.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(11.33), Inches(0.4))
    tf_l5 = lead_s5.text_frame
    p_l5 = tf_l5.paragraphs[0]
    p_l5.text = "Four Pillars of Competitive Advantage: Privacy, Precision, Edge Speed, and Verified Calibration"
    p_l5.font.size = Pt(14)
    p_l5.font.bold = True
    p_l5.font.color.rgb = COLOR_MUTED_TEXT
    p_l5.font.name = "Segoe UI"
    
    usp_items = [
        ("100% Local & Zero Cloud Exposure", COLOR_REFORGED_RED, 
         "All neural inferences run strictly on-device using local CPU/GPU runtime. Zero media frames or audio streams ever leave the user's computer. Enforces a strict 15-minute ephemeral auto-purge policy for maximum privacy compliance."),
        ("Multi-Modal Triangulation & Watermarks", COLOR_TRUSTWIRE_TEAL,
         "Combines Vision Transformer (ViT) spatial artifact scoring, Google Gemini / SynthID 4-pointed star edge correlation, and Wav2Vec2 acoustic spoofing detection. Eliminates blind spots from visual skin smoothing."),
        ("Strict Operational Decoupling", COLOR_DARK_TEXT,
         "First-of-its-kind dual architecture where offline media uploads never trigger distracting live monitoring popups or start capture workers. Live monitoring and media analysis remain strictly isolated."),
        ("Calibrated Benchmark Performance", COLOR_TRUSTWIRE_TEAL,
         "INT8-quantized audio model (355 MB) cuts memory by 4x. Tested with 100% precision on Gemini AI videos (0.96-0.996 confidence) and 100% authentic classification across 50+ real smartphone recordings.")
    ]
    
    usp_width = Inches(5.4)
    usp_height = Inches(1.9)
    usp_shape_ids = []
    
    coords = [
        (Inches(1.0), Inches(2.35)),
        (Inches(6.8), Inches(2.35)),
        (Inches(1.0), Inches(4.45)),
        (Inches(6.8), Inches(4.45))
    ]
    
    for idx, ((title, col, body), (cx, cy)) in enumerate(zip(usp_items, coords)):
        card = s5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, cx, cy, usp_width, usp_height)
        card.fill.solid()
        card.fill.fore_color.rgb = COLOR_CARD_BG
        card.line.color.rgb = col
        card.line.width = Pt(1.5)
        usp_shape_ids.append(card.shape_id)
        
        tf = card.text_frame
        tf.word_wrap = True
        p_t = tf.paragraphs[0]
        p_t.text = f"{idx+1}.  {title}"
        p_t.font.size = Pt(13)
        p_t.font.bold = True
        p_t.font.color.rgb = col
        p_t.font.name = "Segoe UI"
        
        p_b = tf.add_paragraph()
        p_b.text = body
        p_b.font.size = Pt(10.5)
        p_b.font.color.rgb = COLOR_BODY_TEXT
        p_b.font.name = "Segoe UI"
        
    # Metrics Banner
    banner = s5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.0), Inches(6.5), Inches(11.3), Inches(0.45))
    banner.fill.solid()
    banner.fill.fore_color.rgb = COLOR_ACCENT_BG
    banner.line.color.rgb = COLOR_REFORGED_RED
    banner.line.width = Pt(1.0)
    tf_b = banner.text_frame
    p_b = tf_b.paragraphs[0]
    p_b.text = "BENCHMARK: 100% Fake Detection (Gemini AI Videos)  |  100% Real Retention (Smartphone Camera Dataset)  |  22 Automated Pytest Tests Passing"
    p_b.font.size = Pt(11)
    p_b.font.bold = True
    p_b.font.color.rgb = COLOR_REFORGED_RED
    p_b.font.name = "Segoe UI"
    p_b.alignment = PP_ALIGN.CENTER
    usp_shape_ids.append(banner.shape_id)
    
    add_transition(s5, "split")
    add_slide_animations(s5, usp_shape_ids)
    
    # ==========================================
    # SLIDE 6: REFERENCES AND SOURCES
    # ==========================================
    s6 = prs.slides.add_slide(blank_layout)
    s6.shapes.add_picture(bg_images[5], 0, 0, prs.slide_width, prs.slide_height)
    
    lead_s6 = s6.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(11.33), Inches(0.4))
    tf_l6 = lead_s6.text_frame
    p_l6 = tf_l6.paragraphs[0]
    p_l6.text = "Academic Foundations, Open-Source Technologies, and Public Forensic Datasets"
    p_l6.font.size = Pt(14)
    p_l6.font.bold = True
    p_l6.font.color.rgb = COLOR_MUTED_TEXT
    p_l6.font.name = "Segoe UI"
    
    # Left Box: AI Research Papers & Models
    ref_left = s6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.0), Inches(2.35), Inches(5.4), Inches(4.4))
    ref_left.fill.solid()
    ref_left.fill.fore_color.rgb = COLOR_CARD_BG
    ref_left.line.color.rgb = COLOR_REFORGED_RED
    ref_left.line.width = Pt(1.5)
    
    tf_rl = ref_left.text_frame
    tf_rl.word_wrap = True
    p = tf_rl.paragraphs[0]
    p.text = "SCIENTIFIC CITATIONS & MODELS"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = COLOR_REFORGED_RED
    p.font.name = "Segoe UI"
    
    papers = [
        ("Vision Transformer (ViT)", "Dosovitskiy et al., ICLR 2021. 'An Image is Worth 16x16 Words: Transformers for Image Recognition at Scale.' Used for spatial facial anomaly classification."),
        ("Wav2Vec 2.0 Audio Framework", "Baevski et al., NeurIPS 2020. 'wav2vec 2.0: A Framework for Self-Supervised Learning of Speech Representations.' Base for acoustic spoofing classifier."),
        ("ASVspoof Challenge Benchmark", "Yamagishi et al., Computer Speech & Language 2021. Dataset and evaluation metrics for voice spoofing and synthetic vocoder detection."),
        ("FaceForensics++ Benchmark", "Rössler et al., ICCV 2019. 'FaceForensics++: Learning to Detect Manipulated Facial Images.' CVF Open Access benchmark for facial manipulation."),
        ("Google SynthID Provenance", "Google DeepMind SynthID Imperceptible Generative Watermarking & Metadata Provenance Specifications.")
    ]
    for p_title, p_desc in papers:
        p_t = tf_rl.add_paragraph()
        p_t.text = f"•  {p_title}"
        p_t.font.bold = True
        p_t.font.size = Pt(11)
        p_t.font.color.rgb = COLOR_DARK_TEXT
        p_t.font.name = "Segoe UI"
        
        p_d = tf_rl.add_paragraph()
        p_d.text = f"   {p_desc}"
        p_d.font.size = Pt(9.5)
        p_d.font.color.rgb = COLOR_BODY_TEXT
        p_d.font.name = "Segoe UI"
        
    # Right Box: Open-Source Libraries & Platform
    ref_right = s6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(2.35), Inches(5.5), Inches(4.4))
    ref_right.fill.solid()
    ref_right.fill.fore_color.rgb = COLOR_CARD_BG
    ref_right.line.color.rgb = COLOR_TRUSTWIRE_TEAL
    ref_right.line.width = Pt(1.5)
    
    tf_rr = ref_right.text_frame
    tf_rr.word_wrap = True
    p = tf_rr.paragraphs[0]
    p.text = "CORE OPEN-SOURCE ECOSYSTEM"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = COLOR_TRUSTWIRE_TEAL
    p.font.name = "Segoe UI"
    
    tools = [
        ("Inference Engines", "ONNX Runtime 1.31 (CPU AVX2/SIMD acceleration, INT8 quantization), PyTorch 2.14, TorchAudio, Hugging Face Transformers."),
        ("Media & Video Processing", "PyAV 18.1 (FFmpeg 9.0 native C bindings for demuxing), OpenCV (cv2) for Haar cascades and Canny edge correlation, Pillow (PIL)."),
        ("System Capture Loopback", "SoundCard (Windows WASAPI loopback audio capture), mss 10.2 (low-latency multi-monitor screen grab)."),
        ("Backend Web Core", "FastAPI 0.115, Uvicorn 0.34, Pydantic v2, WebSockets for asynchronous live event streaming."),
        ("Desktop Shell & Frontend", "Electron 32 (Chromium/Node desktop wrapper), React 18, Vite 5, Tailwind CSS, Lucide Icons.")
    ]
    for t_title, t_desc in tools:
        p_t = tf_rr.add_paragraph()
        p_t.text = f"✔  {t_title}"
        p_t.font.bold = True
        p_t.font.size = Pt(11)
        p_t.font.color.rgb = COLOR_DARK_TEXT
        p_t.font.name = "Segoe UI"
        
        p_d = tf_rr.add_paragraph()
        p_d.text = f"   {t_desc}"
        p_d.font.size = Pt(9.5)
        p_d.font.color.rgb = COLOR_BODY_TEXT
        p_d.font.name = "Segoe UI"
        
    add_transition(s6, "wipe", direction="r")
    add_slide_animations(s6, [ref_left.shape_id, ref_right.shape_id])
    
    # ==========================================
    # SLIDE 7: THANK YOU
    # ==========================================
    s7 = prs.slides.add_slide(blank_layout)
    s7.shapes.add_picture(bg_images[6], 0, 0, prs.slide_width, prs.slide_height)
    
    # Place Info Card neatly below "THANK YOU" without covering it
    ty_card = s7.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(2.0), Inches(5.4), Inches(9.33), Inches(1.5))
    ty_card.fill.solid()
    ty_card.fill.fore_color.rgb = COLOR_CARD_BG
    ty_card.line.color.rgb = COLOR_REFORGED_RED
    ty_card.line.width = Pt(1.5)
    
    tf_ty = ty_card.text_frame
    tf_ty.word_wrap = True
    
    p = tf_ty.paragraphs[0]
    p.text = "TRUST WIRE  |  DETECT DECEPTION BEFORE IT COSTS YOU"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = COLOR_REFORGED_RED
    p.font.name = "Segoe UI"
    p.alignment = PP_ALIGN.CENTER
    
    p_t = tf_ty.add_paragraph()
    p_t.text = "Team: the omniscient   •   Rudra Veer Singh  •  Daksh Pratap Singh  •  Shivaksh Arya  •  Suhel Khan"
    p_t.font.size = Pt(13)
    p_t.font.bold = True
    p_t.font.color.rgb = COLOR_TRUSTWIRE_TEAL
    p_t.font.name = "Segoe UI"
    p_t.alignment = PP_ALIGN.CENTER
    
    p_q = tf_ty.add_paragraph()
    p_q.text = "Reforged '26  •  Open for Live Demonstration & Questions"
    p_q.font.size = Pt(12)
    p_q.font.bold = True
    p_q.font.color.rgb = COLOR_MUTED_TEXT
    p_q.font.name = "Segoe UI"
    p_q.alignment = PP_ALIGN.CENTER
    
    add_transition(s7, "fade")
    add_slide_animations(s7, [ty_card.shape_id])
    
    # Save to all destination paths
    for out_path in output_pptx_paths:
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        prs.save(out_path)
        print(f"Presentation saved successfully to: {out_path}")

if __name__ == "__main__":
    pdf_input = r"c:\Users\Administrator\Downloads\Copy of Reforged '26.pdf"
    rendered_bg_dir = r"c:\Users\Administrator\Desktop\VS Code\trustwire\assets\presentation_backgrounds"
    
    print("Step 1: Extracting clean backgrounds from Reforged '26 PDF template...")
    bgs = extract_template_backgrounds(pdf_input, rendered_bg_dir)
    
    print("Step 2: Building 7-slide pitch deck with typography, transitions & animations...")
    destinations = [
        r"c:\Users\Administrator\Desktop\VS Code\trustwire\TrustWire_Presentation_The_Omniscient.pptx",
        r"c:\Users\Administrator\Desktop\TrustWire_Presentation_The_Omniscient.pptx",
        r"c:\Users\Administrator\Desktop\VS Code\Reforged\output\TrustWire_Deepfake_Detection_Reforged26.pptx"
    ]
    build_presentation(bgs, destinations)
    print("All tasks completed successfully!")
