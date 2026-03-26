#!/usr/bin/env python3
import json
import re
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
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


def is_ignored(text):
    lowered = normalize_text(text).lower()
    return any(p in lowered for p in IGNORE_ROW_PATTERNS)


def parse_table_row(cells):
    cells = [normalize_text(c) for c in cells]
    if len(cells) < 4:
        return None
    if is_ignored(" ".join(cells)):
        return None
    if len(cells) >= 5:
        qty = parse_number(cells[-2])
        cost = parse_number(cells[-1])
        if qty is not None and cost is not None:
            return {
                "description": cells[0],
                "origin": cells[1] if len(cells) >= 5 else "",
                "unit": cells[2] if len(cells) >= 5 else "",
                "quantity": qty,
                "costPrice": cost,
            }
    return None


def extract_docx(path):
    with zipfile.ZipFile(path) as zf:
        xml_bytes = zf.read("word/document.xml")
    root = ET.fromstring(xml_bytes)
    items = []
    warnings = []

    for tbl in root.findall(".//w:tbl", NS):
        for tr in tbl.findall("w:tr", NS):
            cells = []
            for tc in tr.findall("w:tc", NS):
                texts = [t.text or "" for t in tc.findall(".//w:t", NS)]
                cells.append(normalize_text("".join(texts)))
            item = parse_table_row(cells)
            if item and item["description"]:
                items.append(item)

    if not items:
        paragraphs = []
        for p in root.findall(".//w:p", NS):
            texts = [t.text or "" for t in p.findall(".//w:t", NS)]
            line = normalize_text("".join(texts))
            if line:
                paragraphs.append(line)
        for line in paragraphs:
            if is_ignored(line):
                continue
            if "|" in line:
                parts = [normalize_text(x) for x in line.split("|")]
                item = parse_table_row(parts)
                if item:
                    items.append(item)
    if not items:
        warnings.append("Không trích xuất được item rõ ràng từ file DOCX.")
    return {"items": items, "warnings": warnings}


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 scripts/extract_items_from_docx.py '<path-to-docx>'", file=sys.stderr)
        sys.exit(2)
    path = Path(sys.argv[1]).expanduser().resolve()
    if not path.exists():
        print(f"File không tồn tại: {path}", file=sys.stderr)
        sys.exit(1)
    result = extract_docx(path)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
