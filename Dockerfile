FROM python:3.12-slim

WORKDIR /app

# Poppler cho pdf2image. libgl1 + libglib2.0-0 là thư viện hệ thống mà
# OpenCV cần (EasyOCR và YOLO đều kéo theo OpenCV) — bản python:slim
# không có sẵn, thiếu là lỗi "libGL.so.1: cannot open shared object file".
RUN apt-get update && apt-get install -y --no-install-recommends \
    poppler-utils \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements TRƯỚC code, để sửa code không phải cài lại thư viện
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Tải sẵn checkpoint vào image thay vì để tải lúc chạy. Không có bước này,
# container lên "healthy" nhưng request ĐẦU TIÊN mới phải tải vài trăm MB:
# mạng chậm thì người dùng chờ vài phút, HuggingFace lỗi thì mọi request fail
# trong khi health check vẫn xanh. Cùng loại bug mà require_config() diệt —
# thứ hỏng chắc chắn thì phải lộ ra lúc khởi động, không phải giữa chừng.
#
# Đặt TRƯỚC "COPY src/" để sửa code không làm mất cache lớp này, cùng lý do
# requirements.txt được copy trước src/.
#
# CẢNH BÁO: ba chuỗi dưới đây trùng lặp với MODEL_ID/MODEL_FILENAME trong
# src/layout_detection.py và LANGUAGES trong src/ocr_baseline.py. Đổi ở đó
# thì phải đổi cả ở đây, nếu không image tải sẵn một model và runtime lại đi
# tải model khác — mất trắng tác dụng của bước này mà không có lỗi nào báo.
RUN python -c "\
from huggingface_hub import hf_hub_download; \
hf_hub_download(repo_id='juliozhao/DocLayout-YOLO-DocStructBench', \
                filename='doclayout_yolo_docstructbench_imgsz1024.pt'); \
import easyocr; easyocr.Reader(['vi', 'en'])"

# Giờ mới copy code
COPY src/ ./src/

EXPOSE 8000

CMD ["uvicorn", "api:app", "--app-dir", "src", "--host", "0.0.0.0", "--port", "8000"]