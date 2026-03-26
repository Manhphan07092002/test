# Quote Payload And Templates

## Canonical payload

```json
{
  "customer": {
    "name": "",
    "address": "",
    "phone": "",
    "email": ""
  },
  "items": [
    {
      "description": "",
      "origin": "",
      "unit": "",
      "quantity": 0,
      "costPrice": 0
    }
  ],
  "profitRate": 12
}
```

## Field mapping

Map common column names and labels like this:

- `Khách hàng`, `Tên khách hàng` -> `customer.name`
- `Địa chỉ` -> `customer.address`
- `Điện thoại`, `Số điện thoại` -> `customer.phone`
- `Email` -> `customer.email`
- `Lãi suất`, `Biên lợi nhuận`, `Margin` -> `profitRate`
- `Tên hàng`, `Nội dung`, `Mô tả`, `Model`, `Description`, `Item`, `Product` -> `description`
- `Xuất xứ`, `Origin` -> `origin`
- `ĐVT`, `Đơn vị`, `Unit` -> `unit`
- `SL`, `Số lượng`, `Quantity`, `Qty` -> `quantity`
- `Giá nhập`, `Đơn giá nhập`, `Giá vốn`, `Cost Price`, `Unit Price`, `Đơn giá` -> `costPrice`

If both `giá bán` and `giá nhập` exist, prefer `giá nhập` for `costPrice`.

## Number normalization

Normalize these formats to plain numeric values:

- `1.500.000` -> `1500000`
- `1,500,000` -> `1500000`
- `1 500 000` -> `1500000`
- `12%` -> `12`

## Ignore rows and sections

Ignore rows or paragraphs that are clearly:

- header-only rows
- `Cộng tiền hàng`
- `VAT`
- `Tổng cộng`
- `Bằng chữ`
- `Điều khoản`
- `Thanh toán`
- `Giao hàng`
- `Hiệu lực báo giá`
- `Bảo hành`
- `Kính gửi`
- `Trân trọng`

## Example: simple chat request

Input:

```text
Tạo báo giá cho VNPT Huế
1 Router MikroTik | Latvia | cái | 2 | 1500000
Lãi suất 12
```

Payload:

```json
{
  "customer": {
    "name": "VNPT Huế",
    "address": "",
    "phone": "",
    "email": ""
  },
  "items": [
    {
      "description": "Router MikroTik",
      "origin": "Latvia",
      "unit": "cái",
      "quantity": 2,
      "costPrice": 1500000
    }
  ],
  "profitRate": 12
}
```

## Example: multiline quote

Input:

```text
báo giá cho Viễn Thông Đà Nẵng

1 Router MikroTik | Latvia | cái | 2 | 1500000
2 Switch TP-Link | China | cái | 5 | 900000
3 Converter quang | China | bộ | 3 | 450000

lãi suất 15
```

Payload:

```json
{
  "customer": {
    "name": "Viễn Thông Đà Nẵng",
    "address": "",
    "phone": "",
    "email": ""
  },
  "items": [
    {
      "description": "Router MikroTik",
      "origin": "Latvia",
      "unit": "cái",
      "quantity": 2,
      "costPrice": 1500000
    },
    {
      "description": "Switch TP-Link",
      "origin": "China",
      "unit": "cái",
      "quantity": 5,
      "costPrice": 900000
    },
    {
      "description": "Converter quang",
      "origin": "China",
      "unit": "bộ",
      "quantity": 3,
      "costPrice": 450000
    }
  ],
  "profitRate": 15
}
```

## Example: spreadsheet paste

Input:

```text
STT	Tên hàng	Xuất xứ	ĐVT	SL	Giá nhập
1	Router MikroTik	Latvia	cái	2	1500000
2	Switch TP-Link	China	cái	5	900000
```

The header row should be ignored. The two data rows should become items.

## Example: mixed file plus chat

Source 1: attached xlsx with item rows.
Source 2: chat says `Khách hàng: VNPT Đà Nẵng`.
Source 3: chat says `Lãi suất: 10`.

Final payload should merge all three sources into one canonical payload.

## Example: low-confidence clarification

If a file likely contains items but the price column could be sale price instead of input cost, ask:

`Em đã đọc được bảng hàng từ file, nhưng chưa chắc cột giá là giá nhập hay giá bán. Anh/chị xác nhận giúp em đó là giá nhập nhé.`

## Final execution reminder

After normalization, always run:

```text
cd ~/.openclaw/workspace/Skills/openclaw-quote-bridge
python3 scripts/create_quote_pdf.py '<payload>'
```
