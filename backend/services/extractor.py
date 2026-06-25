from typing import Any

MERGE_STRATEGY = "pdf_first"


def merge(pdf_data: dict, image_data: dict, strategy: str = MERGE_STRATEGY) -> dict:
    """
    PDFと画像から抽出したデータをマージして返す。
    戻り値:
    {
        "basic_info": [...],  # 基礎情報フィールドリスト
        "items": [...]        # 品目明細リスト
    }
    """
    pdf_basic = pdf_data.get("basic_info", {})
    image_basic = image_data.get("basic_info", {})
    pdf_items = pdf_data.get("items", [])
    image_items = image_data.get("items", [])

    # 基礎情報をマージ
    basic_info = _merge_dict(pdf_basic, image_basic, strategy)

    # 品目はPDF優先、なければ画像を使用
    items = pdf_items if pdf_items else image_items

    return {
        "basic_info": basic_info,
        "items": items,
    }


def _merge_dict(pdf_dict: dict, image_dict: dict, strategy: str) -> list[dict]:
    all_keys = set(pdf_dict.keys()) | set(image_dict.keys())
    fields = []

    for key in sorted(all_keys):
        pdf_val = pdf_dict.get(key)
        image_val = image_dict.get(key)
        in_pdf = key in pdf_dict
        in_image = key in image_dict

        if in_pdf and in_image:
            value = pdf_val if pdf_val is not None else image_val
            source = "pdf（重複）"
        elif in_pdf:
            value = pdf_val
            source = "pdf"
        else:
            value = image_val
            source = "image"

        if value is None:
            continue

        fields.append({
            "key": key,
            "value": value,
            "source": source,
            "value_type": _type_name(value),
        })

    return fields


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
