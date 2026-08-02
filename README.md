# AI Document Understanding System — Financial Reports

Step 1 (Week 1-5): OCR baseline. This is a "walking skeleton" —
not pretty yet, but runs end-to-end. Later steps (extraction, API,
validation...) will be built on top of this foundation.

## Setup (Ubuntu/Debian)

```bash
# Tesseract OCR + Vietnamese language pack + poppler (PDF reading)
sudo apt-get install tesseract-ocr tesseract-ocr-vie poppler-utils

# Python dependencies
pip install -r requirements.txt
```

On Windows/Mac: install Tesseract from the official tesseract-ocr
page, and make sure to include the Vietnamese language pack during
installation.

## Try it out

```bash
python src/ocr_baseline.py data/samples/sample_report.png
```

The raw text output will be saved to `data/output/<filename>_raw.txt`.

Tested with `data/samples/sample_report.png` (a sample image
simulating a balance sheet) — OCR correctly recognized almost all
of the financial line items, with only a few minor errors (e.g.
"Đơn" → "Don" due to small font size). This is normal quality for
a baseline — things to improve later: increase dpi when converting
PDFs, add image preprocessing (deskew, contrast enhancement), or
switch to PaddleOCR/a VLM if Tesseract isn't accurate enough.

## Folder structure

```
doc-ai-project/
├── data/
│   ├── samples/     # test PDF/image files — put real financial reports here
│   └── output/      # OCR/extraction results are saved here
├── src/
│   └── ocr_baseline.py   # step 1: document -> raw text
└── requirements.txt
```

## Next step (Week 4-6)

Write `src/extract_baseline.py`: read the `*_raw.txt` file, use
regex/keyword matching to capture common financial line items
(Total Assets, Net Revenue, Net Profit After Tax...) and output
structured JSON. This will serve as the baseline to compare against
the VLM-based approach in the following step.
