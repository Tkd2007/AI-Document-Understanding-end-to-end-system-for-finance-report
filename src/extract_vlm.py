"""
Pipeline step 2 (VLM branch): Document -> Structured JSON via VLM

Sends page images directly to a Vision-Language Model, skipping
the OCR text step entirely.
"""

import base64
import json
import os
import sys
import time
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

from fields_config import (
    DEFAULT_STANDARD,
    FIELD_MAP,
    FIELD_RULES,
    Standard,
    line_codes_for,
)
from metrics import timer
from ocr_baseline import iter_table_regions
from validation import has_required_fields

load_dotenv()

API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL = os.getenv("OPENROUTER_MODEL")

_client = None


def require_config() -> None:
    """
    Báo thiếu config trước khi tốn công convert PDF và chạy YOLO.

    Gọi ở ĐẦU pipeline (`router.route_document`) và lúc khởi động service
    (`api.py`), chứ KHÔNG phải lúc import module này. Check ở mức import
    thì mọi thứ import gián tiếp tới đây đều chết theo: `import router`
    chỉ để test hàm `is_acceptable()` — logic thuần, không chạm mạng —
    cũng đòi phải có API key, nên phần đó không sao viết test được.

    Fail-fast vẫn giữ nguyên: chỗ kiểm tra chỉ lùi từ "lúc import" xuống
    "lúc bắt đầu một lượt chạy thật", vẫn trước mọi việc nặng.
    """
    missing = [
        name
        for name, value in (("OPENROUTER_API_KEY", API_KEY), ("OPENROUTER_MODEL", MODEL))
        if not value
    ]
    if missing:
        raise RuntimeError(
            f"Thiếu biến môi trường bắt buộc trong .env: {', '.join(missing)}. "
            f"Xem phần Setup trong README."
        )


def get_client() -> OpenAI:
    """
    Tạo client ở lần gọi đầu, rồi dùng lại.

    OpenAI(api_key=None) tự ném lỗi lúc khởi tạo, nên client cũng không
    dựng được ở mức module nếu muốn import mà không cần key.
    """
    global _client
    if _client is None:
        require_config()
        _client = OpenAI(
            api_key=API_KEY,
            base_url="https://openrouter.ai/api/v1",
        )
    return _client

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


# Các quy tắc trong prompt. Mỗi phần tử là ĐÚNG MỘT dòng của prompt cuối
# cùng — được ghép lại từ nhiều literal bằng phép nối chuỗi ngầm của
# Python, nên dòng code vừa 100 cột mà chuỗi gửi đi không đổi một ký tự.
#
# Tách khỏi f-string trong build_prompt() chính vì lý do đó: gói cho vừa
# bề rộng ngay trong khối """...""" sẽ chèn xuống dòng THẬT vào prompt,
# khiến model đọc một quy tắc thành hai mẩu rời.
PROMPT_RULES = [
    '1. Chỉ trả về đúng 1 object JSON chứa ĐẦY ĐỦ mọi khoá liệt kê ở trên, KHÔNG thêm bất kỳ '
    'lời giải thích, lời chào, hay markdown (không dùng dấu ```) nào trước/sau JSON.',

    '2. Mỗi trang thường chỉ thuộc MỘT mẫu biểu, nên bình thường chỉ một nhóm chỉ tiêu ở trên '
    'xuất hiện được trên ảnh này. Các chỉ tiêu thuộc nhóm khác PHẢI trả null — đó là kết quả '
    'đúng, không phải thiếu sót.',

    '3. Nếu ảnh KHÔNG chứa một chỉ tiêu nào đó, trả null cho chỉ tiêu đó — TUYỆT ĐỐI KHÔNG được '
    'đoán hay bịa ra một con số gần đúng. Trả null luôn tốt hơn trả số sai.',

    '4. Số trả về phải là số nguyên thuần (integer), KHÔNG chứa dấu chấm, dấu phẩy hay ký hiệu '
    'đơn vị tiền tệ.',

    '5. Nếu số liệu trong ảnh là số âm (thể hiện bằng dấu "-" hoặc đặt trong ngoặc đơn, ví dụ '
    '"(1.234.567)"), PHẢI giữ lại dấu âm trong JSON (ví dụ -1234567). Rất thường gặp với '
    '"Lợi nhuận sau thuế" khi doanh nghiệp thua lỗ.',

    '6. Giữ nguyên đơn vị tính như số liệu hiển thị trong ảnh (ví dụ nếu bảng ghi "Đơn vị tính: '
    'triệu đồng" thì trả về đúng con số theo đơn vị đó), KHÔNG tự quy đổi.',

    '7. Chỉ lấy số liệu của kỳ báo cáo gần nhất. Xác định cột này dựa vào NHÃN/TIÊU ĐỀ cột '
    '(ngày, quý, năm — kỳ có ngày gần hiện tại nhất), KHÔNG mặc định dựa vào vị trí cột đầu '
    'tiên bên trái, vì thứ tự cột có thể khác nhau giữa các mẫu báo cáo. Không lấy số liệu của '
    'kỳ so sánh.',

    '8. Bảng BCTC Việt Nam có cột "Mã số" (số nhỏ 2-3 chữ số như 10, 60, 280) và cột '
    '"Thuyết minh" (ký hiệu như V.5, VI.1) nằm giữa tên chỉ tiêu và giá trị. TUYỆT ĐỐI KHÔNG '
    'lấy nhầm mã số hay số thuyết minh làm giá trị — giá trị là con số tiền tệ lớn, có dấu '
    'phân cách nghìn, nằm ở các cột bên phải.',

    '9. Tên chỉ tiêu trong ảnh có thể kèm số thứ tự/tiền tố ("A.", "I.", "1."), viết hoa toàn '
    'bộ, hoặc diễn đạt hơi khác danh sách trên — nhận diện theo Ý NGHĨA của dòng và mã số đi '
    'kèm, không đòi khớp từng ký tự.',
]


# Tên tiếng Việt của mẫu biểu, tra theo ký hiệu ĐÃ BỎ hậu tố "a".
#
# TT200 ký hiệu mẫu là B01/B02/B03, TT99 là B01a/B02a/B03a, nhưng vẫn là
# cùng ba loại báo cáo nên không cần hai bảng tên. Riêng B01 để cả hai tên
# vì TT99 đổi "Bảng cân đối kế toán" thành "Báo cáo tình hình tài chính" —
# nêu cả hai giúp model nhận ra trang dù báo cáo theo chuẩn nào.
FORM_NAMES = {
    "B01": "Báo cáo tình hình tài chính (bảng cân đối kế toán)",
    "B02": "Báo cáo kết quả hoạt động kinh doanh",
    "B03": "Báo cáo lưu chuyển tiền tệ",
}


def build_prompt(standard: Standard = DEFAULT_STANDARD) -> str:
    """
    Sinh prompt từ fields_config, nhóm theo mẫu biểu.

    Khi danh sách chỉ tiêu còn 3 field thì liệt kê phẳng là đủ. Với 11
    field trải trên hai mẫu biểu khác nhau thì không: mỗi trang ảnh chỉ
    thuộc MỘT mẫu, nên nếu prompt trộn lẫn, model dễ cố tìm cho bằng được
    chỉ tiêu của bảng cân đối trên trang kết quả kinh doanh — rồi bịa ra
    một con số gần đúng. Nhóm theo mẫu và nói rõ "trang này thường chỉ
    chứa một nhóm" giúp model tự tin trả null cho nhóm còn lại.

    Kèm luôn mã số dòng: bảng BCTC Việt Nam in mã ngay cạnh tên chỉ tiêu,
    và mã là thứ ổn định nhất trên trang — hữu ích cho model đối chiếu
    khi tên chỉ tiêu trong ảnh viết hơi khác so với danh sách.
    """
    line_codes = line_codes_for(standard)

    # Gom field theo mẫu biểu, giữ nguyên thứ tự khai báo trong FIELD_MAP
    grouped: dict[str, list[str]] = {}
    ungrouped: list[str] = []

    for key in FIELD_MAP:
        entry = line_codes.get(key)
        if entry is None:
            ungrouped.append(key)
            continue
        form, _ = entry
        grouped.setdefault(form, []).append(key)

    sections = []
    for form, keys in grouped.items():
        lines = [f"NHÓM {form} — {FORM_NAMES.get(form.rstrip('a'), form)}:"]
        for key in keys:
            _, code = line_codes[key]
            required = " [BẮT BUỘC]" if FIELD_RULES.get(key, {}).get("required") else ""
            lines.append(f'- "{key}": dòng "{FIELD_MAP[key]}", mã số {code}{required}')
        sections.append("\n".join(lines))

    if ungrouped:
        lines = ["NHÓM KHÁC:"]
        for key in ungrouped:
            lines.append(f'- "{key}": dòng "{FIELD_MAP[key]}"')
        sections.append("\n".join(lines))

    field_block = "\n\n".join(sections)
    rules_block = "\n".join(PROMPT_RULES)
    json_template = ", ".join(f'"{key}": <số hoặc null>' for key in FIELD_MAP)

    return f"""Bạn là một hệ thống trích xuất dữ liệu tài chính tự động.
Nhiệm vụ: nhìn vào ảnh trang báo cáo tài chính được cung cấp, tìm và trích xuất các chỉ tiêu sau.

{field_block}

QUY TẮC BẮT BUỘC:
{rules_block}

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
            response = get_client().chat.completions.create(
                model=MODEL,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{base64_image}"
                                },
                            },
                        ]
                    }
                ]
            )
            if not response.choices:
                # OpenRouter trả HTTP 200 nhưng body là object lỗi (hết
                # quota, model tạm không khả dụng, request bị từ chối) —
                # không có exception nào để except bắt, nên phải tự kiểm
                # tra. Không có dòng này thì cả request sập, đúng thứ mà
                # retry logic sinh ra để ngăn.
                error = RuntimeError(f"VLM không trả về choices: {response}")
            else:
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
        print(
            f"[WARNING] Lỗi gọi VLM (lần {attempt}/{MAX_RETRIES}): {error} "
            f"— thử lại sau {delay:.0f}s"
        )
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


# Số trang liên tiếp không tìm thêm được field mới thì coi như đã đi hết
# phần bảng biểu. Các mẫu B01a/B02a/B03a luôn nằm liền nhau ở đầu báo cáo
# (trang 6-12 với báo cáo VNM), phần còn lại là thuyết minh — quét tiếp
# chỉ tốn tiền gọi API. Để 3 cho rộng rãi: giữa các bảng có thể chen vài
# trang chữ ký, trang trắng, hoặc trang mà YOLO cắt nhầm.
PATIENCE_PAGES = 3


def extract_fields_from_regions(
    pages,
    metrics=None,
    standard: Standard = DEFAULT_STANDARD,
) -> dict:
    """
    Chạy VLM trên từng vùng bảng đã cắt sẵn, gộp kết quả lại thành 1 dict.

    Với mỗi field, lấy giá trị non-null ĐẦU TIÊN tìm thấy qua các trang
    (field nào trang trước không có, trang sau tìm tiếp; đã có rồi thì
    không ghi đè). Các chỉ tiêu nằm rải ở nhiều trang khác nhau: nhóm
    B01a ở trang bảng cân đối, nhóm B02a ở trang kết quả kinh doanh.

    Điều kiện dừng sớm gồm hai nhánh, vì mục tiêu là lấy ĐỦ field nhưng
    không quét vô ích tới hết tài liệu:
      1. Đủ cả 11 field  -> chắc chắn không còn gì để tìm, dừng ngay.
      2. Đủ field BẮT BUỘC và đã PATIENCE_PAGES trang liên tiếp không có
         thêm field mới -> gần như chắc chắn đã qua hết phần bảng biểu.
    Nếu chỉ dùng nhánh 1, chỉ cần một field không bao giờ đọc được là
    phải gọi API cho cả 55 trang.
    """
    # Prompt dựng MỘT lần cho cả tài liệu, nên chuẩn mẫu biểu phải do người
    # gọi truyền vào chứ không tự dò theo từng trang: nhánh VLM không có
    # text OCR để dò, và một tài liệu thì chỉ theo đúng một chuẩn.
    prompt = build_prompt(standard)
    final_result = {key: None for key in FIELD_MAP}
    pages_without_new_field = 0

    for page in pages:
        page_no = page["page"]
        found_new_field = False

        for region in page["regions"]:
            base64_image = encode_image_to_base64(region)

            with timer(metrics, "vlm"):
                raw_text = call_vlm(base64_image, prompt)

            if metrics is not None:
                metrics.count("vlm_calls")

            if raw_text is None:
                print(f"--- Page {page_no}: bỏ qua (gọi VLM thất bại) ---")
                if metrics is not None:
                    metrics.count("vlm_failures")
                continue

            page_result = parse_response(raw_text)
            if page_result is None:
                print(f"--- Page {page_no}: bỏ qua (parse lỗi) ---")
                if metrics is not None:
                    metrics.count("parse_failures")
                continue

            for key in final_result:
                if final_result[key] is None and page_result.get(key) is not None:
                    final_result[key] = page_result[key]
                    found_new_field = True

            print(f"--- Page {page_no}: {page_result} ---")

        # 1. Đủ hết -> không còn gì để tìm
        if all(value is not None for value in final_result.values()):
            print(f"--- Đã tìm đủ cả {len(FIELD_MAP)} field, dừng ở trang {page_no} ---")
            break

        # 2. Đủ field bắt buộc và đã hết bảng để đọc
        pages_without_new_field = 0 if found_new_field else pages_without_new_field + 1

        if has_required_fields(final_result) and pages_without_new_field >= PATIENCE_PAGES:
            missing = [key for key, value in final_result.items() if value is None]
            print(
                f"--- Đủ field bắt buộc, {PATIENCE_PAGES} trang liên tiếp không có "
                f"field mới -> dừng ở trang {page_no}. Không tìm được: {missing} ---"
            )
            break

    return final_result


def extract_fields_from_document(file_path: str) -> dict:
    """Chạy trọn nhánh VLM từ file gốc (dùng khi chạy standalone)."""
    return extract_fields_from_regions(iter_table_regions(file_path))


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
