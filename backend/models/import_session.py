from datetime import datetime

from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text

from db.database import Base


class ImportSession(Base):
    """
    OCR処理1回分を管理するテーブル

    PDF・画像ファイルの組み合わせを
    1つの処理単位(Session)として保存する
    """
    
    __tablename__ = "import_sessions"

    # セッションID
    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    # 処理日時
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    # アップロードされたPDFファイル名
    pdf_filename = Column(
        String(255),
        nullable=True
    )

    # アップロードされた画像ファイル名
    image_filename = Column(
        String(255),
        nullable=True
    )

    # 使用したマージ戦略
    merge_strategy = Column(
        String(50),
        nullable=True
    )

    # 抽出失敗などの警告メッセージ
    warnings = Column(
        Text,
        nullable=True
    )