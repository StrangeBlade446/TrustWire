# Trustwire — Video Deepfake Detection System Deep Dive

> **Primary Source File:** `backend/detectors/video/detector.py`  
> **Model Architecture:** Vision Transformer (ViT-Base/16)  
> **Pretrained Weights:** `prithivMLmods/deepfake-detector-model-v1`  
> **Inference Engine:** ONNX Runtime (CPU SIMD/AVX2 Optimized)  
> **Input Contract:** 224x224 RGB Normalized Face Tensor `(1, 3, 224, 224)`  

---

## 1. High-Level Video Forensic Pipeline

Trustwire does not analyze random video frames blindly. Because generative face swapping (DeepFaceLab, SimSwap, Roop) and facial reenactment (LivePortrait, Thin-Plate Spline) concentrate manipulation artifacts around the human head and facial boundary seams, Trustwire employs a **multi-stage localized forensic pipeline**:

```
Raw Video Stream / Captured Screen Frame (1080p BGR)
                          |
                          v
        [Stage 1: PyAV Frame Demuxing (1.0 fps)]
                          |
                          v
         [Stage 2: Dual Cascaded Haar Face Detection]
        (haarcascade_frontalface_alt2 / alt, min 64x64)
                          |
          +---------------+---------------+
          | (Face Found)                  | (No Face Found)
          v                               v
[Stage 3: YCrCb Skin Filter]     [Return Inconclusive / Zero Faces]
(Cr: 133-173, Cb: 77-127)                 |
          |                               |
          +---------------+               |
          | Valid Skin    | Non-Human     |
          v               v               |
 [Stage 4: 224x224 Crop] [Discard Box]    |
 (Normalize [-1.0, 1.0])                  |
          |                               |
          v                               |
 [Stage 5: ONNX ViT Classifier]           |
 (16x16 Patches, Self-Attention)          |
          |                               |
          v                               |
 [Stage 6: Multi-Scale SynthID Audit]     |
 (Canny 30/90, Scales 0.40 - 1.15)        |
          |                               |
          v                               |
 [Stage 7: Hardware Metadata Audit]       |
 (Check Camera Tags vs Lavf/FFmpeg)       |
          |                               |
          +---------------+---------------+
                          |
                          v
    [Stage 8: Multi-Frame Temporal Aggregation]
    (Suspicious Frame Ratio > 30% -> High Risk Alert)
```

---

## 2. Face Detection & Chrominance Verification

### A. Dual Cascaded Haar Detectors
Face localization must execute in under 15 milliseconds per frame to avoid choking live capture. Trustwire utilizes OpenCV's optimized Haar Feature-based Cascades:
- **Primary Detector:** `haarcascade_frontalface_alt2.xml` (high precision on frontal and slightly angled faces).
- **Secondary Detector:** `haarcascade_frontalface_alt.xml` (evaluated if primary detector returns zero faces).
- **Minimum Size Constraint:** Faces smaller than $64 \times 64$ pixels are ignored to prevent processing sub-resolution noise artifacts.

### B. YCrCb Skin-Tone Chrominance Filter
A critical vulnerability of Haar detectors is false positives on background patterns (wallpapers, wood grain, furniture shadows). Passing non-human image crops to the Vision Transformer produces erratic confidence scores. Trustwire implements an algorithmic chrominance boundary check:
1. The cropped face region is transformed from BGR to the YCrCb color space:
   $$Y = 0.299R + 0.587G + 0.114B$$
   $$Cr = (R - Y) \times 0.713 + 128$$
   $$Cb = (B - Y) \times 0.564 + 128$$
2. Human skin across all global ethnicities clusters tightly in the chrominance subspace:
   $$\text{Skin Mask} = (Cr \in [133, 173]) \land (Cb \in [77, 127])$$
3. **Rejection Threshold:** If skin pixels constitute less than 15% of the candidate bounding box, the crop is discarded as a non-face false positive.

---

## 3. Vision Transformer (ViT) Architecture & Inference

Once a valid human face crop is secured, it is resized to $224 \times 224 \times 3$, transformed to RGB, and normalized to $[-1.0, 1.0]$:
$$\mathbf{X}_{\text{norm}} = \frac{\mathbf{X}}{127.5} - 1.0$$
The tensor is reshaped to `(1, 3, 224, 224)` and passed into the ONNX Runtime session.

```mermaid
flowchart LR
    A[Face Crop 224x224x3] --> B[Patch Partitioning<br/>196 Patches of 16x16x3]
    B --> C[Linear Patch Projection<br/>768-Dim Vector per Patch]
    C --> D[Add [CLS] Token &<br/>1D Positional Embeddings]
    D --> E[12 Transformer Blocks<br/>Multi-Head Self-Attention]
    E --> F[Extract [CLS] Output]
    F --> G[MLP Classification Head]
    G --> H[Softmax: Real vs Fake]
```

### Why Vision Transformers Outperform CNNs in Deepfake Detection
Convolutional Neural Networks (CNNs) rely on local receptive fields ($3 \times 3$ or $5 \times 5$ convolutions), making them prone to overfitting on camera-specific noise or dataset-specific color grading. 

In contrast, the **Vision Transformer**:
1. Divides the face into $N = (224 / 16) \times (224 / 16) = 196$ independent patches.
2. Evaluates global pairwise self-attention across *all* patches simultaneously:
   $$\text{Attention}(\mathbf{Q}, \mathbf{K}, \mathbf{V}) = \text{softmax}\left(\frac{\mathbf{Q}\mathbf{K}^T}{\sqrt{d_k}}\right)\mathbf{V}$$
3. This allows the model to spot subtle spatial inconsistencies between distant facial regions—such as a mismatched eye reflection (corneal specular disparity), unnatural boundary blending along the jawline, or boundary blurring where the synthetic face was pasted over the donor head.

---

## 4. Multi-Scale SynthID Watermark Detection

In 2024–2026, major generative video systems (Google Veo, Gemini Imagen) began embedding digital watermark markers—specifically the **Google SynthID 4-pointed sparkle**—into generated frames.

Trustwire includes a dedicated digital watermark forensic engine in `detector.py`:
- **Template Reference:** `assets/gemini_star_template.png` (high-contrast alpha-masked sparkle icon).
- **Edge Extraction:** Both the incoming video frame and the template are converted to grayscale and filtered via Canny edge detection:
  $$\text{Canny Thresholds}: \quad T_{\text{low}} = 30, \quad T_{\text{high}} = 90$$
- **Multi-Scale Correlation:** Because watermarks scale with display resolution, Trustwire evaluates template scales $S \in [0.40, 1.15]$ in increments of $0.08$:
  $$R(x, y) = \frac{\sum_{x',y'} (T'(x',y') \cdot I'(x+x', y+y'))}{\sqrt{\sum_{x',y'} T'(x',y')^2 \cdot \sum_{x',y'} I'(x+x', y+y')^2}}$$
- **Detection Trigger:** A normalized cross-correlation peak $R_{\text{max}} \ge 0.55$ confirms the presence of a generative watermark, immediately elevating the frame's synthetic probability to $0.95$.

---

## 5. Hardware Container & Metadata Forensics

Before executing neural inference on a video file, Trustwire inspects the container header via PyAV:
1. **Physical Camera Hardware Tags:** Authentic mobile and professional cameras embed proprietary EXIF and container tags (`make: Apple`, `model: iPhone 15 Pro`, `lens: 24mm f/1.78`).
2. **Synthetic Encoder Flags:** Algorithmic deepfakes and screen recordings are almost universally encoded using open-source software libraries:
   - Tags containing `Lavf` (Libavformat), `Lavc` (Libavcodec), `ffmpeg`, `HandBrake`, or `x264/x265 core` are flagged.
3. **Forensic Correlation:** While software re-encoding does not prove a video is fake, the total absence of camera hardware tags combined with an elevated ViT score ($>0.50$) provides definitive forensic evidence for the final report.

---

## 6. Multi-Frame Temporal Aggregation

For uploaded video files, Trustwire samples frames at 1.0-second intervals throughout the entire duration:
$$N_{\text{frames}} = \lfloor \text{Duration}_{\text{sec}} \rfloor$$
For each frame $i$, the detector records:
$$\text{Evidence}_i = \{\text{timestamp}_i, \text{fake\_score}_i, \text{bbox}_i, \text{face\_detected}_i\}$$

### Final Decision Rule:
$$\text{Suspicious Ratio} = \frac{|\{i : \text{face\_detected}_i \land \text{fake\_score}_i \ge 0.52\}|}{|\{i : \text{face\_detected}_i\}|}$$

- **Condition 1 (Manipulated):** If $\text{Suspicious Ratio} \ge 0.30$, video is classified as **"Potentially manipulated"**. Confidence score is calculated as the mean of the top 20% most suspicious frames.
- **Condition 2 (Authentic):** If $\text{Suspicious Ratio} < 0.30$ and faces were detected, video is classified as **"Likely authentic"**.
- **Condition 3 (Inconclusive / No Faces):** If zero faces were found across all sampled frames, the classification returns **"Inconclusive"** ($P = 0.0$), preventing false alarms on landscape or non-human video content.
