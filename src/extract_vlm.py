"""
Pipeline step 2 (VLM branch): Document -> Structured JSON via VLM

Sends page images directly to a Vision-Language Model, skipping
the OCR text step entirely.
"""

import os
import sys
import json
import base64
from io import BytesIO
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI
from PIL import Image

from ocr_baseline import load_pages   # tái sử dụng hàm cũ, không viết lại

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
)
MODEL = os.getenv("OPENROUTER_MODEL")


def encode_image_to_base64(image: Image.Image) -> str:
    buffer = BytesIO()   # tạo "file giả" rỗng, chưa có gì bên trong
    image.save(buffer, format="PNG")   # "ghi" ảnh vào buffer, giống ghi vào file .png
    image_bytes = buffer.getvalue()   # kiểu dữ liệu: bytes (dãy số nhị phân thô)
    base64_bytes = base64.b64encode(image_bytes)
    return base64_bytes.decode("utf-8")


def build_prompt() -> str:
    return """Bạn là một hệ thống trích xuất dữ liệu tài chính tự động.
Nhiệm vụ: nhìn vào ảnh trang báo cáo tài chính được cung cấp, tìm và trích xuất các chỉ tiêu sau:

- "tong_tai_san": tương ứng với dòng "Tổng tài sản" (thường nằm trong Bảng cân đối kế toán, mục TÀI SẢN)
- "doanh_thu_thuan": tương ứng với dòng "Doanh thu thuần" (thường nằm trong Báo cáo kết quả hoạt động kinh doanh)
- "loi_nhuan_sau_thue": tương ứng với dòng "Lợi nhuận sau thuế" hoặc "Lợi nhuận sau thuế TNDN" (thường ở cuối Báo cáo kết quả hoạt động kinh doanh)

QUY TẮC BẮT BUỘC:
1. Chỉ trả về đúng 1 object JSON, KHÔNG thêm bất kỳ lời giải thích, lời chào, hay markdown (không dùng dấu ```) nào trước/sau JSON.
2. Số trả về phải là số nguyên thuần (integer), KHÔNG chứa dấu chấm, dấu phẩy hay ký hiệu đơn vị tiền tệ.
3. Nếu ảnh này KHÔNG chứa chỉ tiêu nào đó (không thấy trong ảnh), trả về null cho chỉ tiêu đó — TUYỆT ĐỐI KHÔNG được đoán hay bịa ra một con số gần đúng.
4. Chỉ lấy số liệu của kỳ báo cáo gần nhất (cột đầu tiên), không lấy số liệu kỳ so sánh trước đó.

Trả về đúng format JSON sau, không có gì khác:
{"tong_tai_san": <số hoặc null>, "doanh_thu_thuan": <số hoặc null>, "loi_nhuan_sau_thue": <số hoặc null>}"""


def call_vlm(base64_image: str, prompt: str) -> str:
    response = client.chat.completions.create(
        model = MODEL,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}}
                ]
            }
        ]
    )
    return response.choices[0].message.content