# Payload and templates

## Canonical JSON payload

Use this JSON structure when calling the quote generator service:

```json
{
  "customer": {
    "name": "VIỄN THÔNG HUẾ",
    "address": "",
    "phone": "0912345678",
    "email": "abc@example.com"
  },
  "items": [
    {
      "description": "Bộ chuyển đổi tín hiệu Mini Converter SDI to HDMI 6G",
      "origin": "China",
      "unit": "cái",
      "quantity": 2,
      "costPrice": 1850000
    }
  ],
  "profitRate": 12
}
```

## Bot-to-bot forwarding template

Use this exact text template if the host system forwards the request to another bot instead of using HTTP:

```text
Khách hàng: {{customer.name}}
Địa chỉ: {{customer.address}}
Điện thoại: {{customer.phone}}
Email: {{customer.email}}

Hàng hóa:
{{#each items}}
{{index}}. {{description}} | {{origin}} | {{unit}} | {{quantity}} | {{costPrice}}
{{/each}}

Lãi suất: {{profitRate}}
```

Rules:

- Keep the labels exactly as shown.
- Keep the pipe-separated item format.
- Use one item per line.
- If `origin` or `unit` is missing, leave that field blank but keep the pipe separators.

## Missing-field prompt templates

### Missing customer name

```text
Em còn thiếu tên khách hàng để tạo báo giá. Anh/chị gửi giúp em tên khách hàng nhé.
```

### Missing item list

```text
Em chưa thấy danh sách hàng hóa. Anh/chị gửi mỗi dòng theo mẫu: Tên hàng | Xuất xứ | Đơn vị | Số lượng | Giá nhập
```

### Missing item quantity or cost price

```text
Em cần bổ sung thông tin cho mặt hàng "{{description}}":
- Số lượng
- Giá nhập
Anh/chị gửi giúp em nhé.
```

## Success caption

```text
Báo giá cho {{customer.name}} đã tạo xong. Em gửi file PDF bên dưới.
```

## Error caption

```text
Chưa tạo được báo giá. Lý do: {{error_message}}
```

## Example extraction

### User message

```text
Làm BG cho Viễn Thông Huế
2 bộ chuyển đổi Mini Converter SDI to HDMI 6G giá nhập 1.850.000, lãi suất 12%
```

### Normalized interpretation

```json
{
  "customer": {
    "name": "Viễn Thông Huế",
    "address": "",
    "phone": "",
    "email": ""
  },
  "items": [
    {
      "description": "Bộ chuyển đổi Mini Converter SDI to HDMI 6G",
      "origin": "",
      "unit": "",
      "quantity": 2,
      "costPrice": 1850000
    }
  ],
  "profitRate": 12
}
```
