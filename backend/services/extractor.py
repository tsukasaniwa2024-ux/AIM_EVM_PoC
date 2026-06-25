from typing import Any

MERGE_STRATEGY = "pdf_first"


def merge(pdf_data: dict, image_data: dict, strategy: str = MERGE_STRATEGY) -> list[dict]:
    """
    PDFと画像から抽出したデータをマージしてフィールドリストを返す。
    - itemsリストは展開して個別フィールドとして扱う
    - nullフィールドは除外する
    """
    # itemsを展開してフラットなdictに変換
    pdf_flat = _flatten(pdf_data, "pdf")
    image_flat = _flatten(image_data, "image")

    all_keys = set(pdf_flat.keys()) | set(image_flat.keys())
    fields = []

    for key in sorted(all_keys):
        in_pdf = key in pdf_flat
        in_image = key in image_flat

        pdf_val = pdf_flat.get(key)
        image_val = image_flat.get(key)

        if in_pdf and in_image:
            if strategy == "pdf_first":
                value = pdf_val if pdf_val is not None else image_val
                source = "pdf（重複）"
            elif strategy == "image_first":
                value = image_val if image_val is not None else pdf_val
                source = "image（重複）"
            else:
                value = pdf_val
                source = "pdf（重複）"
        elif in_pdf:
            value = pdf_val
            source = "pdf"
        else:
            value = image_val
            source = "image"

        # nullは除外
        if value is None:
            continue

        fields.append({
            "key": key,
            "value": value,
            "source": source,
            "value_type": _type_name(value),
        })

    return fields


def _flatten(data: dict, source: str) -> dict:
    """
    ネストされたdictをフラットに展開する。
    itemsリストは items_0_key, items_1_key 形式に展開。
    """
    result = {}

    for key, value in data.items():
        if key == "items" and isinstance(value, list):
            for i, item in enumerate(value):
                if isinstance(item, dict):
                    for sub_key, sub_val in item.items():
                        result[f"item_{i+1}_{sub_key}"] = sub_val
        else:
            result[key] = value

    return result


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
