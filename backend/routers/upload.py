import datetime
import io
import json
import os
from typing import Optional

from fastapi import APIRouter, Depends, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from db.database import SessionLocal, engine
from db.crud import create_session, save_fields, get_fields_by_session
from models.import_session import ImportSession
from models.import_field import ImportField
from services.ocr.base import get_ocr_provider
from services.extractor import merge
from output.exporter import export_csv, export_excel

ImportSession.metadata.create_all(bind=engine)
ImportField.metadata.create_all(bind=engine)

router = APIRouter()

# items一時保存（record_id → items）
_items_store: dict[int, list[dict]] = {}


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/process")
async def process(
    pdf_file: UploadFile = File(...),
    image_file: UploadFile = File(...),
    exchange_rate: Optional[float] = Form(None),
    db: Session = Depends(get_db),
):
    pdf_bytes = await pdf_file.read()
    image_bytes = await image_file.read()

    # B担当: OCR抽出
    ocr = get_ocr_provider()
    pdf_data = ocr.extract(pdf_bytes, pdf_file.content_type)
    image_data = ocr.extract(image_bytes, image_file.content_type)

    # B担当: マージ
    merged = merge(pdf_data, image_data)
    basic_info = merged["basic_info"]  # list[dict]
    items = merged["items"]            # list[dict]

    # 為替レートの決定（優先順位: PDF → 画像 → UI入力）
    rate = None
    rate_source = None

    for field in basic_info:
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

    # 為替レートをbasic_infoに追加
    basic_info = [f for f in basic_info if f["key"] != "exchange_rate"]
    basic_info.append({
        "key": "exchange_rate",
        "value": rate,
        "source": rate_source,
        "value_type": "float"
    })

    # C担当: DBに保存
    session_record = create_session(
        db=db,
        pdf_filename=pdf_file.filename,
        image_filename=image_file.filename,
        merge_strategy="pdf_first",
        warnings=json.dumps([], ensure_ascii=False),
    )
    save_fields(db=db, session_id=session_record.id, fields=basic_info)
    # 品目明細に円換算額を追加
    for item in items:
        if item.get("amount") is not None:
            amt = float(str(item["amount"]).replace(",", ""))
            item["amount(円換算)"] = f"{round(amt * rate):,}円"
        else:
            item["amount(円換算)"] = None
    _items_store[session_record.id] = items

    return {
        "status": "ok",
        "record_id": session_record.id,
        "pdf": pdf_file.filename,
        "image": image_file.filename,
        "basic_info": basic_info,
        "items": items,
        "warnings": [],
    }


@router.get("/export/csv/{record_id}")
def download_csv(record_id: int, db: Session = Depends(get_db)):
    now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"import_{now}.csv"
    output_path = f"/tmp/{filename}"
    items = _items_store.get(record_id, [])
    export_csv(db=db, record_id=record_id, output_path=output_path, items=items)
    with open(output_path, "rb") as f:
        content = f.read()
    return StreamingResponse(
        io.BytesIO(content),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{filename}"}
    )


@router.get("/export/excel/{record_id}")
def download_excel(record_id: int, db: Session = Depends(get_db)):
    now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"import_{now}.xlsx"
    output_path = f"/tmp/{filename}"
    items = _items_store.get(record_id, [])
    export_excel(db=db, record_id=record_id, output_path=output_path, items=items)
    with open(output_path, "rb") as f:
        content = f.read()
    return StreamingResponse(
        io.BytesIO(content),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{filename}"}
    )
