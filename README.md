# AI Document Understanding System — Financial Reports

End-to-end pipeline for extracting structured financial data (Total Assets,
Net Revenue, Net Profit After Tax) from Vietnamese financial report PDFs.
Final project for the "MasterClass AI Document Understanding" course.

## Architecture

```
Client (PDF upload)
        │
        ▼
   FastAPI Gateway  (POST /extract)
        │
        ▼
Document Classifier & Router
   ├── OCR Pipeline   (Tesseract + regex — cheap, fast, tried first)
   └── VLM Pipeline   (Vision-Language Model — fallback when OCR misses fields)
        │
        ▼
   save_result()  →  data/output/<file>_routed.json
        │
        ▼
   Validation  (sanity checks, warnings)
        │
        ▼
   JSON response
```

## Project structure

```
doc-ai-project/
├── data/
│   ├── samples/            # input PDFs/images (gitignored except demo sample)
│   └── output/              # pipeline outputs (gitignored)
├── src/
│   ├── ocr_baseline.py      # Step 1: document -> raw text (Tesseract OCR)
│   ├── extract_baseline.py  # Step 2 (OCR branch): raw text -> structured JSON (regex)
│   ├── extract_vlm.py       # Step 2 (VLM branch): document -> structured JSON (VLM)
│   ├── fields_config.py     # single source of truth for target fields (FIELD_MAP)
│   ├── router.py            # Document Classifier & Router: OCR first, VLM fallback
│   └── api.py                # FastAPI Gateway: POST /extract endpoint + validation
├── .env                     # local secrets/config, never committed (see Setup)
├── .gitignore
├── requirements.txt
└── README.md
```

## Setup

### 1. Install system dependencies (Windows)

- **Tesseract OCR** (with the Vietnamese language pack) —
  https://github.com/UB-Mannheim/tesseract/wiki
- **Poppler for Windows** —
  https://github.com/oschwartz10612/poppler-windows/releases/

### 2. Install Python dependencies

```bash
python -m pip install -r requirements.txt
```

### 3. Configure `.env`

Create a `.env` file in the project root (this file is gitignored — never commit it):

```
TESSERACT_PATH=C:\Program Files\Tesseract-OCR\tesseract.exe
POPPLER_PATH=C:\poppler\poppler-XX.XX.X\Library\bin
OPENROUTER_API_KEY=your_openrouter_key
OPENROUTER_MODEL=google/gemma-4-31b-it:free
```

- Get an OpenRouter key at openrouter.ai/keys.
- Link your own Google AI Studio key at openrouter.ai/settings/integrations
  to use your own quota instead of the shared free-tier pool (avoids 429
  rate-limit errors).
- `TESSERACT_PATH`/`POPPLER_PATH` are machine-specific — update them after
  cloning onto a new computer.

## Usage

Run each pipeline stage standalone (useful for debugging):

```bash
python src/ocr_baseline.py data/samples/report.pdf         # OCR only -> data/output/*_raw.txt
python src/extract_baseline.py data/output/report_raw.txt  # regex extraction -> *_extracted.json
python src/extract_vlm.py data/samples/report.pdf          # VLM extraction -> *_vlm.json
```

Run the full dual pipeline as an API:

```bash
uvicorn src.api:app --reload
```

Then POST a PDF file to `http://127.0.0.1:8000/extract` (or use the
auto-generated docs at `http://127.0.0.1:8000/docs`).

## Target fields

Defined in `src/fields_config.py` (`FIELD_MAP`) — the single source of truth
used by both the OCR and VLM branches, so adding a new field only requires
editing this one file:

- `tong_tai_san` — Tổng tài sản (Total Assets)
- `doanh_thu_thuan` — Doanh thu thuần (Net Revenue)
- `loi_nhuan_sau_thue` — Lợi nhuận sau thuế (Net Profit After Tax)

## Status

- **OCR Pipeline** (Tesseract + regex): working, but unreliable alone on
  real reports — used only as the fast first attempt.
- **VLM Pipeline** (Gemma 4 31B via OpenRouter): working, verified accurate
  on a real 54-page VNM (Vinamilk) financial report.
- **Document Classifier & Router**: implemented — tries OCR first, falls
  back to VLM when any target field is missing.
- **Validation**: basic sanity checks implemented (negative values,
  revenue-vs-assets ratio).
- **Not yet done**: Docker, CI/CD, monitoring, retry logic for API rate
  limits — see `improvements-todo.md`.