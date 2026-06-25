import os
from abc import ABC, abstractmethod


class OcrProvider(ABC):
    @abstractmethod
    def extract(self, file_bytes: bytes, mime_type: str) -> dict:
        """
        ファイルバイト列からデータを抽出してdictで返す。
        戻り値例:
        {
            "item_name": "Laptop",
            "quantity": 10,
            "unit_price": 100000.0,
            ...
        }
        """
        ...


def get_ocr_provider() -> OcrProvider:
    """OCR_PROVIDER環境変数に応じてプロバイダを返すファクトリ関数"""
    provider = os.getenv("OCR_PROVIDER", "mock")
    if provider == "mock":
        from .mock import MockOcr
        return MockOcr()
    elif provider == "openai":
        from .openai_vision import OpenAIVisionOcr
        return OpenAIVisionOcr()
    raise ValueError(f"Unknown OCR provider: {provider}")
