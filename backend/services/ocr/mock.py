from .base import OcrProvider


class MockOcr(OcrProvider):
    """APIキーなしで開発・テストするためのモックOCR"""

    def extract(self, file_bytes: bytes, mime_type: str) -> dict:
        # PDFと画像で少し違うダミーデータを返す（重複テスト用）
        if mime_type == "application/pdf":
            return {
                "invoice_no": "IV-250414",
                "date": "2025/04/15",
                "item_name": "Laptop",
                "quantity": 5,
                "unit_price": 100000.0,
                "amount": 500000.0,
                "currency": "USD",
            }
        else:
            return {
                "packing_no": "PL-250414",
                "date": "2025/04/15",
                "item_name": "Laptop",
                "quantity": 10,
                "net_weight": 50.0,
                "gross_weight": 51.0,
                "volume": 0.60,
            }
