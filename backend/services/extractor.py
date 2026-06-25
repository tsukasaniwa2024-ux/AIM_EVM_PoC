from typing import Any


def merge(pdf_data: dict, image_data: dict, strategy: str = "both") -> dict:
    """
    PDFと画像から抽出したデータを合体して返す。
    同じキーが両方にあっても両方表示する。
    """
    pdf_basic = pdf_data.get("basic_info", {})
    image_basic = image_data.get("basic_info", {})
    pdf_items = pdf_data.get("items", [])
    image_items = image_data.get("items", [])

    basic_info = []

    # PDFの項目をすべて追加
    for key, value in pdf_basic.items():
        if value is None:
            continue
        basic_info.append({
            "key": key,
            "value": value,
            "source": "pdf",
            "value_type": _type_name(value),
        })

    # 画像の項目をすべて追加（PDFと同じキーでも別行で追加）
    for key, value in image_basic.items():
        if value is None:
            continue
        # PDFに同じキーがあれば source を「image（重複）」にする
        pdf_keys = {f["key"] for f in basic_info}
        source = "image（重複）" if key in pdf_keys else "image"
        basic_info.append({
            "key": key,
            "value": value,
            "source": source,
            "value_type": _type_name(value),
        })

    # 品目はPDF優先、なければ画像
    items = pdf_items if pdf_items else image_items

    return {
        "basic_info": basic_info,
        "items": items,
    }


def _type_name(value: Any) -> str:
    if isinstance(value, bool):
        return "bool"
    if isinstance(value, int):
        return "int"
    if isinstance(value, float):
        return "float"
    if isinstance(value, list):
        return "list"
    return "string"
