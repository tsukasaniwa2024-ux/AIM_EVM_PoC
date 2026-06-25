import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./evm_import.db"
)

# SQLiteデータベースへ接続するためのエンジン
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# DB操作用セッション生成クラス
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# 全モデルの親クラス
Base = declarative_base()