"""
Pipeline step 2: Raw Text -> Structured JSON (Extraction baseline)

Rule-based / regex extraction of key financial line items from
OCR raw text. This is the baseline to compare against a VLM-based
approach later.
"""

import sys
import re
import json
from pathlib import Path

from fields_config import FIELD_MAP


def load_raw_text(file_path: str) -> str:

    with open(file_path, encoding="utf-8") as f:
        text = f.read()
    return text


def extract_field(text: str, field_name: str) -> int | None:
    match = re.search(fr"{field_name}\s+([\d.]+)", text)

    if match:
        raw_number = match.group(1)
        clean_number = raw_number.replace(".", "")
        number = int(clean_number)

        return number
    return None


def extract_all_fields(text: str) -> dict:
    result = dict()

    for key, field_name in FIELD_MAP.items():
        number = extract_field(text, field_name)
        result[key] = number

    return result


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python extract_baseline.py <file_path>")
        sys.exit(1)

    input_path = sys.argv[1]
    text = load_raw_text(input_path)
    result = extract_all_fields(text)

    out_path = Path("data/output")/(Path(input_path).stem + "_extracted.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(result)