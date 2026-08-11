"""
Pipeline step 2 (VLM branch): Document -> Structured JSON via VLM

Sends page images directly to a Vision-Language Model, skipping
the OCR text step entirely.
"""

import os
import sys
import json
import time
import base64
from io import BytesIO
from pathlib import Path

from dotenv import load_dotenv
from openai import (
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    OpenAI,
    RateLimitError,
)
from PIL import Image

from ocr_baseline import load_table_regions   # tái sử dụng hàm cũ, không viết lại
from fields_config import FIELD_MAP

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
)
MODEL = os.getenv("OPENROUTER_MODEL")

MAX_RETRIES = 3
RETRY_BASE_DELAY = 2.0   # giây, nhân đôi sau mỗi lần thất bại: 2 -> 4 -> 8

# Lỗi tạm thời, thử lại thì có cơ may thành công.
RETRYABLE_ERRORS = (RateLimitError, APIConnectionError, APITimeoutError)


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
3. Nếu số liệu trong ảnh là số âm (thể hiện bằng dấu "-" hoặc đặt trong ngoặc đơn, ví dụ "(1.234.567)"), PHẢI giữ lại dấu âm trong JSON (ví dụ -1234567). Đây là trường hợp rất thường gặp với "Lợi nhuận sau thuế" khi doanh nghiệp thua lỗ.
4. Giữ nguyên đơn vị tính như số liệu hiển thị trong ảnh (ví dụ nếu bảng ghi "Đơn vị tính: triệu đồng" thì trả về đúng con số theo đơn vị triệu đồng đó), KHÔNG tự quy đổi sang đơn vị khác.
5. Nếu ảnh này KHÔNG chứa chỉ tiêu nào đó (không thấy trong ảnh), trả về null cho chỉ tiêu đó — TUYỆT ĐỐI KHÔNG được đoán hay bịa ra một con số gần đúng.
6. Chỉ lấy số liệu của kỳ báo cáo gần nhất. Xác định cột này dựa vào NHÃN/TIÊU ĐỀ cột (ngày, quý, năm — kỳ có ngày gần hiện tại nhất), KHÔNG mặc định dựa vào vị trí cột đầu tiên bên trái, vì thứ tự cột có thể khác nhau giữa các mẫu báo cáo. Không lấy số liệu của kỳ so sánh (kỳ trước).
7. Bảng báo cáo tài chính Việt Nam thường có cột "Mã số" (số nhỏ 2-3 chữ số như 10, 60, 270) và cột "Thuyết minh" (ký hiệu như VI.1) nằm giữa tên chỉ tiêu và giá trị. TUYỆT ĐỐI KHÔNG lấy nhầm mã số hay số thuyết minh làm giá trị — giá trị là con số tiền tệ lớn nằm ở các cột bên phải.
8. Tên chỉ tiêu trong ảnh có thể đi kèm số thứ tự/tiền tố (ví dụ "A.", "I.", "1.") hoặc viết hoa toàn bộ, hoặc diễn đạt hơi khác so với tên liệt kê ở trên — hãy nhận diện dựa trên Ý NGHĨA của dòng, không yêu cầu khớp chính xác từng ký tự.

Trả về đúng format JSON sau, không có gì khác:
{{{json_template}}}"""


def call_vlm(base64_image: str, prompt: str) -> str | None:
    """
    Gọi VLM, tự thử lại khi gặp lỗi tạm thời.

    Model free tier trên OpenRouter dính 429 (rate limit) khá thường, và
    một báo cáo có thể 50+ trang. Trước đây một lỗi mạng ở giữa chừng là
    làm hỏng cả lượt chạy. Trả về None khi đã hết lượt thử, để nơi gọi tự
    quyết định bỏ qua trang đó — cùng triết lý với parse_response().
    """
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = client.chat.completions.create(
                model=MODEL,
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

        except RETRYABLE_ERRORS as e:
            error = e

        except APIStatusError as e:
            # 4xx là lỗi từ phía mình (sai API key, sai tên model, ảnh quá
            # lớn) — thử lại bao nhiêu lần cũng vẫn hỏng, dừng luôn.
            if e.status_code < 500:
                print(f"[ERROR] VLM trả lỗi {e.status_code}, không thử lại: {e}")
                return None
            error = e

        if attempt == MAX_RETRIES:
            print(f"[WARNING] Gọi VLM thất bại sau {MAX_RETRIES} lần thử: {error}")
            return None

        delay = RETRY_BASE_DELAY * 2 ** (attempt - 1)
        print(f"[WARNING] Lỗi gọi VLM (lần {attempt}/{MAX_RETRIES}): {error} — thử lại sau {delay:.0f}s")
        time.sleep(delay)

    return None


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
    except json.JSONDecodeError:
        pass

    # Vớt vát: model thỉnh thoảng vẫn kèm một câu dẫn trước/sau JSON.
    # Lấy đoạn từ dấu "{" đầu tiên đến dấu "}" cuối cùng rồi thử lại.
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start != -1 and end > start:
        try:
            return json.loads(cleaned[start:end + 1])
        except json.JSONDecodeError:
            pass

    print("[WARNING] Không parse được JSON từ VLM")
    print(f"Nội dung nhận được (raw): {text!r}")
    return None


def extract_fields_from_regions(pages: list[dict]) -> dict:
    """
    Chạy VLM trên từng vùng bảng đã cắt sẵn, gộp kết quả lại thành 1 dict.

    1 báo cáo tài chính thường nhiều trang: Tổng tài sản nằm ở trang
    Bảng cân đối kế toán, Doanh thu thuần/Lợi nhuận sau thuế nằm ở
    trang Báo cáo KQKD khác. Nên với mỗi field, lấy giá trị non-null
    ĐẦU TIÊN tìm thấy qua các trang (field nào trang trước không có,
    trang sau tìm tiếp; đã có rồi thì không ghi đè).
    """
    prompt = build_prompt()
    final_result = {key: None for key in FIELD_MAP}

    for page in pages:
        page_no = page["page"]

        for region in page["regions"]:
            base64_image = encode_image_to_base64(region)
            raw_text = call_vlm(base64_image, prompt)

            if raw_text is None:
                print(f"--- Page {page_no}: bỏ qua (gọi VLM thất bại) ---")
                continue

            page_result = parse_response(raw_text)
            if page_result is None:
                print(f"--- Page {page_no}: bỏ qua (parse lỗi) ---")
                continue

            for key in final_result:
                if final_result[key] is None and page_result.get(key) is not None:
                    final_result[key] = page_result[key]

            print(f"--- Page {page_no}: {page_result} ---")

        """
        Check nếu đã có hết tất cả dữ liệu cần thiết thì dừng
        """
        if all(value is not None for value in final_result.values()):
            print(f"--- Đã tìm đủ cả {len(FIELD_MAP)} field, dừng sớm ở trang {page_no} ---")
            break

    return final_result


def extract_fields_from_document(file_path: str) -> dict:
    """Chạy trọn nhánh VLM từ file gốc (dùng khi chạy standalone)."""
    return extract_fields_from_regions(load_table_regions(file_path))


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
