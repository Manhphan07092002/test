---
name: openclaw-quote-bridge
description: route vietnamese báo giá requests to the external quote generator api and return a pdf quotation. use when the user asks for báo giá, bg, quote, quotation, pricing sheet, sends multiline item tables, pastes spreadsheet rows, or shares customer quote content or files that must be normalized into a quote payload. support xlsx, docx, and pdf extraction through bundled scripts. never compose quotation text manually.
---

# OpenClaw Quote Bridge

Use this skill to turn Vietnamese quote requests into a real PDF quotation by normalizing customer and item data, optionally extracting rows from attached files, then running the local quote-generation script.

## Non-negotiable rule

For quote intents, do not produce a manual quotation body, markdown price table, sales message, or pseudo-PDF. Only:

1. detect quote intent
2. extract and merge data from chat and files
3. ask only for missing required fields
4. normalize the canonical payload
5. run the local quote PDF script from the skill root
6. return the generated PDF or the real error

## Intent detection

Treat these as quote intents unless context clearly means something else:

- báo giá
- bg
- tạo báo giá
- làm báo giá
- quote
- quotation
- pricing
- price sheet
- xuất pdf báo giá
- làm file pdf báo giá
- làm lại báo giá từ file
- đọc file báo giá khách gửi

## Required fields

Do not run the quote PDF script until these are present:

- `customer.name`
- at least one item
- for each item:
  - `description`
  - `quantity`
  - `costPrice`

Optional fields:

- `customer.address`
- `customer.phone`
- `customer.email`
- `item.origin`
- `item.unit`
- `profitRate`

Default `profitRate` to `12` when omitted.

## Canonical payload

Always normalize to this schema before PDF generation:

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

See `references/payload-and-templates.md` for examples.

## Supported input types

### Semi-structured text

Prefer direct parsing for input such as:

```text
Khách hàng: VNPT Huế
Địa chỉ:
Điện thoại:
Email:

Hàng hóa:
1. Router MikroTik | Latvia | cái | 2 | 1500000

Lãi suất: 12
```

### Multiline item blocks

Accept repeated item lines with or without numbering.

Preferred item format:

```text
Tên hàng | Xuất xứ | Đơn vị | Số lượng | Giá nhập
```

### Excel paste and spreadsheet rows

Support tab-separated or multi-space row pastes. Ignore header rows and total/VAT/notes rows.

### File attachments

If the request depends on attached files or pasted extracted file content:

- use `scripts/extract_items_from_xlsx.py` for `.xlsx` or `.xlsm`
- use `scripts/extract_items_from_docx.py` for `.docx`
- use `scripts/extract_items_from_pdf.py` for `.pdf`

Use the extracted rows as input material, then normalize them into the canonical payload.

## File extraction workflow

### Excel files

Run:

```bash
python3 scripts/extract_items_from_xlsx.py '<path-to-xlsx>'
```

The script returns JSON to stdout with:

- detected sheet name
- detected header row
- extracted `items`
- warnings

Map the extracted items into the canonical payload and merge with any customer or profit-rate details from chat.

### Word files

Run:

```bash
python3 scripts/extract_items_from_docx.py '<path-to-docx>'
```

Use the returned JSON rows and warnings. Prefer table rows over loose paragraphs when both exist.

### PDF files

Run:

```bash
python3 scripts/extract_items_from_pdf.py '<path-to-pdf>'
```

Use the extracted rows if the script found likely item lines. If confidence is low, ask a short clarification question for only the ambiguous rows or fields.

## Parsing rules

Map these labels when present in chat text:

- `Khách hàng` -> `customer.name`
- `Tên khách hàng` -> `customer.name`
- `Địa chỉ` -> `customer.address`
- `Điện thoại` -> `customer.phone`
- `Số điện thoại` -> `customer.phone`
- `Email` -> `customer.email`
- `Lãi suất` -> `profitRate`
- `Biên lợi nhuận` -> `profitRate`
- `Margin` -> `profitRate`
- `Hàng hóa` -> `items`

Normalize numbers by removing spaces, commas, and dots used as thousands separators before parsing. Strip `%` from profit rates.

## Missing-information behavior

Ask only for missing required pieces. Good example:

`Em thiếu 2 thông tin để tạo báo giá: (1) số lượng của mặt hàng Switch TP-Link, (2) giá nhập của mặt hàng Converter quang. Anh/chị gửi bổ sung giúp em nhé.`

Bad example:

`Anh/chị vui lòng nhập lại toàn bộ báo giá theo mẫu.`

## Root-directory execution rule

The quote PDF script must be run from the skill root so relative paths always resolve correctly.

Always run exactly this pattern:

```bash
cd ~/.openclaw/workspace/Skills/openclaw-quote-bridge && \
python3 scripts/create_quote_pdf.py '<canonical_json_payload>'
```

Do not run the script from a subdirectory. Do not omit the `cd` step unless you are already certain the current directory is the skill root.

## Quote PDF script behavior

`scripts/create_quote_pdf.py` sends the canonical JSON payload to the quote API, writes the returned PDF into the output directory, and prints the filesystem path to stdout.

Default API URL:

```text
http://127.0.0.1:3000/api/quote
```

Default output directory:

```text
/tmp/openclaw-quotes/
```

## Success behavior

If the PDF script returns a valid PDF path:

- send the PDF back to the user
- use a short Vietnamese caption
- do not also send a manual quote body

Suggested caption:

`Báo giá cho {{customer.name}} đã tạo xong. Em gửi file PDF bên dưới ạ.`

## Error behavior

If extraction is incomplete, ask only for the missing or ambiguous pieces.

If the quote script fails:

- surface the real validation error briefly in Vietnamese when possible
- for connection or transport failures, say:

`Hệ thống tạo báo giá đang lỗi kết nối. Anh/chị thử lại giúp em sau ít phút.`

Do not replace a failed integration with a manual quotation.

## Forbidden behavior

Never:

- write the final quotation manually
- create a markdown quote table instead of the PDF
- invent missing quantities, prices, or customer names
- expose tokens, API keys, webhook URLs, or internal endpoints

## Files in this skill

- `scripts/create_quote_pdf.py`
- `scripts/extract_items_from_xlsx.py`
- `scripts/extract_items_from_docx.py`
- `scripts/extract_items_from_pdf.py`
- `references/payload-and-templates.md`
