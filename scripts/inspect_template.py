import glob
import os
import pymupdf

pdf_files = glob.glob(r"c:\Users\Administrator\Downloads\*Reforged*.pdf")
print("Found PDFs:", pdf_files)
pdf_path = pdf_files[0]
doc = pymupdf.open(pdf_path)
print("Page count:", len(doc))

for idx, page in enumerate(doc):
    print(f"\n--- PAGE {idx+1} --- (Rect: {page.rect})")
    for b in page.get_text("blocks"):
        # b: (x0, y0, x1, y1, text, block_no, block_type)
        txt = b[4].strip().replace("\n", " // ")
        print(f"  ({b[0]:.1f}, {b[1]:.1f}, {b[2]:.1f}, {b[3]:.1f}): {txt}")
