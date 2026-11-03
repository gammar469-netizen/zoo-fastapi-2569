"""FastAPI - Zoo visitors in Thailand, fiscal year 2569.

Data comes from a real Data.go.th resource (via API, or a CSV downloaded
from its official dataset page). No fabricated production data is used.
"""

import csv
import hashlib
import io
import os
from pathlib import Path

import httpx
from fastapi import FastAPI, HTTPException, Query

app = FastAPI(
    title="Zoo Visitors API - Fiscal Year 2569",
    description="ข้อมูลสถิติผู้เข้าชมสวนสัตว์ จาก Data.go.th ปีงบประมาณ 2569",
    version="1.0.0",
)

DATASET_URL = "https://data.go.th/dataset/zoo-visitors2569"
RESOURCE_ID = "0ecc96cf-d914-42a1-b184-dbbd013c3c9c"
DATA_FILE = Path(__file__).parent / "data" / "zoo_visitors.csv"
# SHA-256 of the real-row excerpt shipped for demonstration only.
DEMO_EXCERPT_SHA256 = "27bebd22ce966286897310b78083a9d0f352df524f7b0cab1680f79a66a862f9"
CKAN_BASE = os.getenv("CKAN_BASE", "https://data.go.th/api/3/action").rstrip("/")


def decode_csv(content: bytes) -> list[dict]:
    """Preserve original Thai column names; support common CSV encodings."""
    for encoding in ("utf-8-sig", "utf-8", "cp874", "tis-620"):
        try:
            text = content.decode(encoding)
            reader = csv.DictReader(io.StringIO(text))
            rows = [
                {str(k).strip(): (v.strip() if isinstance(v, str) else v)
                 for k, v in row.items() if k is not None}
                for row in reader
            ]
            if rows and "สวนสัตว์" in rows[0] and "รายการ" in rows[0]:
                return [row for row in rows if row.get("สวนสัตว์") and row.get("รายการ")]
        except (UnicodeDecodeError, csv.Error):
            pass
    raise ValueError("ไม่พบตาราง CSV ที่มีคอลัมน์ 'สวนสัตว์' และ 'รายการ'")


async def read_from_government_api(limit: int, offset: int):
    """Try the public CKAN DataStore endpoint for the given resource ID."""
    url = f"{CKAN_BASE}/datastore_search"
    async with httpx.AsyncClient(timeout=12, follow_redirects=True) as client:
        response = await client.get(
            url,
            params={"resource_id": RESOURCE_ID, "limit": limit, "offset": offset},
        )
        response.raise_for_status()
        body = response.json()

    if body.get("success") is not True or not isinstance(body.get("result"), dict):
        raise ValueError("DataStore ไม่มีผลลัพธ์สำหรับ Resource ID นี้")

    result = body["result"]
    records = result.get("records", [])
    if not isinstance(records, list) or not records:
        raise ValueError("DataStore ไม่ส่งรายการข้อมูล")
    return {
        "source_type": "government_api",
        "source_url": str(response.url),
        "total": result.get("total", len(records)),
        "data": records,
        "is_excerpt": False,
    }


@app.get("/", tags=["General"])
def home():
    return {"message": "Zoo Visitors API 2569", "docs": "/docs"}


@app.get("/api/zoo-visitors", tags=["Zoo visitors"])
async def zoo_visitors(
    limit: int = Query(default=10, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
):
    """Return real source records, preserving the source's varying columns."""
    # Use the CSV provided from Data.go.th first, if it exists.
    # Otherwise, request the specified CKAN resource online.
    if DATA_FILE.is_file():
        try:
            all_rows = decode_csv(DATA_FILE.read_bytes())
        except (OSError, ValueError) as exc:
            raise HTTPException(status_code=500, detail=f"อ่าน CSV ไม่สำเร็จ: {exc}") from exc
        if not all_rows:
            raise HTTPException(status_code=503, detail="CSV ไม่มีรายการข้อมูล")
        subset = all_rows[offset:offset + limit]
        details = {
            "source_type": "csv_from_dataset_page",
            "source_url": DATASET_URL,
            "total": len(all_rows),
            "data": subset,
            "is_excerpt": hashlib.sha256(DATA_FILE.read_bytes()).hexdigest() == DEMO_EXCERPT_SHA256,
        }
    else:
        try:
            details = await read_from_government_api(limit, offset)
        except (httpx.HTTPError, ValueError, KeyError) as exc:
            raise HTTPException(
                status_code=503,
                detail=("ดึง API ต้นทางไม่ได้ กรุณาดาวน์โหลดไฟล์ CSV จาก Data.go.th "
                        "แล้วบันทึกไว้ที่ data/zoo_visitors.csv "
                        f"(เหตุผล: {type(exc).__name__})"),
            ) from exc

    return {
        "dataset": "zoo-visitors2569",
        "fiscal_year": 2569,
        "resource_id": RESOURCE_ID,
        "source_type": details["source_type"],
        "source_url": details["source_url"],
        "is_excerpt": details["is_excerpt"],
        "total": details["total"],
        "limit": limit,
        "offset": offset,
        "data": details["data"],
    }
