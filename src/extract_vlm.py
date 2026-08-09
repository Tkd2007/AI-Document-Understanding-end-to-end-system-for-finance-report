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
from fields_config import FIELD_MAP

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
    field_lines = "\n".join(f'- "{key}": tương ứng với dòng "{name}"' for key, name in FIELD_MAP.items())
    json_template = ", ".join(f'"{key}": <số hoặc null>' for key in FIELD_MAP)

    return f"""Bạn là một hệ thống trích xuất dữ liệu tài chính tự động.
Nhiệm vụ: nhìn vào ảnh trang báo cáo tài chính được cung cấp, tìm và trích xuất các chỉ tiêu sau:

{field_lines}

QUY TẮC BẮT BUỘC:
1. Chỉ trả về đúng 1 object JSON, KHÔNG thêm bất kỳ lời giải thích, lời chào, hay markdown (không dùng dấu ```) nào trước/sau JSON.
2. Số trả về phải là số nguyên thuần (integer), KHÔNG chứa dấu chấm, dấu phẩy hay ký hiệu đơn vị tiền tệ.
3. Nếu ảnh này KHÔNG chứa chỉ tiêu nào đó (không thấy trong ảnh), trả về null cho chỉ tiêu đó — TUYỆT ĐỐI KHÔNG được đoán hay bịa ra một con số gần đúng.
4. Chỉ lấy số liệu của kỳ báo cáo gần nhất (cột đầu tiên), không lấy số liệu kỳ so sánh trước đó.

Trả về đúng format JSON sau, không có gì khác:
{{{json_template}}}"""


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


def parse_response(text: str) -> dict | None:
    """
    Chuyển chuỗi text mà VLM trả về thành dict Python thật sự.

    Xử lý trường hợp model bọc thêm ```json ... ``` quanh JSON
    (dù prompt đã dặn không làm vậy, model vẫn hay làm).

    Quyết định thiết kế: KHÔNG crash chương trình khi parse lỗi.
    Lý do thực tế: 1 báo cáo có thể 50+ trang, nếu 1 trang model
    trả về rác thì không nên làm dừng toàn bộ các trang còn lại.
    Thay vào đó: in cảnh báo + trả về None, để nơi gọi tự quyết
    định bỏ qua trang đó.
    """
    cleaned = text.strip()

    if cleaned.startswith("```"):
        # bỏ dòng đầu (``` hoặc ```json) và dòng cuối (```)
        lines = cleaned.split("\n")
        lines = lines[1:]
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        cleaned = "\n".join(lines).strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        print(f"[WARNING] Không parse được JSON từ VLM: {e}")
        print(f"Nội dung nhận được (raw): {text!r}")
        return None


def extract_fields_from_document(file_path: str) -> dict:
    """
    Chạy VLM trên từng trang của document, gộp kết quả lại thành 1 dict.

    1 báo cáo tài chính thường nhiều trang: Tổng tài sản nằm ở trang
    Bảng cân đối kế toán, Doanh thu thuần/Lợi nhuận sau thuế nằm ở
    trang Báo cáo KQKD khác. Nên với mỗi field, lấy giá trị non-null
    ĐẦU TIÊN tìm thấy qua các trang (field nào trang trước không có,
    trang sau tìm tiếp; đã có rồi thì không ghi đè).
    """
    pages = load_pages(file_path)
    prompt = build_prompt()

    final_result = {key: None for key in FIELD_MAP}

    for i, page_img in enumerate(pages, start=1):
        base64_image = encode_image_to_base64(page_img)
        raw_text = call_vlm(base64_image, prompt)
        page_result = parse_response(raw_text)

        if page_result is None:
            print(f"--- Page {i}/{len(pages)}: bỏ qua (parse lỗi) ---")
            continue

        for key in final_result:
            if final_result[key] is None and page_result.get(key) is not None:
                final_result[key] = page_result[key]

        print(f"--- Page {i}/{len(pages)}: {page_result} ---")

        """
        Check nếu đã có hết tất cả dữ liệu cần thiết thì dừng
        """
        if all(value is not None for value in final_result.values()):
            print(f"--- Đã tìm đủ cả {len(FIELD_MAP)} field, dừng sớm ở trang {i}/{len(pages)} ---")
            break

    return final_result


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python extract_vlm.py <file_path>")
        sys.exit(1)

    input_path = sys.argv[1]
    result = extract_fields_from_document(input_path)

    out_path = Path("data/output") / (Path(input_path).stem + "_vlm.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(result)
    print(f"\nKết quả đã lưu tại: {out_path}")