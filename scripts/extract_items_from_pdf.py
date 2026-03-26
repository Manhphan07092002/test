#!/usr/bin/env python3
import json
import re
import sys
from pathlib import Path

try:
    from pypdf import PdfReader
except Exception:
    PdfReader = None

IGNORE_ROW_PATTERNS = [
    "cộng tiền hàng", "vat", "tổng cộng", "bằng chữ", "điều khoản", "hiệu lực báo giá", "thanh toán", "giao hàng", "bảo hành", "kính gửi", "trân trọng"
]


def normalize_text(value):
    if value is None:
        return ""
    return re.sub(r"\s+", " ", str(value).strip())


def parse_number(value):
    text = normalize_text(value)
    if not text:
        return None
    text = text.replace("%", "")
    text = re.sub(r"[\s,.]", "", text)
    if not text:
        return None
    try:
        num = float(text)
    except ValueError:
        return None
    return int(num) if num.is_integer() else num


def is_ignored(line):
    lowered = normalize_text(line).lower()
    return any(p in lowered for p in IGNORE_ROW_PATTERNS)


def parse_line_to_item(line):
    if is_ignored(line):
        return None
    if "|" in line:
        parts = [normalize_text(x) for x in line.split("|")]
        if len(parts) >= 5:
            qty = parse_number(parts[-2])
            cost = parse_number(parts[-1])
            if qty is not None and cost is not None:
                return {
                    "description": parts[0],
                    "origin": parts[1],
                    "unit": parts[2],
                    "quantity": qty,
                    "costPrice": cost,
                }
    m = re.match(r"^(?:\d+[.)-]?\s+)?(.+?)\s+([A-Za-zÀ-ỹ]+)?\s+([A-Za-zÀ-ỹ]+)?\s+(\d+)\s+([\d., ]+)$", line)
    if m:
        description = normalize_text(m.group(1))
        maybe_origin = normalize_text(m.group(2) or "")
        maybe_unit = normalize_text(m.group(3) or "")
        qty = parse_number(m.group(4))
        cost = parse_number(m.group(5))
        if description and qty is not None and cost is not None:
            return {
                "description": description,
                "origin": maybe_origin,
                "unit": maybe_unit,
                "quantity": qty,
                "costPrice": cost,
            }
    return None


def extract_pdf(path):
    if PdfReader is None:
        return {"items": [], "warnings": ["Thiếu thư viện pypdf nên chưa đọc được file PDF."]}
    reader = PdfReader(str(path))
    items = []
    warnings = []
    lines = []
    for page in reader.pages:
        text = page.extract_text() or ""
        for raw in text.splitlines():
            line = normalize_text(raw)
            if line:
                lines.append(line)
    for line in lines:
        item = parse_line_to_item(line)
        if item:
            items.append(item)
    if not items:
        warnings.append("Không trích xuất được item rõ ràng từ file PDF.")
    return {"items": items, "warnings": warnings}


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 scripts/extract_items_from_pdf.py '<path-to-pdf>'", file=sys.stderr)
        sys.exit(2)
    path = Path(sys.argv[1]).expanduser().resolve()
    if not path.exists():
        print(f"File không tồn tại: {path}", file=sys.stderr)
        sys.exit(1)
    result = extract_pdf(path)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
