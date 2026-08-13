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

# Giờ mới copy code
COPY src/ ./src/

EXPOSE 8000

CMD ["uvicorn", "api:app", "--app-dir", "src", "--host", "0.0.0.0", "--port", "8000"]