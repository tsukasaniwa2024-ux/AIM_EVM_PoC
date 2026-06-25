from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from typing import Optional
import csv
import io
import datetime

from services.ocr.base import get_ocr_provider
from services.extractor import merge

# 仮のデータストア（C担当のDB実装後に置き換え）
_last_result = {}

router = APIRouter()


@router.post("/process")
async def process(
    pdf_file: UploadFile = File(...),
    image_file: UploadFile = File(...),
    exchange_rate: Optional[float] = Form(None),
):
    pdf_bytes = await pdf_file.read()
    image_bytes = await image_file.read()

    # B担当: OCR抽出
    ocr = get_ocr_provider()
    pdf_data = ocr.extract(pdf_bytes, pdf_file.content_type)
    image_data = ocr.extract(image_bytes, image_file.content_type)

    # B担当: マージ
    fields = merge(pdf_data, image_data)

    # 為替レートの決定（優先順位: PDF → 画像 → UI入力）
    rate = None
    rate_source = None

    for field in fields:
        if field["key"] == "exchange_rate" and field["value"] is not None:
            rate = float(field["value"])
            rate_source = field["source"]
            break

    if rate is None and exchange_rate is not None:
        rate = exchange_rate
        rate_source = "manual"

    if rate is None:
        return {
            "status": "error",
            "message": "為替レートが取得できませんでした。UIから手動入力してください。"
        }

    # 為替レートをfieldsに追加（上書き）
    fields = [f for f in fields if f["key"] != "exchange_rate"]
    fields.append({
        "key": "exchange_rate",
        "value": rate,
        "source": rate_source,
        "value_type": "float"
    })

    warnings = [f["key"] for f in fields if f["value"] is None]

    _last_result["fields"] = fields

    return {
        "status": "ok",
        "record_id": 1,
        "pdf": pdf_file.filename,
        "image": image_file.filename,
        "fields": fields,
        "warnings": warnings,
    }


@router.get("/export/csv/{record_id}")
async def export_csv(record_id: int):
    fields = _last_result.get("fields", [])
    now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"import_{now}.csv"

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["項目名", "値", "抽出元"])
    for field in fields:
        writer.writerow([field["key"], field["value"], field["source"]])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.get("/export/excel/{record_id}")
async def export_excel(record_id: int):
    import openpyxl
    fields = _last_result.get("fields", [])
    now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"import_{now}.xlsx"

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "抽出結果"
    ws.append(["項目名", "値", "抽出元"])
    for field in fields:
        ws.append([field["key"], str(field["value"]), field["source"]])

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
