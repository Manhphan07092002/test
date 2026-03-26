# Payload And Templates

Use this file as the canonical schema and forwarding reference for all quote requests.

## Canonical JSON payload

Always normalize the request internally into this JSON structure before transport:

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

## Field rules

### customer

- `customer.name`: required
- `customer.address`: optional
- `customer.phone`: optional
- `customer.email`: optional

### items

At least one item is required.

For each item:
- `description`: required
- `origin`: optional
- `unit`: optional
- `quantity`: required and must be greater than 0
- `costPrice`: required and must be greater than 0

### profitRate

- optional in user input
- default to `12` if missing
- strip `%` if present
- store as a number only

## Normalization rules

### Labels

Map these Vietnamese labels:

- `Khách hàng` -> `customer.name`
- `Địa chỉ` -> `customer.address`
- `Điện thoại` -> `customer.phone`
- `Email` -> `customer.email`
- `Lãi suất` -> `profitRate`
- `Hàng hóa` -> `items`

### Numbers

Before parsing numeric fields:

- remove spaces
- remove commas used as thousands separators
- remove dots used as thousands separators

Examples:
- `1 500 000` -> `1500000`
- `1,500,000` -> `1500000`
- `1.500.000` -> `1500000`
- `12%` -> `12`

### Items

Preferred item input format:

`Tên hàng | Xuất xứ | Đơn vị | Số lượng | Giá nhập`

If origin or unit is missing, still accept the line if:
- description is present
- quantity is valid
- costPrice is valid

## Bot-to-bot forwarding template

If the active integration path is forwarding to another bot, send exactly this text block and nothing else:

```text
Khách hàng: {{customer.name}}
Địa chỉ: {{customer.address}}
Điện thoại: {{customer.phone}}
Email: {{customer.email}}

Hàng hóa:
1. {{item1.description}} | {{item1.origin}} | {{item1.unit}} | {{item1.quantity}} | {{item1.costPrice}}
2. {{item2.description}} | {{item2.origin}} | {{item2.unit}} | {{item2.quantity}} | {{item2.costPrice}}

Lãi suất: {{profitRate}}
```

## Forwarding rules

When forwarding to another bot:

- do not add greeting text
- do not add markdown
- do not add explanations
- do not add summary text
- do not add internal notes
- do not add sales copy
- do not add quotation table
- do not add commentary before the normalized block
- do not add commentary after the normalized block

## HTTP transport rule

When the integration path is HTTP:

- send JSON only
- use the canonical schema exactly
- do not send prose
- do not wrap the payload in markdown fences

## Examples

### Example 1: minimal valid request

User input:

```text
Tạo báo giá cho khách hàng VNPT Huế
1 Router MikroTik | Latvia | cái | 2 | 1500000
lãi suất 12
```

Normalized payload:

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

Forwarded bot text:

```text
Khách hàng: VNPT Huế
Địa chỉ: 
Điện thoại: 
Email: 

Hàng hóa:
1. Router MikroTik | Latvia | cái | 2 | 1500000

Lãi suất: 12
```

### Example 2: missing optional fields

User input:

```text
BG cho khách hàng ABC
1 Switch TP-Link |  |  | 3 | 900000
```

Normalized payload:

```json
{
  "customer": {
    "name": "ABC",
    "address": "",
    "phone": "",
    "email": ""
  },
  "items": [
    {
      "description": "Switch TP-Link",
      "origin": "",
      "unit": "",
      "quantity": 3,
      "costPrice": 900000
    }
  ],
  "profitRate": 12
}
```

Forwarded bot text:

```text
Khách hàng: ABC
Địa chỉ: 
Điện thoại: 
Email: 

Hàng hóa:
1. Switch TP-Link |  |  | 3 | 900000

Lãi suất: 12
```

### Example 3: ask only for missing required fields

User input:

```text
Làm báo giá cho khách hàng VNPT
1 Router MikroTik | Latvia | cái |  | 1500000
```

Correct assistant response:

```text
Em thiếu 1 thông tin để tạo báo giá: (1) số lượng của mặt hàng Router MikroTik. Anh/chị gửi bổ sung giúp em nhé.
```

### Example 4: invalid cost price

User input:

```text
Khách hàng: ABC
Hàng hóa:
1. Router MikroTik | Latvia | cái | 2 | 0
```

Correct assistant response:

```text
Em thiếu 1 thông tin để tạo báo giá: (1) giá nhập hợp lệ của mặt hàng Router MikroTik. Anh/chị gửi bổ sung giúp em nhé.
```

## Strict behavior reminder

For quote requests, never produce the final quotation manually.

Do only this:

1. extract
2. validate
3. normalize
4. transport
5. return PDF or real error
