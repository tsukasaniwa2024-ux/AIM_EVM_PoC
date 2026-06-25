from typing import Any


def merge(pdf_data: dict, image_data: dict, strategy: str = "pdf_first") -> dict:
    """
    PDFと画像から抽出したデータをマージして返す。
    - 両方にあるキー → PDF優先で1行、source: pdf（重複）
    - PDFにしかないキー → source: pdf
    - 画像にしかないキー → source: image
    """
    pdf_basic = pdf_data.get("basic_info", {})
    image_basic = image_data.get("basic_info", {})
    pdf_items = pdf_data.get("items", [])
    image_items = image_data.get("items", [])

    basic_info = []
    all_keys = list(pdf_basic.keys()) + [k for k in image_basic.keys() if k not in pdf_basic]

    for key in all_keys:
        in_pdf = key in pdf_basic
        in_image = key in image_basic
        pdf_val = pdf_basic.get(key)
        image_val = image_basic.get(key)

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

        basic_info.append({
            "key": key,
            "value": value,
            "source": source,
            "value_type": _type_name(value),
        })

    # 品目をitem_noでマージ
    items = _merge_items(pdf_items, image_items)

    return {
        "basic_info": basic_info,
        "items": items,
    }


def _merge_items(pdf_items: list, image_items: list) -> list:
    """
    item_noをキーにPDFと画像の品目情報をマージする。
    同じitem_noがあれば両方の情報を合体（PDF優先）。
    """
    # image_itemsをitem_noでインデックス化
    image_map = {}
    for item in image_items:
        key = item.get("item_no") or item.get("pkg_no") or str(image_items.index(item))
        image_map[str(key)] = item

    merged = []
    used_image_keys = set()

    for pdf_item in pdf_items:
        key = str(pdf_item.get("item_no") or pdf_items.index(pdf_item))
        image_item = image_map.get(key, {})
        used_image_keys.add(key)

        # 画像のフィールドをPDFにマージ（PDFにないフィールドを追加）
        merged_item = dict(pdf_item)
        for k, v in image_item.items():
            if k not in merged_item or merged_item[k] is None:
                merged_item[k] = v

        merged.append(merged_item)

    # PDFにない画像のみの品目を追加
    for k, v in image_map.items():
        if k not in used_image_keys:
            merged.append(v)

    return merged


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
