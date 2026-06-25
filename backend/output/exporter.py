from pathlib import Path

import pandas as pd
from sqlalchemy.orm import Session

from db.crud import get_fields_by_session


def export_csv(
    db: Session,
    record_id: int,
    output_path: str,
) -> str:
    """
    record_idからDBのデータを取得しCSV出力する

    Parameters
    ----------
    db : Session
        DBセッション

    record_id : int
        import_sessions.id

    output_path : str
        出力先パス

    Returns
    -------
    str
        出力ファイルパス
    """

    fields = get_fields_by_session(
        db=db,
        session_id=record_id,
    )

    rows = []

    for field in fields:
        rows.append(
            {
                "key": field.key,
                "value": field.value,
                "value_type": field.value_type,
                "source": field.source,
                "formula": field.formula,
            }
        )

    df = pd.DataFrame(rows)

    Path(output_path).parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    # Excelで文字化けしないようBOM付きUTF-8で出力
    df.to_csv(
        output_path,
        index=False,
        encoding="utf-8-sig",
    )

    return output_path


def export_excel(
    db: Session,
    record_id: int,
    output_path: str,
) -> str:
    """
    record_idからDBのデータを取得しExcel出力する

    Parameters
    ----------
    db : Session
        DBセッション

    record_id : int
        import_sessions.id

    output_path : str
        出力先パス

    Returns
    -------
    str
        出力ファイルパス
    """

    fields = get_fields_by_session(
        db=db,
        session_id=record_id,
    )

    rows = []

    for field in fields:
        rows.append(
            {
                "key": field.key,
                "value": field.value,
                "value_type": field.value_type,
                "source": field.source,
                "formula": field.formula,
            }
        )

    df = pd.DataFrame(rows)

    Path(output_path).parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    # openpyxlを利用してxlsx出力
    df.to_excel(
        output_path,
        index=False,
        engine="openpyxl",
    )

    return output_path