from sqlalchemy.orm import Session

from models.import_session import ImportSession
from models.import_field import ImportField


def create_session(
    db: Session,
    pdf_filename: str | None = None,
    image_filename: str | None = None,
    merge_strategy: str | None = None,
    warnings: str | None = None,
) -> ImportSession:
    """
    import_sessions に1件登録する
    """

    session_record = ImportSession(
        pdf_filename=pdf_filename,
        image_filename=image_filename,
        merge_strategy=merge_strategy,
        warnings=warnings,
    )

    db.add(session_record)
    db.commit()
    db.refresh(session_record)

    return session_record


def save_field(
    db: Session,
    session_id: int,
    key: str,
    value: str | None,
    value_type: str | None = None,
    source: str | None = None,
    formula: str | None = None,
) -> ImportField:
    """
    import_fields に1件登録する
    """

    field_record = ImportField(
        session_id=session_id,
        key=key,
        value=value,
        value_type=value_type,
        source=source,
        formula=formula,
    )

    db.add(field_record)
    db.commit()
    db.refresh(field_record)

    return field_record


def save_fields(
    db: Session,
    session_id: int,
    fields: list[dict],
) -> None:
    """
    複数フィールドを一括保存する

    fields例:
    [
        {
            "key": "quantity",
            "value": "100",
            "value_type": "float",
            "source": "image"
        }
    ]
    """

    field_records = []

    for field in fields:
        field_records.append(
            ImportField(
                session_id=session_id,
                key=field.get("key"),
                value=str(field.get("value"))
                if field.get("value") is not None
                else None,
                value_type=field.get("value_type"),
                source=field.get("source"),
                formula=field.get("formula"),
            )
        )

    db.add_all(field_records)
    db.commit()


def get_session(
    db: Session,
    session_id: int,
) -> ImportSession | None:
    """
    セッション情報取得
    """

    return (
        db.query(ImportSession)
        .filter(ImportSession.id == session_id)
        .first()
    )


def get_fields_by_session(
    db: Session,
    session_id: int,
) -> list[ImportField]:
    """
    セッションに紐づくフィールド一覧取得
    """

    return (
        db.query(ImportField)
        .filter(ImportField.session_id == session_id)
        .all()
    )


def delete_session(
    db: Session,
    session_id: int,
) -> bool:
    """
    セッション削除
    """

    session_record = (
        db.query(ImportSession)
        .filter(ImportSession.id == session_id)
        .first()
    )

    if session_record is None:
        return False

    (
        db.query(ImportField)
        .filter(ImportField.session_id == session_id)
        .delete()
    )

    db.delete(session_record)
    db.commit()

    return True