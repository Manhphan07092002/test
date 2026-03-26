#!/usr/bin/env python3
import json
import os
import re
import sys
import uuid
from pathlib import Path

import requests

DEFAULT_API_URL = "http://127.0.0.1:3000/api/quote"
OUTPUT_DIR = Path(os.environ.get("QUOTE_OUTPUT_DIR", "/tmp/openclaw-quotes"))


class QuoteError(Exception):
    pass


def fail(message: str, code: int = 1) -> None:
    print(message, file=sys.stderr)
    sys.exit(code)


def sanitize_filename(name: str) -> str:
    name = name.strip() or "bao-gia"
    name = re.sub(r"\s+", "-", name)
    name = re.sub(r"[^a-zA-Z0-9\-_.àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđÀÁẠẢÃÂẦẤẬẨẪĂẰẮẶẲẴÈÉẸẺẼÊỀẾỆỂỄÌÍỊỈĨÒÓỌỎÕÔỒỐỘỔỖƠỜỚỢỞỠÙÚỤỦŨƯỪỨỰỬỮỲÝỴỶỸĐ]+",
                  "-", name)
    name = name.strip("-_.")
    return name or "bao-gia"


def validate_payload(payload: dict) -> None:
    if not isinstance(payload, dict):
        raise QuoteError("Payload không hợp lệ: phải là object JSON.")
    customer = payload.get("customer")
    if not isinstance(customer, dict):
        raise QuoteError("Thiếu customer hợp lệ.")
    customer_name = str(customer.get("name", "")).strip()
    if not customer_name:
        raise QuoteError("Thiếu tên khách hàng.")
    items = payload.get("items")
    if not isinstance(items, list) or not items:
        raise QuoteError("Thiếu danh sách hàng hóa.")
    for idx, item in enumerate(items, start=1):
        if not isinstance(item, dict):
            raise QuoteError(f"Mặt hàng #{idx} không hợp lệ.")
        description = str(item.get("description", "")).strip()
        if not description:
            raise QuoteError(f"Mặt hàng #{idx} thiếu mô tả.")
        quantity = item.get("quantity")
        cost_price = item.get("costPrice")
        try:
            quantity_num = float(quantity)
        except Exception:
            quantity_num = 0
        try:
            cost_price_num = float(cost_price)
        except Exception:
            cost_price_num = 0
        if quantity_num <= 0:
            raise QuoteError(f'Mặt hàng "{description}" thiếu hoặc sai số lượng.')
        if cost_price_num <= 0:
            raise QuoteError(f'Mặt hàng "{description}" thiếu hoặc sai giá nhập.')
    profit_rate = payload.get("profitRate", 12)
    try:
        payload["profitRate"] = float(profit_rate)
    except Exception:
        payload["profitRate"] = 12.0


def get_api_url() -> str:
    return os.environ.get("QUOTE_API_URL", DEFAULT_API_URL).strip() or DEFAULT_API_URL


def extract_filename(response: requests.Response, customer_name: str) -> str:
    disposition = response.headers.get("content-disposition", "")
    match = re.search(r'filename="([^"]+)"', disposition, re.IGNORECASE)
    if match:
        filename = match.group(1).strip()
        if filename.lower().endswith(".pdf"):
            return filename
    safe_name = sanitize_filename(customer_name)
    return f"{safe_name}-{uuid.uuid4().hex[:8]}.pdf"


def write_pdf(content: bytes, filename: str) -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUTPUT_DIR / filename
    out_path.write_bytes(content)
    return out_path.resolve()


def call_quote_api(payload: dict) -> Path:
    api_url = get_api_url()
    try:
        response = requests.post(api_url, json=payload, timeout=120)
    except requests.RequestException as exc:
        raise QuoteError(f"Lỗi kết nối API báo giá: {exc}") from exc
    if not response.ok:
        detail = response.text.strip() if getattr(response, "text", None) else ""
        raise QuoteError(f"API báo giá lỗi {response.status_code}: {detail or 'không rõ lỗi'}")
    content_type = (response.headers.get("content-type") or "").lower()
    if "application/pdf" not in content_type:
        detail = response.text.strip() if getattr(response, "text", None) else ""
        raise QuoteError(f"API không trả về PDF: {detail or 'nội dung không hợp lệ'}")
    customer_name = str(payload.get("customer", {}).get("name", "")).strip() or "bao-gia"
    filename = extract_filename(response, customer_name)
    return write_pdf(response.content, filename)


def main() -> None:
    if len(sys.argv) != 2:
        fail("Usage: python3 scripts/create_quote_pdf.py '<json_payload>'", 2)
    raw_payload = sys.argv[1]
    try:
        payload = json.loads(raw_payload)
    except json.JSONDecodeError as exc:
        fail(f"JSON không hợp lệ: {exc}", 2)
    try:
        validate_payload(payload)
        pdf_path = call_quote_api(payload)
    except QuoteError as exc:
        fail(str(exc), 1)
    print(str(pdf_path))


if __name__ == "__main__":
    main()
