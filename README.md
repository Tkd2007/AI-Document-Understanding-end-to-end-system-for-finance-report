# AI Document Understanding System — Financial Reports
![CI](https://github.com/Tkd2007/AI-Document-Understanding-end-to-end-system-for-finance-report/actions/workflows/ci.yml/badge.svg)

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
        │   · lưu tạm với hậu tố ngẫu nhiên, xoá sau khi xử lý xong
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
├── .github/
│   └── workflows/
│       └── ci.yml           # lint (ruff) + test (pytest) mỗi lần push
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
│   ├── api.py               # FastAPI Gateway: POST /extract endpoint
│   └── metrics.py           # đo thời gian từng stage + đếm lần gọi VLM
├── tests/
│   ├── test_extract_baseline.py
│   ├── test_router.py       # cổng quyết định fallback (không cần key/mạng)
│   └── test_validation.py
├── monitoring/
│   └── prometheus.yml       # scrape config, trỏ vào app:8000/metrics
├── docker-compose.yml       # app + Prometheus (sau profile "monitoring")
├── pytest.ini               # pythonpath = src, cho import phẳng
├── ruff.toml                # chốt bộ rule để CI và máy local giống nhau
├── .env                     # tự tạo — local secrets/config, never committed (see Setup)
├── .env.docker              # tự tạo — chỉ OPENROUTER_*, dùng khi chạy container
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
`load_page()` truyền `poppler_path=None` và `pdf2image` tự tìm được.

Lần build đầu mất 10–20 phút, chủ yếu là tải PyTorch. Các lần sau chỉ vài
giây: `Dockerfile` copy `requirements.txt` **trước** `src/`, nên sửa code
không làm mất cache của bước cài thư viện.

Kết quả ghi ra `/app/data/output/` **bên trong container** và mất đi khi
container dừng (do cờ `--rm`). Muốn giữ lại trên máy thì gắn volume:

```bash
docker run --rm -p 8000:8000 -v "${PWD}/data:/app/data" --env-file .env.docker doc-ai
```

#### Chạy kèm monitoring (docker compose)

```bash
docker compose up                            # chỉ app
docker compose --profile monitoring up       # app + Prometheus
```

Prometheus nằm sau `profiles` nên **không** khởi động mặc định. Lý do: nó chạy
nền và scrape `/metrics` mỗi 15 giây bất kể có ai dùng hay không, mà project này
chạy theo phiên làm việc chứ không phải 24/7 — bật khi cần xem số là đủ.

Kiểm tra theo đúng thứ tự này, mỗi bước xanh mới sang bước sau:

1. `curl 127.0.0.1:8000/metrics` — app có trả metric không
2. `127.0.0.1:9090/targets` — job `doc-ai` phải hiện **UP**
3. `127.0.0.1:9090/graph`, gõ `doc_ai_documents_total` — Prometheus có lưu được không

Bước 2 là chỗ bắt lỗi phổ biến nhất: `targets` trong `monitoring/prometheus.yml`
phải là **tên service** (`app:8000`), không phải `localhost:8000`. Mỗi container
là một network namespace riêng nên `localhost` trỏ về chính Prometheus.

Dừng và dọn:

| Lệnh | Tác dụng |
|---|---|
| `docker compose stop prometheus` | Ngừng scrape, giữ nguyên dữ liệu |
| `docker compose down` | Xoá container, **giữ** volume |
| `docker compose down -v` | Xoá cả volume — mất sạch lịch sử, không phục hồi được |

Dữ liệu Prometheus nằm trong named volume `prometheus_data` và tự xoá theo
`--storage.tsdb.retention.time=15d`, nên không phình vô hạn. Lúc hệ thống rảnh
thì gần như miễn phí: counter không đổi được nén theo độ lệch, một đêm 8 tiếng
không hoạt động chỉ tốn vài KB.

Đừng "tiết kiệm" bằng cách nới `scrape_interval` lên hàng giờ: `rate()` cần ít
nhất hai điểm trong cửa sổ truy vấn mới tính được độ lệch, nên interval quá thưa
khiến mọi truy vấn trả rỗng — hệ thống vẫn chạy, vẫn tốn RAM, và không nói gì.
Muốn tắt thì tắt hẳn container.

#### Checkpoint được tải sẵn vào image

`Dockerfile` gọi `hf_hub_download()` và `easyocr.Reader()` ngay lúc build, nên
container không cần mạng lúc chạy. Nếu để tải lúc runtime thì container lên
`healthy` rồi **request đầu tiên** mới phải tải vài trăm MB: mạng chậm là người
dùng chờ vài phút, HuggingFace lỗi là mọi request fail trong khi health check
vẫn xanh — cùng loại bug mà `require_config()` diệt.

Đánh đổi: image to thêm ~400 MB và build lần đầu lâu hơn. Dòng `RUN` đặt **trước**
`COPY src/` nên sửa code không làm mất cache lớp này.

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

Các version trong `requirements.txt` được **ghim** (`==`) chứ không để trôi:
đây đúng là bộ đã verify chạy trọn pipeline. Không ghim thì mỗi lần
`docker build` lại ra một bộ thư viện khác, và `easyocr`/`doclayout-yolo`
có thể kéo về bản `torch` không tương thích mà không còn cách nào biết bản
nào từng chạy được. Muốn nâng thì sửa số ở đó rồi chạy lại trên một báo cáo
thật, đừng nâng bằng cách bỏ ghim.

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
  "Vì sao nhánh OCR đang tắt mặc định" ở trên).
- `OPENROUTER_API_KEY` và `OPENROUTER_MODEL` là bắt buộc, kiểm bằng
  `require_config()`. Chỗ kiểm được đặt ở **entrypoint** chứ không phải lúc
  import module: `api.py` gọi lúc khởi động (thiếu key thì container chết
  ngay thay vì lên "healthy" rồi trả 500 ở từng request), `route_document()`
  gọi ở đầu mỗi lượt chạy — vẫn trước khi tốn công convert PDF và chạy YOLO.
  Nhờ vậy `import router` không đòi API key, nên phần logic thuần của router
  mới viết được unit test (xem `tests/test_router.py`).

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

> File upload được lưu tạm dưới tên `<tên gốc>_<8 ký tự ngẫu nhiên>.pdf` rồi xoá
> ngay sau khi xử lý xong. Hậu tố ngẫu nhiên là **bắt buộc chứ không phải cho
> đẹp**: hai người cùng upload `report.pdf` mà dùng nguyên tên client gửi lên thì
> request đến sau ghi đè file của request đang chạy — và vì `load_page()` mở lại
> file cho *từng trang*, request đầu sẽ đọc tiếp sang nội dung tài liệu kia rồi
> trả về số của một báo cáo khác. Kết quả trong `data/output/` vì thế cũng mang
> hậu tố đó (`report_a3f2b1c9_routed.json`) thay vì đè lên nhau.

Chạy standalone bằng `python src/router.py` thì không có chuyện đó — tên file
giữ nguyên và kết quả là `data/output/<file>_routed.json`.

> `route_document(file_path, save=True)` — tham số `save` quyết định có ghi
> `data/output/<stem>_routed.json` hay không, và **người gọi quyết định** chứ
> không phải pipeline, cùng nguyên tắc như `require_config()` được đẩy ra
> entrypoint.

#### Kết quả upload qua API được ghi ra file (trạng thái debug hiện tại)

`api.py` đang truyền `save=True`, nên **mỗi request để lại một file JSON** trong
`data/output/`:

```
data/output/VNM_Q1_2026_a3f2b1c9_routed.json
data/output/VNM_Q1_2026_7e4d0b88_routed.json    <- upload lần 2, cùng báo cáo
```

Hai điều cần biết khi dùng:

- **Tên file không đoán trước được.** Hậu tố 8 ký tự là hậu tố ngẫu nhiên của
  request (xem ghi chú về file upload ở trên), nên upload cùng một báo cáo nhiều
  lần sẽ ra nhiều file nội dung giống nhau. Tìm kết quả của lần chạy vừa rồi thì
  sắp theo thời gian sửa file, đừng tìm theo tên:

  ```bash
  ls -t data/output/*_routed.json | head -1     # Linux / macOS
  Get-ChildItem data/output/*_routed.json | Sort-Object LastWriteTime -Desc | Select -First 1   # PowerShell
  ```

- **Không có gì tự dọn.** `data/output/` phình theo số request. Dọn định kỳ bằng
  tay, chú ý giữ lại `metrics.jsonl`:

  ```bash
  rm data/output/*_routed.json
  ```

  Chạy bằng Docker thì file nằm trong container, chỉ ra tới máy bạn nếu đã gắn
  volume `./data:/app/data` (mặc định trong `docker-compose.yml` là có).

Trạng thái này là **tạm thời để debug**. Cùng dữ liệu đó đã có ở hai chỗ khác:
response HTTP, và `metrics.jsonl` — chỗ sau còn ghi được cả lượt chạy *thất bại*,
vì `metrics.save()` nằm trong `finally` còn `save_result()` thì không; dòng thất
bại nhận ra bằng khoá `"status": "error"`. Kế hoạch đổi về `save=False` nằm
trong `improvements-todo.md`.

Không cần file thì dùng CLI, tên giữ nguyên nên dễ tra:

```bash
python src/router.py data/samples/report.pdf   # -> data/output/report_routed.json
```

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

Chạy test và lint:

```bash
pytest
ruff check src tests
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
- **Monitoring**: `metrics.py` đo thời gian từng giai đoạn (`pdf_convert`,
  `layout`, `ocr`, `vlm`), đếm số lần gọi VLM và số lần lỗi, ghi mỗi lượt
  chạy thành một dòng JSON trong `data/output/metrics.jsonl`, và cộng dồn
  vào bộ đếm toàn cục cho endpoint `/metrics` (định dạng Prometheus).
  Mỗi dòng có khoá `status` — `"ok"` khi pipeline đi trọn, `"error"` khi ném
  lỗi giữa chừng, `"running"` nếu process chết trước cả khối `finally`. Lọc
  lượt chạy hỏng bằng chính khoá đó, đừng suy ra từ việc thiếu
  `info.pages_processed`:

  ```bash
  grep '"status": "error"' data/output/metrics.jsonl
  ```

  Truyền `metrics=None` thì mọi hàm vẫn chạy standalone như cũ.
  **Prometheus** đã dựng qua `docker-compose.yml`, scrape `/metrics` mỗi 15s và
  giữ 15 ngày. Grafana và Alertmanager chưa làm.
- **Unit test**: 15 test với `pytest`, không cần model hay mạng nên chạy
  trong vài giây. Đáng chú ý là test đẳng thức kế toán: sửa một chỉ tiêu
  lệch 10 triệu đồng trên tổng tài sản 47 nghìn tỷ vẫn bị bắt — kiểm chứng
  được lựa chọn `IDENTITY_TOLERANCE_RATIO=1e-7`. `test_router.py` phủ cổng
  quyết định fallback, gồm ca mọi field đều CÓ giá trị nhưng một con số bị
  đọc nhầm dòng — nếu cổng chỉ đếm field thì lỗi đó lọt qua âm thầm.
- **CI**: GitHub Actions chạy hai job mỗi lần push và pull request.
  - `test` — `ruff check` + `pytest`. Cố tình KHÔNG cài `requirements.txt`
    mà chỉ cài phần nhẹ (`numpy pillow openai python-dotenv`): `easyocr` và
    `doclayout-yolo` được import lười bên trong `get_reader()`/`get_model()`
    nên test không cần tới, mà cài đủ bộ là tải PyTorch ~2GB.
  - `docker` — build image rồi **chạy thử thật**: khởi động container và
    gọi `/metrics`. Build xong không đảm bảo chạy được; cả ba bug ở mục
    "Vài thứ chỉ lộ ra khi chạy thật" bên dưới đều chỉ lộ lúc runtime.

### Not yet done

- Đánh giá có hệ thống: chưa có tập test nhiều báo cáo từ nhiều công ty để
  đo accuracy, hiện mới verify tay trên một báo cáo.
- Unit test mới phủ phần logic thuần (parse số, validation, cổng fallback
  của router). Chưa có test cho OCR và VLM — những phần cần model hoặc gọi
  mạng, sẽ cần mock/fixture ảnh thay vì gọi thật.
- Monitoring: đã có thu thập per-run ra file, endpoint `/metrics` và Prometheus
  scrape + lưu lịch sử. Chưa có Grafana (dashboard) và Alertmanager (cảnh báo),
  chưa có Loki cho log.
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

- **Đo mới biết chi phí nằm ở đâu.** Comment trong code từng ghi YOLO là 
một trong hai việc đắt nhất pipeline. Metrics cho thấy ngược lại: convert 
PDF chiếm 59% tổng thời gian còn YOLO chỉ 15%. Tệ hơn, `convert_from_path`
render toàn bộ 55 trang trước lần `yield` đầu tiên, nên thiết kế generator 
không tiết kiệm được gì ở khâu đó — dừng sớm ở trang 10 vẫn trả đủ 169 
giây. Chuyển sang convert từng trang bằng `first_page`/`last_page` đưa con số 
đó xuống 12 giây và cắt 60% tổng thời gian chạy.