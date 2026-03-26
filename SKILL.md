---
name: openclaw-quote-bridge
description: force openclaw to route vietnamese báo giá requests to a real quote pdf generator through a local script and quote api instead of drafting the quotation itself.
---

# OpenClaw Quote Bridge

Route quote requests to the external quote generator. Do not compose the quotation yourself.

Workflow:
1. detect quote intent
2. collect fields
3. normalize payload
4. run local script
5. return generated PDF

Run:

python3 scripts/create_quote_pdf.py '<canonical_json_payload>'