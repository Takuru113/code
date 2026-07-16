#!/usr/bin/env python3
"""Write MCN Markdown deliverables to a Feishu docx document.

Dry-run is the default. Use --execute only after FEISHU_APP_ID and
FEISHU_APP_SECRET are provided through environment variables.
"""

from __future__ import annotations

import argparse
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

API = "https://open.feishu.cn/open-apis"


def request_json(method: str, url: str, payload=None, token: str | None = None, retries: int = 4):
    data = None if payload is None else json.dumps(payload, ensure_ascii=False).encode("utf-8")
    headers = {"Content-Type": "application/json; charset=utf-8"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    for attempt in range(retries):
        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                body = json.loads(response.read().decode("utf-8"))
            if body.get("code", 0) == 99991400 and attempt + 1 < retries:
                time.sleep(2**attempt)
                continue
            if body.get("code", 0) != 0:
                raise RuntimeError(f"Feishu API error {body.get('code')}: {body.get('msg')}")
            return body
        except urllib.error.HTTPError as exc:
            if exc.code in (429, 500, 502, 503) and attempt + 1 < retries:
                time.sleep(2**attempt)
                continue
            detail = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"HTTP {exc.code}: {detail}") from exc
    raise RuntimeError("Feishu API retry limit reached")


def markdown_to_blocks(markdown: str) -> list[dict]:
    blocks = []
    for raw in markdown.splitlines():
        line = raw.rstrip()
        if not line:
            continue
        # Use text blocks for broad API compatibility; retain Markdown heading marks.
        blocks.append(
            {
                "block_type": 2,
                "text": {
                    "elements": [
                        {
                            "text_run": {
                                "content": line[:5000],
                                "text_element_style": {},
                            }
                        }
                    ],
                    "style": {},
                },
            }
        )
    return blocks


def load_inputs(paths: list[Path]) -> str:
    sections = []
    for path in paths:
        sections.append(f"# 来源文件：{path.name}\n\n{path.read_text(encoding='utf-8')}")
    return "\n\n---\n\n".join(sections)


def get_tenant_token(app_id: str, app_secret: str) -> str:
    body = request_json(
        "POST",
        f"{API}/auth/v3/tenant_access_token/internal",
        {"app_id": app_id, "app_secret": app_secret},
    )
    return body["tenant_access_token"]


def create_document(token: str, title: str, folder_token: str | None) -> str:
    query = ""
    if folder_token:
        query = "?" + urllib.parse.urlencode({"folder_token": folder_token})
    body = request_json("POST", f"{API}/docx/v1/documents{query}", {"title": title}, token)
    return body["data"]["document"]["document_id"]


def append_blocks(token: str, document_id: str, blocks: list[dict]) -> None:
    url = f"{API}/docx/v1/documents/{document_id}/blocks/{document_id}/children"
    for start in range(0, len(blocks), 40):
        request_json("POST", url, {"index": -1, "children": blocks[start : start + 40]}, token)
        time.sleep(0.4)


def verify_document(token: str, document_id: str, expected_title: str) -> dict:
    meta = request_json("GET", f"{API}/docx/v1/documents/{document_id}", token=token)
    raw = request_json("GET", f"{API}/docx/v1/documents/{document_id}/raw_content", token=token)
    actual_title = meta["data"]["document"]["title"]
    content = raw["data"].get("content", "")
    return {
        "title_matches": actual_title == expected_title,
        "content_chars": len(content),
        "contains_project_name": "小红书达人调研" in content,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("inputs", nargs="+", type=Path)
    parser.add_argument("--title", default="小红书达人调研 + 商单脚本生成助手")
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--receipt", type=Path, default=Path("automation/output/feishu-receipt.json"))
    args = parser.parse_args()

    markdown = load_inputs(args.inputs)
    blocks = markdown_to_blocks(markdown)
    preview = {"mode": "execute" if args.execute else "dry-run", "files": [str(p) for p in args.inputs], "blocks": len(blocks), "chars": len(markdown)}
    if not args.execute:
        print(json.dumps(preview, ensure_ascii=False, indent=2))
        return 0

    app_id = os.environ.get("FEISHU_APP_ID")
    app_secret = os.environ.get("FEISHU_APP_SECRET")
    if not app_id or not app_secret:
        raise SystemExit("FEISHU_APP_ID and FEISHU_APP_SECRET are required for --execute")
    token = get_tenant_token(app_id, app_secret)
    document_id = create_document(token, args.title, os.environ.get("FEISHU_FOLDER_TOKEN"))
    append_blocks(token, document_id, blocks)
    verification = verify_document(token, document_id, args.title)
    receipt = {
        **preview,
        "document_id": document_id,
        "document_url": f"https://feishu.cn/docx/{document_id}",
        "verification": verification,
    }
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    args.receipt.write_text(json.dumps(receipt, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(receipt, ensure_ascii=False, indent=2))
    return 0 if all(verification.values()) else 2


if __name__ == "__main__":
    raise SystemExit(main())

