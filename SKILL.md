---
name: openclaw-quote-bridge
description: force openclaw to route vietnamese báo giá requests to an external quote generator bot or api instead of drafting the quotation itself. use when a user asks for bg, báo giá, tạo báo giá, quote, quotation, pricing sheet, or provides customer information, item lines, quantities, prices, or profit rate for quote generation.
---

# OpenClaw Quote Bridge

Route quote requests to the external quote generator. Do not compose the final quotation content yourself.

## Non-negotiable rule

For any quote intent, do not generate:
- a finished quotation table
- a markdown quotation
- a sales message
- a zalo message
- internal pricing notes
- a pseudo-pdf response
- a manually drafted “bảng chào giá”

Your job is only to:

1. detect quote intent
2. collect missing fields
3. normalize the request
4. forward it to the configured integration
5. return the generated PDF or the real integration error

If no integration is configured or callable, say so briefly in Vietnamese. Do not fabricate a quote.

## Quote intent triggers

Treat these as quote intents unless context clearly means something else:

- báo giá
- bg
- tạo báo giá
- làm báo giá
- quote
- quotation
- pricing
- price sheet

## Required output behavior

When the user asks for a quote:

- never answer with a completed quote body
- never calculate and present a final formatted quotation directly
- never create “tin nhắn 1 / tin nhắn 2 / tin nhắn 3”
- always follow the transport workflow below

## Transport workflow

Always follow this order:

1. Detect quote request.
2. Extract available fields.
3. Ask only for missing required fields.
4. Build the canonical payload.
5. Send the payload to the external quote generator integration.
6. Return the PDF or file result.
7. If the integration fails, return the real error briefly in Vietnamese.

## Integration priority

Use exactly one configured path, in this order:

1. HTTP POST to quote API
2. webhook automation
3. forwarding normalized text to quote bot

If none is configured, reply exactly:

`Em đã nhận yêu cầu báo giá nhưng hệ thống cầu nối sang bot tạo báo giá chưa được cấu hình, nên em chưa thể tạo file PDF tự động.`

Do not generate a manual quote in place of the missing integration.

## Required fields

Do not submit until these fields are present:

- customer.name
- at least one item
- for each item:
  - description
  - quantity
  - costPrice

Optional fields:

- customer.address
- customer.phone
- customer.email
- item.origin
- item.unit
- profitRate

Default `profitRate` to `12` if omitted.

## Extraction rules

Support both free text and semi-structured text.

Map labels like this:

- `Khách hàng` -> `customer.name`
- `Địa chỉ` -> `customer.address`
- `Điện thoại` -> `customer.phone`
- `Email` -> `customer.email`
- `Lãi suất` -> `profitRate`
- `Hàng hóa` -> `items`

Preferred item format:

`Tên hàng | Xuất xứ | Đơn vị | Số lượng | Giá nhập`

If origin or unit is missing, still accept the item when description, quantity, and cost price are present.

Normalize numbers by removing spaces, commas, and dots used as thousands separators before parsing.

## Missing-information behavior

Ask only for missing pieces.

Good:

`Em thiếu 2 thông tin để tạo báo giá: (1) tên khách hàng, (2) số lượng của mặt hàng MikroTik. Anh/chị gửi bổ sung giúp em nhé.`

Bad:

`Anh/chị vui lòng nhập lại toàn bộ theo mẫu.`

## Output contract

Before transport, structure the request internally as:

- `customer`: object
- `items`: array
- `profitRate`: number

Use the exact schema and forwarding template in `references/payload-and-templates.md`.

## Bot-to-bot forwarding rule

If the configured integration is another bot, forward only the normalized block from `references/payload-and-templates.md`.

Do not add:
- greetings
- explanation
- markdown table
- pricing notes
- extra prose before the block
- extra prose after the block

## Success behavior

If the quote generator returns a PDF or file URL:

- send the file back to the user
- include a short Vietnamese caption
- mention customer name if known

Suggested caption:

`Báo giá cho {{customer.name}} đã tạo xong. Em gửi file PDF bên dưới.`

## Error behavior

If the quote generator returns an error:

- show the real error briefly
- if validation failed, name the missing or invalid field
- if transport failed, say:

`Hệ thống tạo báo giá đang lỗi kết nối. Anh/chị thử lại giúp em sau ít phút.`

Do not replace the failed integration with a manually drafted quote.

## Conversation style

- Reply in Vietnamese by default.
- Be brief and operational.
- Ask in checklist form when data is missing.
- Do not mention internal parsing unless asked.

## Safety and secrets

- Never expose bot tokens, api keys, webhook URLs, or internal endpoints.
- Never repeat secrets pasted by the user.
- Assume secrets live in environment variables or host configuration.

## Edge cases

- If the user sends multiple quote requests in one message, split them into separate normalized requests.
- If quantity or cost price is zero or invalid, treat it as missing.
- If the user gives `%`, strip it and keep the numeric value.
- If revising an existing quote, preserve prior fields and ask only for changed values.

## Files in this skill

- `references/payload-and-templates.md`: canonical payload, forwarding template, and examples.
