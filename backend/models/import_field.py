from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text

from db.database import Base


class ImportField(Base):
    """
    抽出結果・計算結果を保存するテーブル

    EAV(Entity Attribute Value)構造を採用し、
    フィールド追加時にテーブル変更が不要な設計
    """

    __tablename__ = "import_fields"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    # import_sessions.idとの関連
    session_id = Column(
        Integer,
        ForeignKey("import_sessions.id"),
        nullable=False
    )

    # 項目名
    key = Column(
        String(255),
        nullable=False
    )

    # 項目値
    value = Column(
        Text,
        nullable=True
    )

    # データ型情報
    value_type = Column(
        String(50),
        nullable=True
    )

    # 値の取得元 pdf / image / calculated
    source = Column(
        String(50),
        nullable=True
    )

    # 計算結果の場合の計算式
    formula = Column(
        Text,
        nullable=True
    )