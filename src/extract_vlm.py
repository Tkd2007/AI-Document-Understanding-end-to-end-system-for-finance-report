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

from extraction_types import ExtractionResult, FieldResult, Provenance
from fields_config import (
    DEFAULT_STANDARD,
    FIELD_MAP,
    FIELD_RULES,
    UNIT_KEY,
    Standard,
    empty_result,
    fields_for,
    line_codes_for,
    parse_unit,
)
from metrics import bam_prompt, timer
from ocr_baseline import iter_table_regions
from validation import coerce_number, has_required_fields

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
    'triệu đồng" thì trả về đúng con số theo đơn vị đó), KHÔNG tự quy đổi. ĐỒNG THỜI đọc dòng '
    'khai báo đơn vị ở đầu bảng (thường ghi "Đơn vị tính: ...") và trả về NGUYÊN VĂN cụm đơn vị '
    'ở khoá "don_vi_tinh", ví dụ "triệu đồng". Nếu ảnh không có dòng đó, trả null cho khoá này — '
    'không được suy đoán đơn vị từ độ lớn của các con số.',

    '7. Chỉ lấy số liệu của KỲ BÁO CÁO NGẮN NHẤT VÀ MỚI NHẤT. Ưu tiên xác định cột bằng '
    'NHÃN/TIÊU ĐỀ cột theo các quy tắc 7b-7d dưới đây. Khi nhãn cột mờ hoặc thiếu thì ĐƯỢC '
    'PHÉP dùng VỊ TRÍ làm căn cứ phụ: theo mẫu biểu Việt Nam, cột số liệu ĐẦU TIÊN ngay sau '
    'các cột nhãn ("Mã số", "Chỉ tiêu", "Thuyết minh") chính là kỳ báo cáo hiện tại. Lưu ý '
    '"đầu tiên" tính theo chiều đọc CỦA BẢNG, không phải theo mép trái của ảnh — trang có thể '
    'bị xoay 90 độ, và khi đó chiều đọc cũng xoay theo.',

    '7b. Bảng kết quả kinh doanh quý thường có BỐN cột số liệu, chia làm hai nhóm: nhóm "Quý '
    '<số>" và nhóm LUỸ KẾ (nhãn ghi "Luỹ kế từ đầu năm...", "Kỳ kế toán <N> tháng...", "6 '
    'tháng", "9 tháng"). Mỗi nhóm lại có cột kỳ này và cột kỳ trước. LUÔN LẤY CỘT CỦA NHÓM QUÝ, '
    'kỳ này. TUYỆT ĐỐI KHÔNG lấy cột luỹ kế.',

    '7c. Hai nhóm cột đó THƯỜNG KẾT THÚC CÙNG MỘT NGÀY (ví dụ quý IV và luỹ kế cả năm cùng kết '
    'thúc ngày 31 tháng 12), nên KHÔNG được chọn cột bằng cách so ngày kết thúc — cách đó không '
    'phân biệt được hai nhóm. Phân biệt bằng ĐỘ DÀI KỲ: cột quý gộp khoảng 3 tháng, cột luỹ kế '
    'gộp từ đầu năm tài chính. Chọn cột có kỳ NGẮN hơn.',

    '7d. Bảng cân đối kế toán (tình hình tài chính) thì khác: nó có HAI cột, đều là số dư tại '
    'một THỜI ĐIỂM chứ không phải một kỳ (ví dụ "Ngày 31 tháng 12 năm 2025" và "Ngày 30 tháng 6 '
    'năm 2025", hoặc "Số cuối kỳ" và "Số đầu năm"). Ở bảng này lấy cột có ngày MỚI NHẤT, tức số '
    'cuối kỳ. Không có cột luỹ kế nào ở đây.',

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
# Hậu tố "a"/"b" là KỲ BÁO CÁO chứ không phải Thông tư: cả TT200 lẫn TT99
# đều dùng đủ ba ký hiệu B01-DN, B01a-DN, B01b-DN — xem chú thích ở
# FORM_MARKERS trong fields_config.py, nơi bản cũ tin nhầm điều ngược lại và
# trượt mọi trang B01a-DN. Bỏ hậu tố đi thì chỉ còn ba loại báo cáo, nên một
# bảng tên là đủ. Riêng B01 để cả hai tên vì TT99 đổi "Bảng cân đối kế toán"
# thành "Báo cáo tình hình tài chính" — nêu cả hai giúp model nhận ra trang
# dù báo cáo theo chuẩn nào.
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

    # Gom field theo mẫu biểu, giữ nguyên thứ tự khai báo trong FIELD_MAP.
    #
    # Duyệt fields_for(standard) chứ KHÔNG duyệt FIELD_MAP. FIELD_MAP là hợp
    # của cả hai chuẩn, nên với báo cáo TT200 nó kéo theo
    # tai_san_sinh_hoc_ngan_han — dòng TT200 không có. Chỉ tiêu đó rơi vào
    # "NHÓM KHÁC" (không mã số để đối chiếu) và vào cả khuôn JSON bắt buộc,
    # tức prompt đi bảo model tìm một dòng không tồn tại trên giấy. Luật 3 có
    # dặn trả null khi không thấy, nhưng mời model đi tìm cái không có là tự
    # tạo áp lực bịa ở đúng chỗ nhạy cảm nhất.
    cac_field = fields_for(standard)
    grouped: dict[str, list[str]] = {}
    ungrouped: list[str] = []

    for key in cac_field:
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

    # don_vi_tinh nối vào CUỐI template và mang kiểu chuỗi, không phải số.
    # Nó là dữ liệu meta về cách đọc cả bảng chứ không phải một chỉ tiêu,
    # nên cố ý không nằm trong FIELD_MAP — xem chú thích ở UNIT_KEY.
    o_so = ", ".join(f'"{key}": <số hoặc null>' for key in cac_field)
    json_template = f'{o_so}, "{UNIT_KEY}": <chuỗi đơn vị hoặc null>'

    return f"""Bạn là một hệ thống trích xuất dữ liệu tài chính tự động.
Nhiệm vụ: nhìn vào ảnh trang báo cáo tài chính được cung cấp, tìm và trích xuất các chỉ tiêu sau.

{field_block}

QUY TẮC BẮT BUỘC:
{rules_block}

Trả về đúng format JSON sau, không có gì khác:
{{{json_template}}}"""


def call_vlm(base64_image: str, prompt: str, temperature: float = 0.0) -> str | None:
    """
    Gọi VLM, tự thử lại khi gặp lỗi tạm thời.

    temperature phải truyền được vì self-consistency đứng trên nó: ở nhiệt
    độ 0 thì k mẫu giống hệt nhau và tỷ lệ đồng thuận luôn bằng 1, tức là
    không đo được gì.

    Model free tier trên OpenRouter dính 429 (rate limit) khá thường, và
    một báo cáo có thể 50+ trang. Trước đây một lỗi mạng ở giữa chừng là
    làm hỏng cả lượt chạy. Trả về None khi đã hết lượt thử, để nơi gọi tự
    quyết định bỏ qua trang đó — cùng triết lý với parse_response().
    """
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = get_client().chat.completions.create(
                model=MODEL,
                temperature=temperature,
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

# Tắt HOÀN TOÀN mọi điều kiện dừng sớm. CHỈ DÙNG KHI ĐO.
#
# Dừng sớm là tối ưu chi phí cho đường phục vụ, nhưng nó làm hỏng phép đo
# theo một kiểu khó thấy. Nhánh PATIENCE_PAGES dừng khi đã đủ field BẮT
# BUỘC — tức nó cố ý bỏ qua phần đuôi tài liệu. Sau B4 mở rộng bộ trường,
# một chỉ tiêu mới có thể nằm đúng ở phần đuôi đó, và khi ấy tỷ lệ "không
# đọc được" của nó sẽ là tạo tác của điều kiện dừng chứ không phải của mô
# hình. Không ai phát hiện được từ bảng kết quả, vì trường bị bỏ qua và
# trường đọc hỏng trông giống hệt nhau: cùng là một ô null.
#
# Cùng lý do với DISABLE_CONSTRAINT_GATE ở router.py — đo một hệ trên đầu
# ra mà chính hệ đó đã cắt xén thì con số thu được không nói lên điều gì.
DISABLE_EARLY_STOP = os.getenv("DISABLE_EARLY_STOP", "false").strip().lower() in {
    "1",
    "true",
    "yes",
}


def _lay_mau_vung(
    base64_image: str,
    prompt: str,
    n_samples: int,
    temperature: float,
    metrics=None,
) -> list[dict]:
    """
    Gọi VLM n_samples lần trên CÙNG một ảnh, trả về các mẫu parse được.

    Mẫu nào gọi hỏng hoặc parse hỏng thì bị bỏ khỏi danh sách, nhưng vẫn
    được đếm vào n_samples ở mẫu số của confidence — xem _bo_phieu().
    """
    cac_mau = []

    for _ in range(n_samples):
        with timer(metrics, "vlm"):
            raw_text = call_vlm(base64_image, prompt, temperature)

        if metrics is not None:
            metrics.count("vlm_calls")

        if raw_text is None:
            if metrics is not None:
                metrics.count("vlm_failures")
            continue

        da_parse = parse_response(raw_text)
        if da_parse is None:
            if metrics is not None:
                metrics.count("parse_failures")
            continue

        cac_mau.append(da_parse)

    return cac_mau


def _chuan_hoa_chuoi(gia_tri):
    """Chuẩn hoá đơn vị tính trước khi bỏ phiếu: chỉ cắt khoảng trắng."""
    if gia_tri is None:
        return None
    da_cat = str(gia_tri).strip()
    return da_cat or None


def _bo_phieu(cac_mau: list[dict], khoa: str, n_samples: int) -> tuple[FieldResult, str | None]:
    """
    Bỏ phiếu self-consistency cho một chỉ tiêu, trả về (kết quả, cảnh báo).

    Ba quyết định đáng ghi lại:

    None CŨNG LÀ MỘT ỨNG VIÊN bỏ phiếu. Model trả null ba trên năm lần là
    một tín hiệu thật — nó nói rằng chỉ tiêu này thường không đọc được trên
    ảnh đó — và biến nó thành phiếu trắng sẽ làm confidence của hai lần còn
    lại trông cao giả tạo.

    Mẫu số là n_samples chứ không phải số mẫu parse được. Một lượt gọi hỏng
    là một lượt không có bằng chứng, nên nó PHẢI kéo confidence xuống. Lấy
    số mẫu thành công làm mẫu số sẽ cho ra confidence 1.0 trên một tài liệu
    mà bốn trong năm lần gọi đều thất bại.

    Hoà phiếu thì ưu tiên giá trị non-null, rồi tới giá trị xuất hiện sớm
    nhất. Điều kiện thứ hai chỉ để KẾT QUẢ TẤT ĐỊNH — cùng đầu vào phải cho
    cùng đầu ra, nếu không thì không tái lập được thí nghiệm.
    """
    chuan_hoa = _chuan_hoa_chuoi if khoa == UNIT_KEY else coerce_number

    phieu: dict = {}
    xuat_hien_dau = {}

    for thu_tu, mau in enumerate(cac_mau):
        gia_tri = chuan_hoa(mau.get(khoa))
        phieu[gia_tri] = phieu.get(gia_tri, 0) + 1
        xuat_hien_dau.setdefault(gia_tri, thu_tu)

    if not phieu:
        return FieldResult(value=None, confidence=0.0), None

    thang = min(phieu, key=lambda g: (-phieu[g], g is None, xuat_hien_dau[g]))
    so_phieu_thang = phieu[thang]

    canh_bao = None
    hoa_voi = [
        g for g in phieu
        if g != thang and phieu[g] == so_phieu_thang and g is not None
    ]
    if hoa_voi and thang is not None:
        canh_bao = (
            f"{khoa}: hoà phiếu {so_phieu_thang} đều giữa {thang} và {hoa_voi}, "
            f"đã chọn {thang} theo thứ tự xuất hiện"
        )

    return (
        FieldResult(
            value=thang,
            confidence=so_phieu_thang / n_samples,
            votes={str(g): so for g, so in phieu.items()},
        ),
        canh_bao,
    )


# Tỷ lệ đồng thuận tối thiểu để một vùng được quyền GHI ĐÈ đơn vị đang kế
# thừa từ vùng trước.
#
# Vì sao phải có ngưỡng chứ không đè vô điều kiện: buộc đơn vị theo bảng mở
# ra một chế độ lỗi mới. Trước đây cả tài liệu chỉ có MỘT lần đọc đơn vị có
# thể sai; giờ mỗi bảng là một cơ hội sai, và một đơn vị bịa ra trên trang
# tiếp nối vốn không in dòng khai báo sẽ làm hỏng mọi chỉ tiêu của bảng đó.
# Không đẳng thức nào bắt được — hệ ràng buộc thuần nhất nên bất biến với
# phép nhân vô hướng (PREREGISTRATION mục 4.2).
#
# Để QUÁ BÁN, tính cả ca hoà phiếu với null: model đọc ra đơn vị ở một nửa
# số mẫu và không thấy gì ở nửa kia thì khả năng cao là dòng khai báo có
# thật nhưng mờ, chứ không phải model bịa. Null là "không nhìn thấy", không
# phải "đơn vị khác".
#
# Ở cấu hình đang chạy thật (n_samples=1) ngưỡng này KHÔNG có tác dụng:
# _bo_phieu() trên một mẫu luôn cho confidence 1,0. Nó chỉ bắt đầu chặn khi
# bật self-consistency, và đó là chủ ý — đừng đọc con số 0,5 như một tham số
# đã hiệu chỉnh trên dữ liệu.
NGUONG_DON_VI_VUNG = 0.5


def _he_so_vung(ket_qua_don_vi: FieldResult, he_so_truoc: int | None) -> tuple[int | None, str]:
    """
    Hệ số quy đổi áp cho MỘT vùng bảng, kèm nguồn của kết luận đó.

    Ba nguồn, và chúng phải phân biệt được nhau trong kết quả ghi ra vì
    chúng là ba mức tin cậy khác hẳn nhau:

      doc_duoc   vùng tự khai đơn vị và phiếu đủ mạnh -> dùng của chính nó
      ke_thua    vùng không khai (hoặc khai không đọc được) -> lấy của vùng trước
      chua_biet  chưa vùng nào đọc được đơn vị -> không quy đổi, không đoán

    ĐỌC ĐƯỢC THẮNG KẾ THỪA, đây là chỗ đảo ngược hành vi cũ. Bản trước đối
    xử với đơn vị như một chỉ tiêu bình thường, nên vùng ĐẦU TIÊN đọc được
    sẽ chốt cho cả tài liệu và không bao giờ được đọc lại. Trên
    `HNG_2025H1_TT200` vùng đầu tiên ấy là công văn giải trình ở trang 1
    khai `tỷ đồng`, và nó chốt trước khi bảng cân đối kịp khai `nghìn đồng`
    — 24/26 chỉ tiêu sai gấp 1e6 lần.

    KHÔNG sao chép ba ràng buộc của `ky_hieu_mau.py` sang đây dù khuôn mẫu
    trông giống hệt ("đọc ở đâu đọc được, lan sang chỗ không đọc được"). Ký
    hiệu mẫu THẬT SỰ thuần nhất trong một hồ sơ, nên ở đó "chốt một lần" là
    đúng và "vùng sau khác vùng trước" là dấu hiệu hỏng. Đơn vị tính thì
    không thuần nhất — HNG là phản ví dụ đo được — nên ở đây cùng một sự
    kiện lại là chuyện bình thường và phải được phép ghi đè.
    """
    he_so_doc, _ = parse_unit(ket_qua_don_vi.value)

    if he_so_doc is not None and ket_qua_don_vi.confidence >= NGUONG_DON_VI_VUNG:
        return he_so_doc, "doc_duoc"

    if he_so_truoc is not None:
        return he_so_truoc, "ke_thua"

    return None, "chua_biet"


def _don_vi_tai_lieu(
    he_so_theo_truong: dict[str, int], da_doc: list[tuple[int, str]]
) -> tuple[str | None, int | None]:
    """
    Kết luận đơn vị MỨC TÀI LIỆU: hệ số đã áp cho NHIỀU chỉ tiêu nhất.

    Vì sao vẫn cần một con số mức tài liệu khi hệ số đã buộc theo bảng: hai
    thứ hạ nguồn đọc nó. `validate_result()` lùi về nó cho những ô không rõ
    đọc từ bảng nào (ví dụ ô do nhánh OCR điền), và tập gold chấm điểm bằng
    `unit_multiplier` — một trường DUY NHẤT cho mỗi tài liệu, theo
    ANNOTATION-GUIDELINE mục 3.1.

    ĐA SỐ THEO SỐ CHỈ TIÊU, không phải vùng đọc được đầu tiên. Với HNG, một
    chỉ tiêu đọc từ công văn `tỷ đồng` và 25 chỉ tiêu đọc từ BCTC `nghìn
    đồng`, nên đa số trả về `nghìn đồng` — khớp gold. Lấy vùng đầu tiên sẽ
    trả về `tỷ đồng` và bảng chấm điểm báo sai đơn vị trong khi 25/26 con số
    đã quy đổi đúng, tức con số đo nói ngược lại điều đã xảy ra.

    Hoà thì lấy hệ số ĐỌC ĐƯỢC SỚM NHẤT. Điều kiện này không mang ý nghĩa
    nghiệp vụ, nó chỉ để kết quả TẤT ĐỊNH: cùng đầu vào phải cho cùng đầu
    ra, nếu không thì lượt chạy không tái lập được.

    `da_doc` là các cặp (hệ số, chuỗi gốc) theo đúng thứ tự đọc được trên
    tài liệu. Trả `(None, None)` khi chưa vùng nào đọc được — tuyệt đối
    không lùi về "đồng", đúng nguyên tắc của `parse_unit()`.
    """
    thu_tu: dict[int, int] = {}
    raw_cua: dict[int, str] = {}
    for i, (he_so, raw) in enumerate(da_doc):
        thu_tu.setdefault(he_so, i)
        raw_cua.setdefault(he_so, raw)

    if not he_so_theo_truong:
        return (da_doc[0][1], da_doc[0][0]) if da_doc else (None, None)

    dem: dict[int, int] = {}
    for he_so in he_so_theo_truong.values():
        dem[he_so] = dem.get(he_so, 0) + 1

    thang = min(dem, key=lambda h: (-dem[h], thu_tu.get(h, len(da_doc))))
    return raw_cua.get(thang), thang


def _luu_crop(region, page_no: int, region_index: int, crop_dir) -> str | None:
    """
    Ghi ảnh crop ra đĩa để bước đọc lại dùng lại, trả về đường dẫn.

    Tên file mang (trang, chỉ số vùng) chứ KHÔNG mang số ngẫu nhiên: crop
    này tồn tại để tra cứu lại bằng tay khi đi dò một kết quả đáng ngờ, mà
    tên ngẫu nhiên thì không tra được. document_id nằm ở chính tên thư mục
    crop_dir do người gọi đặt.

    Trả None khi không bật lưu crop — bbox trong Provenance vẫn đủ để cắt
    lại từ PDF gốc, chỉ tốn công convert lại trang.
    """
    if crop_dir is None:
        return None

    thu_muc = Path(crop_dir)
    thu_muc.mkdir(parents=True, exist_ok=True)

    duong_dan = thu_muc / f"p{page_no:03d}_r{region_index}.png"
    region.image.save(duong_dan)

    return str(duong_dan)


def extract_fields_from_regions(
    pages,
    metrics=None,
    standard: Standard = DEFAULT_STANDARD,
    n_samples: int = 1,
    temperature: float = 0.0,
    crop_dir: str | Path | None = None,
) -> ExtractionResult:
    """
    Chạy VLM trên từng vùng bảng đã cắt sẵn, gộp thành một ExtractionResult.

    Với mỗi field, lấy giá trị non-null ĐẦU TIÊN tìm thấy qua các trang
    (field nào trang trước không có, trang sau tìm tiếp; đã có rồi thì
    không ghi đè). Các chỉ tiêu nằm rải ở nhiều trang khác nhau: nhóm B01a
    ở trang bảng cân đối, nhóm B02a ở trang kết quả kinh doanh.

    ĐƠN VỊ TÍNH THÌ NGƯỢC LẠI — đọc lại ở MỌI vùng, và vùng nào tự khai được
    thì đơn vị của nó thắng đơn vị đang kế thừa. Vùng không khai mới lấy của
    vùng trước. Xem `_he_so_vung()` cho lý do và cho ca HNG đã đo được.
    Kết quả đi ra ở meta dưới ba khoá: `don_vi_tinh` (kết luận mức tài liệu,
    theo đa số chỉ tiêu), `he_so_don_vi_theo_truong` (hệ số của từng ô, để
    `validate_result()` quy đổi), và `don_vi_theo_vung` (bản khai từng vùng).

    n_samples > 1 bật self-consistency: gọi VLM nhiều lần trên cùng một ảnh
    ở nhiệt độ lớn hơn 0 rồi lấy tỷ lệ đồng thuận làm confidence. Một thay
    đổi cho ba thứ — confidence cho H1, baseline VLM cộng self-consistency
    voting, và tập ứng viên sửa lỗi từ chính các giá trị thua phiếu.

    n_samples = 1 và temperature = 0 cho hành vi Y HỆT bản trước, với
    confidence 1.0 ở mọi field có giá trị. Con số 1.0 đó KHÔNG có nghĩa là
    chắc chắn, nó có nghĩa là không đo được — xem FieldResult.khong_do().

    Điều kiện dừng sớm gồm hai nhánh, vì mục tiêu là lấy ĐỦ field nhưng
    không quét vô ích tới hết tài liệu:
      1. Đủ cả field trong FIELD_MAP -> chắc chắn không còn gì để tìm.
         Kiểm sau mỗi VÙNG, không đợi hết trang.
      2. Đủ field BẮT BUỘC và đã PATIENCE_PAGES trang liên tiếp không có
         thêm field mới -> gần như chắc chắn đã qua hết phần bảng biểu.
         Kiểm ở cuối mỗi trang, vì bộ đếm kiên nhẫn đếm theo trang.
    Nếu chỉ dùng nhánh 1, chỉ cần một field không bao giờ đọc được là phải
    gọi API cho cả 55 trang.

    Cả hai nhánh tắt được bằng DISABLE_EARLY_STOP=true, và dù bật hay tắt
    thì `meta["early_stop"]` luôn ghi lại đã dừng hay chưa, vì lý do gì, ở
    trang nào, và những field nào còn thiếu lúc đó. Nhánh 2 mới là nhánh
    đáng ngờ khi ĐO: nó dừng lúc chưa đủ field, nên field còn thiếu có thể
    chưa từng được nhìn tới chứ không phải model đọc hỏng.
    """
    if n_samples > 1 and temperature == 0:
        raise ValueError(
            f"n_samples={n_samples} với temperature=0 là vô nghĩa: mọi mẫu sẽ giống "
            f"hệt nhau nên tỷ lệ đồng thuận luôn bằng 1. Đặt temperature > 0, hoặc "
            f"để n_samples=1 nếu chưa cần đo confidence."
        )

    # Prompt dựng MỘT lần cho cả tài liệu, nên chuẩn mẫu biểu phải do người
    # gọi truyền vào chứ không tự dò theo từng trang: nhánh VLM không có
    # text OCR để dò, và một tài liệu thì chỉ theo đúng một chuẩn.
    prompt = build_prompt(standard)

    # Bộ chỉ tiêu của ĐÚNG chuẩn này — thứ mà điều kiện dừng sớm nhánh 1
    # đếm trên. Lấy một lần ở đây thay vì gọi lại trong vòng lặp vì nó cố
    # định suốt cả tài liệu: một tài liệu chỉ theo đúng một chuẩn.
    cac_field_can = fields_for(standard)

    # UNIT_KEY KHÔNG nằm trong khung tích luỹ này nữa, dù empty_result() vẫn
    # trả nó về. Khung này giữ những thứ "tìm thấy một lần rồi thôi", còn đơn
    # vị tính bây giờ được đọc lại ở MỌI vùng — để nó chung khung thì đúng
    # dòng `continue` bên dưới sẽ chốt nó ở vùng đầu tiên, tức dựng lại
    # nguyên xi lỗi mà cả thay đổi này sinh ra để sửa.
    final_result: dict[str, FieldResult] = {
        khoa: FieldResult(value=None, confidence=0.0)
        for khoa in empty_result(standard)
        if khoa != UNIT_KEY
    }
    warnings: list[str] = []
    pages_without_new_field = 0

    # Đơn vị tính buộc theo BẢNG. Ba biến, ba vai trò khác nhau:
    #
    #   he_so_hien_hanh    đơn vị của vùng gần nhất đọc được, để vùng sau kế thừa
    #   he_so_theo_truong  {chỉ tiêu -> hệ số của vùng đã sinh ra nó}, đi thẳng
    #                      xuống validate_result()
    #   don_vi_theo_vung   bản khai từng vùng: đọc ra gì, tin bao nhiêu, cuối
    #                      cùng áp hệ số nào, vì lý do gì
    #
    # Cái thứ ba là certificate của cơ chế này. Bài học đắt của lượt chạy
    # 30/08 (HANDOFF mục 20.7): bật một cơ chế mới mà không lưu certificate
    # của nó thì cho ra số không quy được về nguyên nhân, và cái giá là chạy
    # lại cả tập.
    he_so_hien_hanh: int | None = None
    he_so_theo_truong: dict[str, int] = {}
    don_vi_theo_vung: list[dict] = []
    da_doc_don_vi: list[tuple[int, str]] = []

    # Trạng thái dừng sớm là khoá TƯỜNG MINH trong meta, không để người đọc
    # suy ra từ số trang đã quét. Lý do: một chỉ tiêu bị bỏ qua vì dừng sớm
    # và một chỉ tiêu đọc hỏng cho ra cùng một thứ — ô null — nên nếu không
    # ghi lại thì bảng kết quả không phân biệt được hai chuyện hoàn toàn
    # khác nhau về bản chất.
    dung_som = {
        "da_dung_som": False,
        "ly_do": "",
        "trang_cuoi": None,
        "field_con_thieu": [],
    }
    da_du_het = False

    for page in pages:
        page_no = page["page"]
        found_new_field = False

        for region_index, region in enumerate(page["regions"]):
            base64_image = encode_image_to_base64(region.image)
            cac_mau = _lay_mau_vung(base64_image, prompt, n_samples, temperature, metrics)

            if not cac_mau:
                print(f"--- Page {page_no}: bỏ qua (không mẫu nào dùng được) ---")
                continue

            nguon = Provenance(
                page=page_no,
                region_index=region_index,
                bbox=region.bbox,
                crop_path=_luu_crop(region, page_no, region_index, crop_dir),
            )

            # Đơn vị của vùng, quyết TRƯỚC mọi chỉ tiêu: mọi con số đọc ra từ
            # vùng này đều được đóng dấu hệ số ấy ngay lúc lấy.
            #
            # Bước bỏ phiếu này KHÔNG mua thêm một lời gọi VLM nào. Prompt đã
            # bắt model trả don_vi_tinh cho mọi vùng (mục 6 trong build_prompt),
            # nên chuỗi đơn vị của từng bảng vốn đã nằm sẵn trong cac_mau —
            # bản trước chỉ đơn giản là vứt nó đi từ vùng thứ hai trở đi.
            ket_qua_don_vi, canh_bao_don_vi = _bo_phieu(cac_mau, UNIT_KEY, n_samples)
            he_so_vung, nguon_don_vi = _he_so_vung(ket_qua_don_vi, he_so_hien_hanh)
            if nguon_don_vi == "doc_duoc":
                he_so_hien_hanh = he_so_vung
                da_doc_don_vi.append((he_so_vung, ket_qua_don_vi.value))
                if canh_bao_don_vi:
                    warnings.append(f"Trang {page_no}: {canh_bao_don_vi}")

            don_vi_theo_vung.append({
                "trang": page_no,
                "vung": region_index,
                # Chuỗi ĐỌC ĐƯỢC tại vùng này, tách khỏi hệ số CUỐI CÙNG áp cho
                # nó. Một vùng đọc ra "tỷ đồng" nhưng bị ngưỡng chặn rồi kế thừa
                # "nghìn đồng" là một sự kiện đáng biết, và gộp hai khoá lại thì
                # nó biến mất.
                "raw": ket_qua_don_vi.value,
                "confidence": ket_qua_don_vi.confidence,
                "he_so": he_so_vung,
                "nguon": nguon_don_vi,
            })

            for khoa in final_result:
                if final_result[khoa].value is not None:
                    continue

                ket_qua, canh_bao = _bo_phieu(cac_mau, khoa, n_samples)

                if ket_qua.value is None:
                    # "Model nhất quán trả null" là một tín hiệu THẬT cho
                    # H1 — nó nói chỉ tiêu này không đọc được trên ảnh —
                    # nên vẫn ghi lại confidence của verdict đó. Nhưng
                    # KHÔNG tính là đã tìm thấy field, để trang sau còn
                    # được thử: các chỉ tiêu nằm rải ở nhiều trang.
                    if ket_qua.confidence > final_result[khoa].confidence:
                        ket_qua.provenance = nguon
                        final_result[khoa] = ket_qua
                    continue

                ket_qua.provenance = nguon
                final_result[khoa] = ket_qua
                found_new_field = True
                # Đóng dấu hệ số của ĐÚNG vùng vừa sinh ra con số này. Ghi ngay
                # tại chỗ gán chứ không tra ngược từ provenance về sau: tra
                # ngược thì phải giữ thêm một bảng vùng->hệ số và giữ cho nó
                # đồng bộ, mà hai nguồn sự thật cho cùng một dữ kiện là cách
                # chắc chắn nhất để chúng lệch nhau mà không ai thấy.
                if he_so_vung is not None:
                    he_so_theo_truong[khoa] = he_so_vung
                if canh_bao:
                    warnings.append(f"Trang {page_no}: {canh_bao}")

            print(f"--- Page {page_no}: {cac_mau[0]} ---")

            # 1. Đủ hết -> không còn gì để tìm. Kiểm ngay sau MỖI VÙNG chứ
            #    không đợi hết trang: một trang thường có vài vùng bảng, và
            #    nếu vùng đầu đã lấp nốt field cuối cùng thì các vùng còn
            #    lại là những lời gọi VLM mua về đúng thứ đã có.
            #
            #    Điều kiện tính trên fields_for(standard) chứ không trên cả
            #    final_result: đơn vị tính chỉ in ở header bảng nên có trang
            #    không có nó, và để nó chặn early-stop thì gặp báo cáo thiếu
            #    dòng khai báo là quét tới hết tài liệu.
            #
            #    Và KHÔNG tính trên FIELD_MAP: FIELD_MAP là hợp của cả hai
            #    chuẩn, nên với báo cáo TT200 thì tai_san_sinh_hoc_ngan_han
            #    không bao giờ điền được và nhánh dừng sớm này thành BẤT KHẢ
            #    THI. Mọi lượt chạy khi đó phải rơi xuống nhánh 2 — nhánh
            #    dừng khi CHƯA đủ field, tức nhánh nguy hiểm cho phép đo.
            if not DISABLE_EARLY_STOP and all(
                final_result[khoa].value is not None for khoa in cac_field_can
            ):
                print(
                    f"--- Đã tìm đủ cả {len(cac_field_can)} field, dừng ở trang "
                    f"{page_no} vùng {region_index} ---"
                )
                dung_som = {
                    "da_dung_som": True,
                    "ly_do": "du_het_field",
                    "trang_cuoi": page_no,
                    "field_con_thieu": [],
                }
                da_du_het = True
                break

        if da_du_het:
            break

        # 2. Đủ field bắt buộc và đã hết bảng để đọc
        pages_without_new_field = 0 if found_new_field else pages_without_new_field + 1

        gia_tri_hien_co = {khoa: kq.value for khoa, kq in final_result.items()}
        if (
            not DISABLE_EARLY_STOP
            and has_required_fields(gia_tri_hien_co)
            and pages_without_new_field >= PATIENCE_PAGES
        ):
            missing = [khoa for khoa, kq in final_result.items() if kq.value is None]
            print(
                f"--- Đủ field bắt buộc, {PATIENCE_PAGES} trang liên tiếp không có "
                f"field mới -> dừng ở trang {page_no}. Không tìm được: {missing} ---"
            )
            # Đây là nhánh nguy hiểm cho phép đo: nó dừng khi CHƯA đủ field,
            # chỉ đủ field bắt buộc. Những field trong field_con_thieu có
            # thể nằm ở phần đuôi chưa hề được quét, nên đừng đếm chúng vào
            # tỷ lệ "model không đọc được" mà không tách ra trước.
            dung_som = {
                "da_dung_som": True,
                "ly_do": "het_bang_de_doc",
                "trang_cuoi": page_no,
                "field_con_thieu": missing,
            }
            break

    # Đơn vị tính đi ra ở tầng meta chứ không nằm chung với các chỉ tiêu:
    # nó là dữ liệu về CÁCH ĐỌC cả bảng, và mọi hàm hạ nguồn đều giả định
    # data chỉ chứa số.
    don_vi_raw, _ = _don_vi_tai_lieu(he_so_theo_truong, da_doc_don_vi)

    return ExtractionResult(
        data=final_result,
        meta={
            UNIT_KEY: don_vi_raw,
            # Hệ số theo từng chỉ tiêu và bản khai từng vùng. Cả hai LUÔN có
            # mặt: một lượt chạy không đọc được đơn vị ở đâu cả và một lượt
            # chưa hề chạy cơ chế này phải phân biệt được nhau, mà nếu để khoá
            # vắng mặt thì người đọc phải suy — và suy thì sai.
            "he_so_don_vi_theo_truong": he_so_theo_truong,
            "don_vi_theo_vung": don_vi_theo_vung,
            "standard": standard.value,
            # Băm NỘI DUNG prompt chứ không phải số phiên bản: số phiên
            # bản đòi con người nhớ tăng nó, và người ta không nhớ.
            "prompt_hash": bam_prompt(prompt),
            "early_stop": dung_som,
        },
        warnings=warnings,
        n_samples=n_samples,
        temperature=temperature,
        model=MODEL,
    )


def extract_fields_from_document(
    file_path: str,
    n_samples: int = 1,
    temperature: float = 0.0,
) -> ExtractionResult:
    """Chạy trọn nhánh VLM từ file gốc (dùng khi chạy standalone)."""
    return extract_fields_from_regions(
        iter_table_regions(file_path),
        n_samples=n_samples,
        temperature=temperature,
    )


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python extract_vlm.py <file_path>")
        sys.exit(1)

    # Console Windows mặc định cp1252 nên in tiếng Việt sẽ nổ.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    input_path = sys.argv[1]
    result = extract_fields_from_document(input_path)

    out_path = Path("data/output") / (Path(input_path).stem + "_vlm.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # Ghi cả confidence và votes chứ không chỉ giá trị: chạy standalone là
    # cách rẻ nhất để soi một tài liệu, và votes chính là tập ứng viên sửa
    # lỗi — gọi lại VLM để có lại nó thì tốn đúng số tiền vừa tiêu.
    ghi_ra = {
        "data": {
            ten: {"value": kq.value, "confidence": kq.confidence, "votes": kq.votes}
            for ten, kq in result.data.items()
        },
        "meta": result.meta,
        "warnings": result.warnings,
        "n_samples": result.n_samples,
        "temperature": result.temperature,
        "model": result.model,
    }

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(ghi_ra, f, ensure_ascii=False, indent=2)

    print(result.values())
    print(f"\nKết quả đã lưu tại: {out_path}")
