from typing import Any


MERGE_STRATEGY = "pdf_first"  # pdf_first | image_first | both


def merge(pdf_data: dict, image_data: dict, strategy: str = MERGE_STRATEGY) -> list[dict]:
    """
    PDFと画像から抽出したデータをマージしてフィールドリストを返す。

    戻り値:
    [
        {"key": "item_name", "value": "Laptop", "source": "pdf"},
        {"key": "quantity",  "value": 10,       "source": "image"},
        ...
    ]
    """
    all_keys = set(pdf_data.keys()) | set(image_data.keys())
    fields = []

    for key in sorted(all_keys):
        in_pdf = key in pdf_data
        in_image = key in image_data

        if in_pdf and in_image:
            # 両方に存在する場合はマージ戦略に従う
            if strategy == "pdf_first":
                fields.append(_make_field(key, pdf_data[key], "pdf（重複）"))
            elif strategy == "image_first":
                fields.append(_make_field(key, image_data[key], "image（重複）"))
            elif strategy == "both":
                fields.append(_make_field(f"{key}_pdf", pdf_data[key], "pdf"))
                fields.append(_make_field(f"{key}_image", image_data[key], "image"))
        elif in_pdf:
            fields.append(_make_field(key, pdf_data[key], "pdf"))
        else:
            fields.append(_make_field(key, image_data[key], "image"))

    return fields


def _make_field(key: str, value: Any, source: str) -> dict:
    return {
        "key": key,
        "value": value,
        "source": source,
        "value_type": _type_name(value),
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
