# Chạy kèm monitoring — docker compose, Prometheus, Grafana

Tách khỏi `README.md` ngày 03/09/2026. Phần này dài hơn cả mục cài đặt mà
chỉ cần tới khi thật sự dựng dashboard, nên nó không đáng nằm trên đường
đọc của người mới clone repo.

Cách chạy tối thiểu — chỉ API, không monitoring — vẫn ở `README.md`.

---

## Chạy kèm monitoring (docker compose)

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

Ở bước 1, ba counter `doc_ai_documents_total`, `doc_ai_documents_ok_total` và
`doc_ai_documents_error_total` phải hiện ra ngay cả khi chưa xử lý tài liệu nào —
cả ba bằng 0. Tỷ lệ lỗi trong 5 phút gần nhất:

```promql
rate(doc_ai_documents_error_total[5m]) / rate(doc_ai_documents_total[5m])
```

Lúc không có request nào thì cả tử lẫn mẫu đều bằng 0 và biểu thức trả rỗng, nên
alert dựng trên nó nhớ kèm điều kiện có lưu lượng, ví dụ
`rate(doc_ai_documents_total[5m]) > 0`.

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

## Grafana — dashboard

Grafana **không lưu số liệu**, nó chỉ gửi PromQL sang Prometheus rồi vẽ. Thứ
duy nhất nó sở hữu là định nghĩa dashboard và tài khoản đăng nhập — nên câu
hỏi kiến trúc duy nhất là: định nghĩa dashboard sống ở đâu?

Ở đây chọn **provisioning** (file trong repo) thay vì click trong UI (lưu vào
SQLite nội bộ container). Lý do: `docker compose down -v` rồi `up` lại vẫn ra
đúng dashboard đó, và thay đổi review được bằng `git diff`.

Ba loại file, hai cái đầu rất dễ nhầm nhau:

| File | Vai trò |
|---|---|
| `provisioning/datasources/prometheus.yml` | Prometheus nằm ở đâu |
| `provisioning/dashboards/dashboards.yml` | **không phải dashboard** — chỉ cho Grafana biết đi tìm file `.json` ở thư mục nào |
| `dashboards/*.json` | dashboard thật |

`/etc/grafana/provisioning` là đường dẫn **cố định** của image, không đổi được
bằng config. Còn `options.path` trong file thứ hai phải **khớp từng ký tự** với
vế phải của bind mount `dashboards` trong `docker-compose.yml` — lệch một ký tự
thì Grafana lên xanh, datasource có, dashboard rỗng, và không lỗi nào. Cùng loại
bẫy với `--config.file` của Prometheus.

Datasource trỏ `http://prometheus:9090` — **tên service**, không phải
`localhost`, và là cổng TRONG container. Cùng lý do đã ghi ở `prometheus.yml`.
Grafana không bao giờ nói chuyện với `app`: luồng là
`app → Prometheus → Grafana`, và FastAPI không hiểu PromQL.

### Biến môi trường

Thêm vào `.env` (KHÔNG phải `.env.docker`):
GRAFANA_USER=admin
GRAFANA_PASSWORD=<tự đặt>


Nghe ngược nhưng đúng: cú pháp `${...}` trong `docker-compose.yml` được
**Compose** thay thế lúc đọc file, nên nó đọc `.env` của thư mục chạy lệnh.
`env_file:` là chuyện khác — thứ đó truyền biến vào *trong* container.

Biến thiếu thì Compose mặc định thay bằng chuỗi rỗng và chỉ cảnh báo: Grafana
lên bình thường rồi không đăng nhập được bằng bất cứ thứ gì. Nên dùng cú pháp
`${GRAFANA_PASSWORD:?...}` để Compose chết ngay kèm câu giải thích — cùng tinh
thần với `require_config()`.

### Kiểm tra, mỗi bước xanh mới sang bước sau

1. `docker compose --profile monitoring up` — 3 container lên, không cái nào restart lặp
2. `127.0.0.1:3000` — đăng nhập bằng `GRAFANA_USER` / `GRAFANA_PASSWORD`
3. `Connections → Data sources` — Prometheus **đã có sẵn**, không phải tự thêm
4. `Explore` → gõ `doc_ai_documents_total` → ra series phẳng ở 0
5. Chạy một tài liệu thật, đợi 15–30s, xem số nhích lên

Bước 3 là chỗ phân biệt "provisioning chạy được" với "tự click thêm datasource".
Phải thêm tay nghĩa là mount `provisioning` sai — log Grafana lúc khởi động có
dòng cho biết nó đọc được mấy file.

Kiểm cấu trúc YAML mà chưa cần pull image:

```bash
docker compose --profile monitoring config --services
```

Dùng `--services`, đừng dùng `config` trần: lệnh trần resolve luôn `env_file`
và **in `OPENROUTER_API_KEY` ra dạng thô**.

### PromQL cho panel

| Panel | Query |
|---|---|
| Service sống? | `up{job="doc-ai"}` |
| Throughput | `increase(doc_ai_documents_total[1h])` |
| Tỷ lệ lỗi | `rate(doc_ai_documents_error_total[5m]) / rate(doc_ai_documents_total[5m])` |
| Thời gian TB / tài liệu | `rate(doc_ai_seconds_total[5m]) / rate(doc_ai_documents_total[5m])` |
| Thời gian TB theo stage | `rate(doc_ai_stage_vlm_seconds_total[5m]) / rate(doc_ai_documents_total[5m])` |
| Tỷ lệ gọi VLM hỏng | `rate(doc_ai_vlm_failures_total[5m]) / rate(doc_ai_vlm_calls_total[5m])` |

Chỉ có **trung bình**, chưa có p95/p99: `metrics.py` cộng dồn `seconds_total`
chứ không có histogram bucket. Muốn phân vị thật thì phải đổi kiến trúc bộ đếm.

### Ba thứ trông như dashboard hỏng nhưng không phải

- **Panel trống ≠ sai query.** Project chạy theo phiên, mỗi lượt mất vài phút,
  nên cửa sổ `[5m]` nhiều khi chỉ ôm được một điểm và `rate()` trả rỗng. Với
  throughput dùng `increase(...[1h])` cho dễ đọc.
- **Counter reset về 0 mỗi lần restart container.** `rate()` tự xử lý được,
  nhưng panel Stat gõ thẳng `doc_ai_documents_total` sẽ tụt về 0 sau mỗi
  `docker compose up`. Muốn tổng tích luỹ thì `increase(doc_ai_documents_total[30d])`.
- **Sửa panel trong UI KHÔNG cập nhật file trong repo.** `allowUiUpdates: true`
  cho phép lưu, nhưng lưu vào SQLite nội bộ. Sau vài lần chỉnh, cái nhìn thấy và
  cái trong git là hai thứ khác nhau mà `git diff` vẫn sạch. Quy trình bắt buộc:
  chỉnh UI → `Dashboard settings → JSON Model` → dán về
  `monitoring/grafana/dashboards/` → commit.

