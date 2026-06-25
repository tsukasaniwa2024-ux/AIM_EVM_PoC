from pathlib import Path

import pandas as pd
from sqlalchemy.orm import Session

from db.crud import get_fields_by_session


def export_csv(
    db: Session,
    record_id: int,
    output_path: str,
    items: list[dict] = [],
) -> str:
    fields = get_fields_by_session(db=db, session_id=record_id)

    # 基礎情報（value_type・formulaは除外）
    basic_rows = [
        {"項目名": f.key, "値": f.value, "抽出元": f.source}
        for f in fields
    ]

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8-sig", newline="") as fp:
        # 基礎情報セクション
        df_basic = pd.DataFrame(basic_rows)
        fp.write("【基礎情報】\n")
        df_basic.to_csv(fp, index=False)

        if items:
            fp.write("\n【品目明細】\n")
            df_items = pd.DataFrame(items)
            df_items.to_csv(fp, index=False)

    return output_path


def export_excel(
    db: Session,
    record_id: int,
    output_path: str,
    items: list[dict] = [],
) -> str:
    fields = get_fields_by_session(db=db, session_id=record_id)

    basic_rows = [
        {"項目名": f.key, "値": f.value, "抽出元": f.source}
        for f in fields
    ]

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        # 基礎情報シート
        df_basic = pd.DataFrame(basic_rows)
        df_basic.to_excel(writer, sheet_name="基礎情報", index=False)

        # 品目明細シート
        if items:
            df_items = pd.DataFrame(items)
            df_items.to_excel(writer, sheet_name="品目明細", index=False)

    return output_path
