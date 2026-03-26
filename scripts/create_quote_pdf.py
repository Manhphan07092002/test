#!/usr/bin/env python3
import json,sys,requests,os,uuid
from pathlib import Path

API_URL=os.environ.get("QUOTE_API_URL","http://127.0.0.1:3000/api/quote")
OUT_DIR=Path("/tmp/openclaw-quotes")
OUT_DIR.mkdir(parents=True,exist_ok=True)

if len(sys.argv)!=2:
    print("Usage: create_quote_pdf.py '<json_payload>'",file=sys.stderr)
    sys.exit(1)

payload=json.loads(sys.argv[1])

r=requests.post(API_URL,json=payload,timeout=120)
if r.status_code!=200:
    print("API error:",r.text,file=sys.stderr)
    sys.exit(2)

if "application/pdf" not in r.headers.get("content-type",""):
    print("API did not return PDF",file=sys.stderr)
    sys.exit(3)

name=payload.get("customer",{}).get("name","bao-gia").replace(" ","-")
file=OUT_DIR/f"{name}-{uuid.uuid4().hex[:6]}.pdf"
file.write_bytes(r.content)

print(str(file))