---
name: openclaw-quote-bridge
description: guide openclaw to handle vietnamese báo giá requests, collect missing quote fields, normalize the request into a strict payload, forward the request to an external quote generator service or bot, and return the generated pdf or error back to the user. use when a user asks for bg, báo giá, quote, quotation, pricing sheet, or wants to create a sales quote from chat.
---

# OpenClaw Quote Bridge

Handle quote creation requests in Vietnamese with a strict, repeatable flow.

## Core workflow

Follow this sequence every time:

1. Detect whether the user is asking for a quote or price sheet.
2. Extract all available fields from the user's message.
3. If required fields are missing, ask only for the missing fields.
4. Normalize the request into the canonical payload shown in `references/payload-and-templates.md`.
5. Send that payload to the quote generator integration configured by the host system.
6. Return the PDF to the user.
7. If PDF generation fails, explain the exact missing field or integration error in Vietnamese.

## Trigger phrases

Treat these as quote intents unless the surrounding context clearly means something else:

- báo giá
- bg
- tạo báo giá
- làm báo giá
- quote
- quotation
- pricing
- price sheet

## Required fields

Do not submit the request until these are present:

- customer.name
- at least one item
- for each item: description, quantity, costPrice

These fields are optional unless the business requires them:

- customer.address
- customer.phone
- customer.email
- item.origin
- item.unit
- profitRate

Default `profitRate` to `12` if the user does not provide one.

## Extraction rules

Support both free text and semi-structured text.

Map Vietnamese labels as follows:

- `Khách hàng` -> `customer.name`
- `Địa chỉ` -> `customer.address`
- `Điện thoại` -> `customer.phone`
- `Email` -> `customer.email`
- `Lãi suất` -> `profitRate`
- `Hàng hóa` -> `items`

For item lines, prefer this format:

`Tên hàng | Xuất xứ | Đơn vị | Số lượng | Giá nhập`

If origin or unit is missing, still create the item if description, quantity, and cost price are present.

Normalize numbers by removing spaces, commas, and dots used as thousands separators before numeric parsing.

## Missing-information behavior

If information is incomplete, do not ask the user to repeat everything. Ask only for the missing pieces.

Good example:

`Em thiếu 2 thông tin để tạo báo giá: (1) tên khách hàng, (2) số lượng của mặt hàng MikroTik. Anh/chị gửi bổ sung giúp em nhé.`

Bad example:

`Anh/chị vui lòng nhập lại toàn bộ báo giá theo đúng mẫu.`

## Transport behavior

The host system must implement one integration path. Prefer them in this order:

1. HTTP POST to the quote generator endpoint.
2. Webhook call to an automation layer.
3. Forwarding a normalized message to another bot.

When the integration is HTTP-based, send the canonical JSON payload only. Do not send prose.

If the integration is bot-to-bot messaging, send the normalized request in the exact text template from `references/payload-and-templates.md` so the quote generator bot can parse it reliably.

## Response behavior

If the quote generator returns a PDF or file URL:

- send the file back to the user
- include a short Vietnamese caption
- mention the customer name if known

Use a concise caption such as:

`Báo giá cho {{customer.name}} đã tạo xong. Em gửi file PDF bên dưới.`

If the quote generator returns an error:

- surface the real error briefly
- if the error is a validation problem, name the offending field
- if the error is an integration problem, say that hệ thống tạo báo giá đang lỗi and ask the user to thử lại

## Safety and secrets

Never expose Telegram bot tokens, API keys, webhooks, or internal URLs to the user.
Never hardcode secrets in replies, examples, or logs.
Assume secrets are stored in environment variables or host configuration.
If the user pastes a token or secret, treat it as sensitive and do not repeat it.

## Output contract

Before calling the integration, internally structure the request as:

- `customer`: object
- `items`: array
- `profitRate`: number

Use the exact schema in `references/payload-and-templates.md`.

## Conversation style

- Reply in Vietnamese by default.
- Be operational and brief.
- When data is missing, ask in checklist form.
- When successful, confirm success and deliver the file.
- Do not mention internal normalization, parsing, or transport details unless the user asks.

## Edge cases

- If the user sends multiple quote requests in one message, split them into separate requests and confirm each one separately.
- If quantity or cost price is zero or invalid, treat it as missing and ask for correction.
- If the user gives `%` in profit rate, strip `%` and keep the numeric value.
- If the user asks to revise an existing quote, preserve prior fields and ask only for the changed ones.

## Files in this skill

- `references/payload-and-templates.md`: canonical payload, forwarding template, and examples.
