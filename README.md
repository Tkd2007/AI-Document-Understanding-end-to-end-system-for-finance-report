# AI Document Understanding System — Financial Reports
![CI](https://github.com/Tkd2007/AI-Document-Understanding-end-to-end-system-for-finance-report/actions/workflows/ci.yml/badge.svg)

End-to-end pipeline for extracting **27 structured financial line items**
(balance sheet, income statement, cash flow) from Vietnamese financial report
PDFs — 27 dưới chuẩn TT99, 26 dưới TT200.
Final project for the "MasterClass AI Document Understanding" course.

Repo hiện có **hai lớp**, và README này mô tả lớp thứ nhất:

1. **Pipeline trích xuất** — phần dưới đây. Chạy được, đã đóng gói Docker,
   có API và monitoring.
2. **Hạ tầng nghiên cứu** đang xây trên nhánh `research`: đo identifiability
   của hệ ràng buộc kế toán, định vị lỗi bằng ứng viên sinh từ chính tài
   liệu, và sửa lỗi bằng cách ĐỌC LẠI nguồn thay vì suy ra từ donor. Bốn
   giả thuyết và kế hoạch phân tích đã đăng ký trước ở
   [PREREGISTRATION.md](PREREGISTRATION.md); trạng thái thi công và các
   quyết định thiết kế ở [HANDOFF.md](HANDOFF.md).

## Mục lục

[Architecture](#architecture) · [Project structure](#project-structure) ·
[Setup](#setup) · [Usage](#usage) · [Target fields](#target-fields) ·
[Status](#status) · [Vài thứ chỉ lộ ra khi chạy thật](#vài-thứ-chỉ-lộ-ra-khi-chạy-thật)

Muốn chạy nhanh nhất: `docker build -t doc-ai . && docker run --rm -p 8000:8000
--env-file .env.docker doc-ai`, rồi mở `http://127.0.0.1:8000/docs`. Chi tiết
và các bẫy ở phần [Setup](#setup).

---

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
   Validation  (ép kiểu số, quy đổi đơn vị, sanity checks, warnings)
        │
        ▼
   JSON response  {"data": {...}, "meta": {...}, "confidence": {...}, "warnings": [...]}
```

Đường CLI (`python src/router.py <file>`) đi qua đúng chuỗi đó rồi ghi thêm
`data/output/<file>_routed.json`; đường API truyền `save=False` nên không ghi
file — chi tiết ở mục Usage.

### Router quyết định thế nào

Router coi kết quả là **đạt** khi thoả cả hai điều kiện:

1. Có đủ các chỉ tiêu **bắt buộc** (`required` trong `FIELD_RULES`) — không đòi đủ
   mọi field, vì danh sách càng dài thì càng dễ thiếu một chỉ tiêu phụ và lần nào
   cũng phải fallback. Điều này càng đúng sau khi Mốc 1 mở bộ chỉ tiêu lên 21.
2. `validate_result()` **không sinh warning nào**. Chỉ kiểm tra "có giá trị" là chưa
   đủ: regex có thể bắt trúng một con số SAI (không phải `None`) và router sẽ tin
   dùng luôn mà không bao giờ gọi VLM.

Khi chưa đạt thì gọi VLM. Nếu lý do chưa đạt là *có warning* (giá trị đang có nhưng
sai) thì VLM được phép **ghi đè**, chứ không chỉ lấp chỗ `None` — nếu không thì con
số sai vẫn nằm nguyên đó và cả validation gate thành vô nghĩa.

### Nhánh OCR — bật hay tắt, và vì sao

`USE_OCR_FIRST` trong `.env`. Nhánh OCR rẻ tiền hơn VLM nhưng chậm hơn
nhiều (EasyOCR chạy CPU), và nó đọc **số** rất chuẩn trong khi đọc **chữ
tiếng Việt có dấu** thì hỏng — `TỔNG TÀI SẢN` ra `TỖNG TÀISẢN` — nên nhánh
regex phải dò theo **mã số dòng** chứ không theo tên chỉ tiêu.

Hậu quả của việc bật hay tắt cờ này ghi ngay tại chỗ khai báo nó trong
`src/router.py`; số đo trước–sau ở [CHANGELOG.md](CHANGELOG.md). Không chép
lại ở đây — đoạn cũ tại chỗ này từng giữ một bảng `11/11 chỉ tiêu` đo dưới
bộ chỉ tiêu CŨ gồm 11 dòng, kèm chính lời cảnh báo rằng nó chưa đo lại sau
khi bộ chỉ tiêu mở lên 26–27 dòng.

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
│   ├── extraction_types.py  # FieldResult/Provenance/ExtractionResult, dùng chung
│   ├── fields_config.py     # single source of truth: fields, aliases, rules, checks
│   ├── validation.py        # ép kiểu số + sanity checks; cũng là gate quyết định fallback
│   ├── router.py            # Document Classifier & Router: OCR (optional) -> VLM
│   ├── api.py               # FastAPI Gateway: POST /extract endpoint
│   ├── metrics.py           # đo thời gian từng stage + đếm lần gọi VLM
│   ├── constraints.py       # ma trận ràng buộc A, hạng, không gian null (H0)
│   ├── repair/              # định vị và sửa lỗi bằng ứng viên sinh từ tài liệu
│   │   ├── candidates.py    #   sinh tập ứng viên từ chính trang giấy
│   │   └── diagnose.py      #   min-cardinality diagnosis + hai baseline đối chứng
│   └── eval/                # hạ tầng ĐO, tách hẳn khỏi hạ tầng CHẠY
│       ├── schema.py        #   định dạng ground truth
│       ├── metrics.py       #   chỉ số: lỗi câm, AUROC, top-k, chống bịa
│       ├── stats.py         #   bootstrap THEO CỤM TÀI LIỆU, McNemar
│       ├── split.py         #   chia tập theo TÀI LIỆU, không theo trang
│       ├── ocr_compare.py   #   đo engine OCR trên ô số (xem data/output/)
│       └── xbrl_tier/       #   tầng đánh giá quy mô lớn từ hồ sơ SEC XBRL
├── tests/                   # 318 test, không cần model và không cần mạng
│   ├── test_api.py          # giới hạn upload, dọn file tạm, /metrics
│   ├── test_constraints.py  # ma trận ràng buộc và identifiability
│   ├── test_diagnose.py     # định vị lỗi + baseline 8 và 9
│   ├── test_early_stop.py   # điều kiện dừng sớm và cờ tắt khi ĐO
│   ├── test_eval_stats.py   # bootstrap theo cụm, kiểm định ghép cặp
│   ├── test_metrics.py      # bộ đếm toàn cục + histogram cho /metrics
│   ├── test_ocr_compare.py  # bộ đo engine OCR (dùng engine giả)
│   ├── test_router.py       # cổng quyết định fallback (không cần key/mạng)
│   └── ...                  # provenance, units, standards, confidence, xbrl_tier
├── monitoring/
│   ├── prometheus.yml       # scrape config, trỏ vào app:8000/metrics
│   └── grafana/
│       ├── provisioning/
│       │   ├── datasources/prometheus.yml
│       │   └── dashboards/dashboards.yml    # provider, không phải dashboard
│       └── dashboards/                      # file .json export từ UI
├── docker-compose.yml       # app + Prometheus (sau profile "monitoring")
├── pytest.ini               # pythonpath = src, cho import phẳng
├── ruff.toml                # chốt bộ rule để CI và máy local giống nhau
├── .env                     # tự tạo — local secrets/config, never committed (see Setup)
├── .env.docker              # tự tạo — chỉ OPENROUTER_*, dùng khi chạy container
├── Dockerfile
├── .dockerignore
├── .gitignore
├── requirements.txt         # bộ chạy production, phiên bản ghim
├── requirements-dev.txt     # pytest + httpx, KHÔNG cài vào image
├── PREREGISTRATION.md       # đăng ký trước giả thuyết — dấu thời gian git là bằng chứng
├── HANDOFF.md               # trạng thái nghiên cứu, đọc trước khi làm tiếp
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

#### Chạy kèm monitoring

`docker compose up` dựng thêm Prometheus và Grafana. Cách dựng, cấu hình,
và bốn cái bẫy đã cắn thật khi làm dashboard: [docs/docker-va-monitoring.md](docs/docker-va-monitoring.md).

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
python -m pip install -r requirements.txt                          # để CHẠY
python -m pip install -r requirements.txt -r requirements-dev.txt  # để PHÁT TRIỂN
```

`pytest` và `httpx` nằm ở `requirements-dev.txt` chứ không ở bộ chính, vì
`Dockerfile` chỉ cài bộ chính và image production không có lý do gì mang
theo một bộ test framework không bao giờ được gọi.

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
DISABLE_CONSTRAINT_GATE=false
DISABLE_LINE_PROBE=false
GRAFANA_USER=admin
GRAFANA_PASSWORD=${GRAFANA_PASSWORD}
```

- Get an OpenRouter key at openrouter.ai/keys.
- Link your own Google AI Studio key at openrouter.ai/settings/integrations
  to use your own quota instead of the shared free-tier pool (avoids 429
  rate-limit errors).
- `POPPLER_PATH` is machine-specific — update it after cloning onto a new
  computer.
- `USE_OCR_FIRST` bật/tắt nhánh OCR + regex (mặc định `false` — xem
  "Vì sao nhánh OCR đang tắt mặc định" ở trên).
- `DISABLE_LINE_PROBE` tắt bước **dò sự tồn tại của dòng** (mặc định `false`,
  tức probe đang BẬT). Probe chạy EasyOCR trên các trang đã duyệt và tra theo
  **mã số dòng** để biết một chỉ tiêu vắng mặt trên biểu mẫu hay chỉ là đọc
  hỏng — hai chuyện trước đây cùng cho ra `null` và vì thế làm bước kiểm đẳng
  thức phải bỏ qua cả đẳng thức. Tắt là **mất tính năng, không sinh số sai**:
  không có dấu vết thì không chỉ tiêu nào được điền 0.
- `DISABLE_CONSTRAINT_GATE` **chỉ dùng khi ĐO, không dùng khi phục vụ**
  (mặc định `false`). Bật lên thì pipeline chạy đúng một nhánh, không gọi
  `is_acceptable()`, không fallback, và trả kết quả thô. Nó tồn tại vì
  pipeline thường đã dùng chính đẳng thức kế toán làm cổng quyết định
  fallback, nên đo "vi phạm ràng buộc dự báo lỗi tốt đến đâu" trên đầu ra
  đó là vòng lặp luận chứng — ta đánh giá một tín hiệu trên tập đã bị chính
  nó lọc. Lượt chạy nào ở chế độ này được đánh dấu bằng khoá
  `constraint_gate: false` trong `metrics.jsonl`, vì dữ liệu hai chế độ
  không so được với nhau.
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

> `route_document(file_path, save=True, standard=None)` — `standard` để `None`
> thì lùi về `DEFAULT_STANDARD` và ghi rõ việc lùi đó vào
> `meta["standard_nguon"]`. Tham số `save` quyết định có ghi
> `data/output/<stem>_routed.json` hay không, và **người gọi quyết định** chứ
> không phải pipeline, cùng nguyên tắc như `require_config()` được đẩy ra
> entrypoint.

#### Đường API không ghi file kết quả

`api.py` truyền `save=False`, nên upload qua HTTP **không để lại file nào** trong
`data/output/`. Cùng dữ liệu đó đã có ở hai chỗ: response HTTP, và
`metrics.jsonl` — chỗ sau còn ghi được cả lượt chạy *thất bại*, vì
`metrics.save()` nằm trong `finally` còn `save_result()` thì không; dòng thất bại
nhận ra bằng khoá `"status": "error"`.

File thứ ba từng tồn tại và đã bỏ: tên nó mang hậu tố ngẫu nhiên của request
(`VNM_Q1_2026_a3f2b1c9_routed.json`) nên upload cùng một báo cáo ba lần ra ba
file nội dung giống nhau mà không tra cứu theo tên được, và không có gì tự dọn.

Muốn có file thì dùng CLI, tên giữ nguyên nên dễ tra:

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

**Bộ chỉ tiêu: 27 với TT99, 26 với TT200** (kịch bản E, chốt 25/08/2026).
Chênh một chỉ tiêu vì Tài sản sinh học ngắn hạn chỉ tồn tại ở TT99.

**BA MÃ ĐỔI NGHĨA GIỮA HAI CHUẨN** — đây là nguồn lỗi câm, vì tra nhầm bảng mã
không làm gì nổ, nó chỉ lặng lẽ trả về một con số hợp lệ của chỉ tiêu khác:
mã **270** (Tổng cộng tài sản ở TT200, Tài sản dài hạn khác ở TT99), mã **150**
(Tài sản ngắn hạn khác ở TT200, Tài sản sinh học ở TT99), và mã **142/149**
(dự phòng giảm giá hàng tồn kho). Vì vậy `standard` là tham số **bắt buộc** của
`extract_field_by_code()` và của `validate_result()`.

**Danh sách đầy đủ nằm trong `FIELD_MAP` và `FIELD_LINE_CODES` của
`src/fields_config.py`.** Cố ý không chép bảng đó vào đây: chép ra là tạo bản
thứ hai của một sự thật, và bản trong README sẽ cũ đi mà không test nào bắt
được — đúng chuyện đã xảy ra, README này từng ghi 11 rồi 21 chỉ tiêu sau khi
code đã đổi.

Ba biểu mẫu được dùng: **B01** bảng cân đối kế toán (TT200) / báo cáo tình
hình tài chính (TT99), **B02** kết quả kinh doanh, **B03** lưu chuyển tiền tệ.
Chín đẳng thức kế toán nối chúng lại, khai báo ở `FIELD_IDENTITIES`.


## Status

- **Layout Detection** (DocLayout-YOLO): working — lọc trang không có bảng
  và cắt riêng từng vùng bảng trước khi đưa vào OCR/VLM.
- **OCR Pipeline** (EasyOCR + regex): working, bật/tắt bằng `USE_OCR_FIRST`
  trong `.env`. Nó là khoản đắt nhất của một lượt chạy, nên `run_ocr_first()`
  có bộ đếm kiên nhẫn `PATIENCE_PAGES_OCR` — dừng khi đã ngần ấy trang liên
  tiếp không trích thêm được chỉ tiêu nào. Trang nó dừng cũng là **trần của
  nhánh VLM**; lý do ở comment trong `src/extract_vlm.py`.
- **VLM Pipeline** (Gemma 4 31B via OpenRouter): working. Chạy ở
  `n_samples=1, temperature=0.0`, nên confidence trả về là **1,0 ở mọi
  trường** và con số đó nghĩa là *không đo được*, không phải *chắc chắn* —
  muốn đo H1 phải bật `n_samples > 1`. Có retry với exponential backoff khi
  gặp 429, và dừng sớm theo `PATIENCE_PAGES`.

### Số đo trên tập gold

**Không chép số vào đây.** Mọi con số trước–sau sống ở [CHANGELOG.md](CHANGELOG.md); hiện trạng lượt chấm mới nhất và các chế độ
lỗi đã đặt tên ở `HANDOFF.md` mục 17.4. Một bản sao số đo trong README là
một bản sao sẽ cũ đi mà không ai biết: đoạn cũ ở đây còn mô tả tập gold
lúc mới có mười tài liệu.

Chạy phép chấm: xem `CLAUDE.md` mục **Lệnh hay dùng**.

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

  Endpoint `/metrics` tách cùng thông tin đó thành ba counter:
  `doc_ai_documents_total` (mọi lượt chạy, ok + error),
  `doc_ai_documents_ok_total` và `doc_ai_documents_error_total`. Cả ba có
  mặt với giá trị 0 ngay từ lúc process khởi động, không đợi lượt lỗi đầu
  tiên — Prometheus chưa có series thì `rate()` trả rỗng và alert dựng trên
  nó không bao giờ bắn.
  Truyền `metrics=None` thì mọi hàm vẫn chạy standalone như cũ.
  Latency có **histogram** (`doc_ai_document_seconds`, và một histogram cho
  mỗi giai đoạn), nên `histogram_quantile()` dựng được p95/p99. Biên bucket
  chọn theo số đo thật trong `metrics.jsonl` chứ không theo cảm tính. Con số
  lấy từ bucket là **nội suy**, không phải phân vị thật — muốn chính xác thì
  đọc từng số đo trong `metrics.jsonl`.
  **Prometheus** scrape `/metrics` mỗi 15s, giữ 15 ngày. Grafana dựng qua
  provisioning nên dashboard nằm trong repo. Chưa có Alertmanager (cảnh báo)
  và Loki (log).
- **Unit test**: `pytest`, không cần model hay mạng nên chạy trong vài giây.
  Đáng chú ý là test đẳng thức kế toán: sửa một chỉ tiêu lệch 10 triệu đồng
  trên tổng tài sản 47 nghìn tỷ vẫn bị bắt, tức `IDENTITY_TOLERANCE_RATIO=1e-7`
  làm đúng việc của nó. Số test hiện tại lấy bằng `pytest -q`, không chép
  vào đây.
- **CI**: GitHub Actions chạy hai job mỗi lần push và pull request.
  - `test` — `ruff check` + `pytest`. Cố tình KHÔNG cài `requirements.txt`
    mà chỉ cài phần nhẹ: `easyocr` và `doclayout-yolo` được import lười bên
    trong `get_reader()`/`get_model()` nên test không cần tới, mà cài đủ bộ
    là tải PyTorch ~2GB. Danh sách cài phải phủ MỌI thư viện được import ở
    mức module trong `src/` và `tests/` — thiếu một cái thì pytest hỏng ở
    bước *collect*, tức cả file test biến mất chứ không phải một test đỏ, và
    số test giảm mà không ai để ý. Đã xảy ra một lần với `scipy`.
  - `docker` — build image rồi **chạy thử thật**: khởi động container và
    gọi `/metrics`. Build xong không đảm bảo chạy được; cả ba bug ở mục
    "Vài thứ chỉ lộ ra khi chạy thật" bên dưới đều chỉ lộ lúc runtime.

### Chưa làm — phần thuộc tầng repo

Việc đang dở của phần NGHIÊN CỨU nằm ở `HANDOFF.md` mục 16 và 17.4, không
chép lại ở đây.

- Monitoring: đã có thu thập per-run ra file, endpoint `/metrics` kèm
  histogram latency, Prometheus scrape và lưu lịch sử. Chưa có Alertmanager
  (cảnh báo), chưa có Loki cho log.
- Chặn upload lớn mới làm ở tầng ứng dụng (`MAX_UPLOAD_BYTES` trong
  `api.py`). Nó ngăn được việc nạp cả file vào RAM, nhưng KHÔNG ngăn được
  việc truyền dữ liệu lên — chỗ chặn đúng là reverse proxy, tầng repo này
  chưa có.
- Chưa có test cho OCR và VLM — những phần cần model hoặc gọi mạng, sẽ cần
  mock hoặc fixture ảnh thay vì gọi thật.

Nhật ký thay đổi kèm số đo trước và sau: [CHANGELOG.md](CHANGELOG.md).


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