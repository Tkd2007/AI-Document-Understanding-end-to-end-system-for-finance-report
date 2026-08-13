# AI Document Understanding System — Financial Reports

End-to-end pipeline for extracting **11 structured financial line items**
(balance sheet + income statement) from Vietnamese financial report PDFs.
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
   ├── OCR Pipeline   (EasyOCR + regex — rẻ, nhanh; TẮT mặc định, xem bên dưới)
   └── VLM Pipeline   (Vision-Language Model — đắt hơn nhưng đáng tin hơn)
        │
        ▼
   Validation  (ép kiểu số, sanity checks, warnings)
        │
        ▼
   save_result()  →  data/output/<file>_routed.json
        │
        ▼
   JSON response  {"data": {...}, "warnings": [...]}
```

### Router quyết định thế nào

Router coi kết quả là **đạt** khi thoả cả hai điều kiện:

1. Có đủ các chỉ tiêu **bắt buộc** (`required` trong `FIELD_RULES`) — không đòi đủ
   cả 11 field, vì danh sách càng dài thì càng dễ thiếu một chỉ tiêu phụ và lần nào
   cũng phải fallback.
2. `validate_result()` **không sinh warning nào**. Chỉ kiểm tra "có giá trị" là chưa
   đủ: regex có thể bắt trúng một con số SAI (không phải `None`) và router sẽ tin
   dùng luôn mà không bao giờ gọi VLM.

Khi chưa đạt thì gọi VLM. Nếu lý do chưa đạt là *có warning* (giá trị đang có nhưng
sai) thì VLM được phép **ghi đè**, chứ không chỉ lấp chỗ `None` — nếu không thì con
số sai vẫn nằm nguyên đó và cả validation gate thành vô nghĩa.

### Vì sao nhánh OCR đang tắt mặc định

`USE_OCR_FIRST=false`. Đo trên báo cáo VNM Q1/2026:

- EasyOCR đọc **số** rất chuẩn nhưng đọc **chữ tiếng Việt có dấu** thì hỏng
  (`TỔNG TÀI SẢN` → `TỖNG TÀISẢN`), trong khi regex lại phải khớp đúng tên chỉ tiêu.
- Lúc bị tắt, nhánh OCR quét hết 55 trang (chậm, EasyOCR chạy CPU) rồi vẫn thiếu
  field, sau đó mới gọi VLM — người dùng phải chờ trọn một nhánh vô ích.
- Nhánh VLM một mình trả đúng cả 11/11 field và dừng ở trang 10.

Từ đó regex đã khá lên nhiều nhờ dò theo **mã số dòng** và luật loại trừ hai chiều:
trên đúng OCR text ấy, nhánh regex hiện trích đúng **11/11 chỉ tiêu** và không sinh
warning nào — tức là sẽ không cần fallback VLM nữa. Nhưng mặc định vẫn để `false`
cho tới khi đo được trên nhiều báo cáo khác, vì đây mới là **một** tài liệu và
regex vốn nhạy với cách OCR cắt chữ ở từng bản in.

Code nhánh OCR được **giữ nguyên**, bật lại bằng `USE_OCR_FIRST=true` trong `.env`.

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
│   ├── fields_config.py     # single source of truth: fields, aliases, rules, checks
│   ├── validation.py        # ép kiểu số + sanity checks; cũng là gate quyết định fallback
│   ├── router.py            # Document Classifier & Router: OCR (optional) -> VLM
│   └── api.py               # FastAPI Gateway: POST /extract endpoint
├── .env                     # local secrets/config, never committed (see Setup)
├── .env.docker              # chỉ OPENROUTER_*, dùng khi chạy container
├── Dockerfile
├── .dockerignore
├── .gitignore
├── requirements.txt
└── README.md
```

## Setup

Có hai cách chạy. **Docker là cách được khuyến nghị**: không phải cài
Poppler, không phải chỉnh đường dẫn theo từng máy.

### Cách A — Docker (khuyến nghị)

Chỉ cần cài [Docker Desktop](https://www.docker.com/products/docker-desktop/).

```bash
docker build -t doc-ai .
docker run --rm -p 8000:8000 --env-file .env.docker doc-ai
```

Mở `http://127.0.0.1:8000/docs` để upload file và xem kết quả.

`.env.docker` chỉ gồm hai dòng (KHÔNG dùng chung `.env` với chạy local —
`POPPLER_PATH` trong đó là đường dẫn Windows, truyền vào container Linux
sẽ khiến `pdf2image` tìm sai chỗ):

OPENROUTER_API_KEY=your_openrouter_key 
OPENROUTER_MODEL=google/gemma-4-31b-it:free

Trong container, Poppler được cài qua `apt-get` nên nằm sẵn trong `PATH`;
`load_pages()` truyền `poppler_path=None` và `pdf2image` tự tìm được.

Lần build đầu mất 10–20 phút, chủ yếu là tải PyTorch. Các lần sau chỉ vài
giây: `Dockerfile` copy `requirements.txt` **trước** `src/`, nên sửa code
không làm mất cache của bước cài thư viện.

Kết quả ghi ra `/app/data/output/` **bên trong container** và mất đi khi
container dừng (do cờ `--rm`). Muốn giữ lại trên máy thì gắn volume:

```bash
docker run --rm -p 8000:8000 -v "${PWD}/data:/app/data" --env-file .env.docker doc-ai
```

### Cách B — chạy trực tiếp trên máy

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
USE_OCR_FIRST=false
```

- Get an OpenRouter key at openrouter.ai/keys.
- Link your own Google AI Studio key at openrouter.ai/settings/integrations
  to use your own quota instead of the shared free-tier pool (avoids 429
  rate-limit errors).
- `POPPLER_PATH` is machine-specific — update it after cloning onto a new
  computer.
- `USE_OCR_FIRST` bật/tắt nhánh OCR + regex (mặc định `false` — xem
  "Vì sao nhánh OCR đang tắt mặc định" ở trên). `OPENROUTER_API_KEY` và
  `OPENROUTER_MODEL` là bắt buộc: thiếu thì nhánh VLM báo lỗi ngay lúc import.

## Usage

Run each pipeline stage standalone (useful for debugging):

```bash
python src/ocr_baseline.py data/samples/report.pdf         # OCR only -> data/output/*_raw.txt
python src/extract_baseline.py data/output/report_raw.txt  # regex extraction -> *_extracted.json
python src/extract_vlm.py data/samples/report.pdf          # VLM extraction -> *_vlm.json
python src/router.py data/samples/report.pdf               # full router -> *_routed.json
```

> Lưu ý khi chạy `extract_baseline.py` trên raw text của **cả tài liệu**: text toàn
> văn chứa marker của nhiều mẫu biểu cùng lúc, nên lớp bảo vệ theo `FORM_MARKERS`
> mất tác dụng và việc dò theo mã số dòng có thể lấy nhầm (mã `10` là Doanh thu
> thuần ở B02a nhưng là Biến động hàng tồn kho ở B03a). Trong pipeline thật,
> `router.py` gọi hàm này theo **từng trang** nên không dính vấn đề đó.

Run the full dual pipeline as an API:

```bash
uvicorn api:app --app-dir src --reload
```

`--app-dir src` là bắt buộc: các module trong `src/` dùng import phẳng
(`from validation import ...`) nên chỉ resolve được khi `src/` nằm trên `sys.path`
— đúng như khi chạy `python src/router.py`. Không có cờ này thì
`uvicorn src.api:app` sẽ chết với `ModuleNotFoundError: No module named 'validation'`.

Then POST a PDF file to `http://127.0.0.1:8000/extract` (or use the
auto-generated docs at `http://127.0.0.1:8000/docs`).

Response format (giá trị thật từ báo cáo VNM Q1/2026, đơn vị VND):

```json
{
  "data": {
    "tai_san_ngan_han": 29403116984122,
    "hang_ton_kho": 5393002084291,
    "tai_san_dai_han": 18372709942261,
    "tong_tai_san": 47775826926383,
    "no_phai_tra": 16666572149360,
    "von_chu_so_huu": 31109254777023,
    "doanh_thu_thuan": 13217639635987,
    "gia_von_hang_ban": 7278764406353,
    "loi_nhuan_gop": 5938875229634,
    "loi_nhuan_truoc_thue": 2523887147085,
    "loi_nhuan_sau_thue": 2049247209782
  },
  "warnings": []
}
```

## Target fields

Defined in `src/fields_config.py` — the single source of truth used by both
the OCR and VLM branches, so adding a new field only requires editing this
one file.

**B01a-DN — Báo cáo tình hình tài chính (bảng cân đối kế toán)**

| Key | Chỉ tiêu | Mã số | Bắt buộc |
|---|---|---|---|
| `tai_san_ngan_han` | Tài sản ngắn hạn | 100 | |
| `hang_ton_kho` | Hàng tồn kho | 140 | |
| `tai_san_dai_han` | Tài sản dài hạn | 200 | |
| `tong_tai_san` | Tổng tài sản | 280 | ✅ |
| `no_phai_tra` | Nợ phải trả | 300 | |
| `von_chu_so_huu` | Vốn chủ sở hữu | 400 | |

**B02a-DN — Báo cáo kết quả hoạt động kinh doanh**

| Key | Chỉ tiêu | Mã số | Bắt buộc |
|---|---|---|---|
| `doanh_thu_thuan` | Doanh thu thuần | 10 | ✅ |
| `gia_von_hang_ban` | Giá vốn hàng bán | 11 | |
| `loi_nhuan_gop` | Lợi nhuận gộp | 20 | |
| `loi_nhuan_truoc_thue` | Lợi nhuận trước thuế | 50 | |
| `loi_nhuan_sau_thue` | Lợi nhuận sau thuế | 60 | ✅ |

### Các bảng cấu hình trong `fields_config.py`

| Bảng | Dùng cho | Vai trò |
|---|---|---|
| `FIELD_MAP` | cả hai nhánh | danh sách field chuẩn + tên tiếng Việt |
| `FIELD_RULES` | validation | `allow_negative`, `required` cho từng field |
| `FIELD_RELATIONS` | validation | bất đẳng thức (Hàng tồn kho ≤ Tài sản ngắn hạn…) |
| `FIELD_IDENTITIES` | validation | đẳng thức kế toán (TSNH + TSDH = Tổng TS…) |
| `FIELD_RATIO_BOUNDS` | validation | biên tỷ trọng, bắt lỗi lệch bậc độ lớn |
| `FIELD_ALIASES` | nhánh regex | các cách gọi của cùng chỉ tiêu, xếp cụ thể → chung |
| `FIELD_EXCLUDE` | nhánh regex | cụm từ loại trừ, theo vị trí `before` / `between` |
| `FIELD_LINE_CODES` | regex + prompt VLM | mã số dòng theo mẫu biểu |
| `FORM_MARKERS` | nhánh regex | nhận diện trang thuộc mẫu B01a / B02a / B03a |

Nhánh VLM không cần `FIELD_ALIASES` / `FIELD_EXCLUDE` / `FORM_MARKERS` vì model
tự hiểu ngữ nghĩa của dòng.

### Vì sao regex phải khó tính đến vậy

**1. Cột Mã số và Thuyết minh chen giữa nhãn và giá trị:**

```
Doanh thu thuần về bán và cung cấp dịch vụ    10    VI.1    13.217.639.635.987
                                          (mã số) (t.minh)      (giá trị)
```

Nên regex "lấy số ngay sau nhãn" sẽ bắt được `10` chứ không phải giá trị.
Cách xử lý: chỉ chấp nhận con số **có dấu phân cách nghìn** — giá trị tiền
tệ luôn có, còn mã số và số thuyết minh thì không.

**2. Tên chỉ tiêu KHÔNG duy nhất trong tài liệu.** Một alias ngắn có thể nằm gọn
ở *đầu* nhãn khác ("Lợi nhuận sau thuế" trong "…chưa phân phối") hoặc ở *đuôi*
("Hàng tồn kho" trong "Dự phòng giảm giá hàng tồn kho" — mã 142, một khoản âm nhỏ
hơn giá trị thật khoảng 1000 lần). Vì vậy `FIELD_EXCLUDE` soi **cả hai chiều**:

```python
"loi_nhuan_sau_thue": {"between": ["chưa phân", ...]},   # từ khoá đứng SAU nhãn
"hang_ton_kho":       {"before":  ["giảm giá", ...]},    # từ khoá đứng TRƯỚC nhãn
```

**3. OCR làm hỏng chữ tiếng Việt có dấu.** Khi không alias nào khớp, hệ thống dò
tiếp theo **mã số dòng** (`FIELD_LINE_CODES`): trên báo cáo VNM, EasyOCR đọc
`TỔNG TÀI SẢN` thành `TỖNG TÀISẢN` nên alias thất bại, còn mã `280` thì đọc đúng
tuyệt đối. Mã số chỉ duy nhất **trong một mẫu biểu**, nên chỉ được dùng khi trang
khớp `FORM_MARKERS` của đúng mẫu đó.

## Status

- **Layout Detection** (DocLayout-YOLO): working — lọc trang không có bảng
  và cắt riêng từng vùng bảng trước khi đưa vào OCR/VLM.
- **OCR Pipeline** (EasyOCR + regex): working nhưng **tắt mặc định**
  (`USE_OCR_FIRST=false`). Trên OCR text của báo cáo VNM Q1/2026, kết hợp alias +
  mã số dòng hiện trích đúng **11/11 chỉ tiêu**, nhưng vẫn chậm hơn nhiều so với
  chạy thẳng VLM — xem phần lý do ở trên.
- **VLM Pipeline** (Gemma 4 31B via OpenRouter): working, verified accurate
  on the same 54-page report — 11/11 field, dừng sớm ở trang 10. Có retry với
  exponential backoff khi gặp 429, và dừng sớm theo `PATIENCE_PAGES`.
- **Document Classifier & Router**: implemented — gọi VLM khi kết quả chưa đủ
  field bắt buộc **hoặc** validation còn warning. Layout detection và convert
  PDF chỉ chạy một lần, dùng chung cho cả hai nhánh.
- **Validation**: 7 lớp kiểm tra — ép kiểu số (VLM đôi khi trả string), giá trị âm
  bất thường, bất đẳng thức giữa các chỉ tiêu, **đẳng thức kế toán** (chặt nhất:
  lệch một chữ số là lộ ngay), biên tỷ trọng, tỷ lệ doanh thu/tài sản, và thiếu
  chỉ tiêu bắt buộc.
  - **Docker**: working — đã build và chạy thử thành công, xử lý được trọn
  pipeline (YOLO + VLM) qua endpoint HTTP trong container. Image cài sẵn
  `poppler-utils` nên bỏ được phụ thuộc ngoài duy nhất còn lại; không cần
  `POPPLER_PATH` khi chạy bằng Docker.

### Not yet done

- Đánh giá có hệ thống: chưa có tập test nhiều báo cáo từ nhiều công ty để
  đo accuracy, hiện mới verify tay trên một báo cáo.
- Chưa có unit test.
- CI/CD, monitoring.
- Chuẩn hoá đơn vị tính: prompt yêu cầu VLM giữ nguyên đơn vị hiển thị trong
  ảnh, nên hai báo cáo dùng đơn vị khác nhau ("đồng" vs "triệu đồng") sẽ cho
  ra số không cùng thang đo. Cần thêm field đơn vị hoặc bước quy đổi.


## Vài thứ chỉ lộ ra khi chạy thật

- **Build thử Dockerfile là bắt buộc, không phải tuỳ chọn.** Lần chạy đầu
  trong container lộ ra ba thứ chưa từng gặp khi chạy trên Windows:
  `uvicorn` mặc định chỉ nghe `127.0.0.1` nên bên ngoài không vào được
  (phải `--host 0.0.0.0`), import phẳng trong `src/` cần `--app-dir src`,
  và `python:slim` thiếu thư viện hệ thống mà OpenCV cần.

- **Một bug thật lộ ra nhờ chạy container:** OpenRouter thỉnh thoảng trả
  HTTP 200 nhưng `choices` là `null`. Không có exception nào để `except`
  bắt, nên nó lọt qua toàn bộ retry logic và giết cả request giữa chừng —
  dù `call_vlm()` vốn được thiết kế để không bao giờ làm sập pipeline.

- **Fail open ở Layout Detection đã cứu dữ liệu thật.** Log cho thấy YOLO
  không nhận ra bảng ở trang 7 (bảng BCTC Việt Nam không kẻ khung nên bị
  phân loại thành `plain text`), nhưng vì pipeline trả về nguyên trang
  thay vì bỏ qua, VLM vẫn trích đúng hai chỉ tiêu từ trang đó.