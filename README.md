# AI Document Understanding System — Financial Reports

End-to-end pipeline for extracting structured financial data (Total Assets,
Net Revenue, Net Profit After Tax) from Vietnamese financial report PDFs.
Final project for the "MasterClass AI Document Understanding" course.

## Architecture

```
Client (PDF / image upload)
        │
        ▼
   FastAPI Gateway  (POST /extract)
        │   · làm sạch tên file, kiểm tra định dạng
        ▼
   Layout Detection  (DocLayout-YOLO)
        │   · bỏ qua trang không có bảng
        │   · cắt riêng từng vùng bảng để giảm nhiễu
        │   · chạy MỘT LẦN, dùng chung cho cả hai nhánh bên dưới
        ▼
Document Classifier & Router
   ├── OCR Pipeline   (EasyOCR + regex — rẻ, nhanh, thử trước)
   └── VLM Pipeline   (Vision-Language Model — fallback khi OCR thiếu field)
        │
        ▼
   save_result()  →  data/output/<file>_routed.json
        │
        ▼
   Validation  (ép kiểu số, sanity checks, warnings)
        │
        ▼
   JSON response  {"data": {...}, "warnings": [...]}
```

Router chỉ gọi VLM khi nhánh OCR còn thiếu field — VLM chính xác hơn nhưng
chậm và tốn tiền hơn, nên chỉ dùng khi thật sự cần.

## Project structure

```
doc-ai-project/
├── data/
│   ├── samples/             # input PDFs/images (gitignored except demo sample)
│   └── output/              # pipeline outputs (gitignored)
├── src/
│   ├── layout_detection.py  # Step 0: page image -> table regions (DocLayout-YOLO)
│   ├── ocr_baseline.py      # Step 1: document -> raw text (EasyOCR)
│   ├── extract_baseline.py  # Step 2 (OCR branch): raw text -> structured JSON (regex)
│   ├── extract_vlm.py       # Step 2 (VLM branch): table images -> structured JSON (VLM)
│   ├── fields_config.py     # single source of truth for target fields
│   ├── router.py            # Document Classifier & Router: OCR first, VLM fallback
│   └── api.py               # FastAPI Gateway: POST /extract endpoint + validation
├── .env                     # local secrets/config, never committed (see Setup)
├── .gitignore
├── requirements.txt
└── README.md
```

## Setup

### 1. Install system dependencies (Windows)

- **Poppler for Windows** (cần cho `pdf2image` để convert PDF sang ảnh) —
  https://github.com/oschwartz10612/poppler-windows/releases/

Không cần cài Tesseract. Pipeline đã chuyển sang EasyOCR, chạy hoàn toàn
bằng Python nên không phụ thuộc binary OCR bên ngoài.

### 2. Install Python dependencies

```bash
python -m pip install -r requirements.txt
```

Lần chạy đầu tiên sẽ tự tải checkpoint của EasyOCR và DocLayout-YOLO về
cache — mất vài phút và cần mạng, các lần sau thì không.

### 3. Configure `.env`

Create a `.env` file in the project root (this file is gitignored — never commit it):

```
POPPLER_PATH=C:\poppler\poppler-XX.XX.X\Library\bin
OPENROUTER_API_KEY=your_openrouter_key
OPENROUTER_MODEL=google/gemma-4-31b-it:free
```

- Get an OpenRouter key at openrouter.ai/keys.
- Link your own Google AI Studio key at openrouter.ai/settings/integrations
  to use your own quota instead of the shared free-tier pool (avoids 429
  rate-limit errors).
- `POPPLER_PATH` is machine-specific — update it after cloning onto a new
  computer.

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

Response format:

```json
{
  "data": {
    "tong_tai_san": 47775826926383,
    "doanh_thu_thuan": 13217639635987,
    "loi_nhuan_sau_thue": 2049247209782
  },
  "warnings": []
}
```

## Target fields

Defined in `src/fields_config.py` — the single source of truth used by both
the OCR and VLM branches, so adding a new field only requires editing this
one file:

- `tong_tai_san` — Tổng tài sản (Total Assets)
- `doanh_thu_thuan` — Doanh thu thuần (Net Revenue)
- `loi_nhuan_sau_thue` — Lợi nhuận sau thuế (Net Profit After Tax)

`FIELD_MAP` là danh sách field chuẩn. Riêng nhánh regex cần thêm
`FIELD_ALIASES` (các cách gọi khác nhau của cùng một chỉ tiêu, xếp từ cụ thể
tới chung chung) và `FIELD_EXCLUDE` (cụm từ loại trừ, để "Lợi nhuận sau
thuế" không khớp nhầm "Lợi nhuận sau thuế chưa phân phối"). Nhánh VLM không
cần hai bảng này vì model tự hiểu ngữ nghĩa.

### Vì sao regex phải khó tính đến vậy

Bảng BCTC Việt Nam có cột **Mã số** và **Thuyết minh** nằm chen giữa tên chỉ
tiêu và giá trị:

```
Doanh thu thuần về bán và cung cấp dịch vụ    10    VI.1    13.217.639.635.987
                                          (mã số) (t.minh)      (giá trị)
```

Nên regex "lấy số ngay sau nhãn" sẽ bắt được `10` chứ không phải giá trị.
Cách xử lý: chỉ chấp nhận con số **có dấu phân cách nghìn** — giá trị tiền
tệ luôn có, còn mã số và số thuyết minh thì không.

## Status

- **Layout Detection** (DocLayout-YOLO): working — lọc trang không có bảng
  và cắt riêng từng vùng bảng trước khi đưa vào OCR/VLM.
- **OCR Pipeline** (EasyOCR + regex): working — đã verify trích đúng cả 3
  chỉ tiêu trên báo cáo VNM (Vinamilk) Q1/2026, khớp với kết quả VLM.
- **VLM Pipeline** (Gemma 4 31B via OpenRouter): working, verified accurate
  on the same 54-page report. Có retry với exponential backoff khi gặp 429.
- **Document Classifier & Router**: implemented — tries OCR first, falls
  back to VLM when any target field is missing. Layout detection và convert
  PDF chỉ chạy một lần, dùng chung cho cả hai nhánh.
- **Validation**: ép kiểu số (VLM đôi khi trả string), cảnh báo giá trị âm
  bất thường, tỷ lệ doanh thu/tài sản, và field không trích được.

### Not yet done

- Đánh giá có hệ thống: chưa có tập test nhiều báo cáo từ nhiều công ty để
  đo accuracy, hiện mới verify tay trên một báo cáo.
- Chưa có unit test.
- Docker, CI/CD, monitoring.
- Chuẩn hoá đơn vị tính: prompt yêu cầu VLM giữ nguyên đơn vị hiển thị trong
  ảnh, nên hai báo cáo dùng đơn vị khác nhau ("đồng" vs "triệu đồng") sẽ cho
  ra số không cùng thang đo. Cần thêm field đơn vị hoặc bước quy đổi.
