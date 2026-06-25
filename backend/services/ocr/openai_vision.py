import base64
import json
import os

from openai import OpenAI

from .base import OcrProvider


class OpenAIVisionOcr(OcrProvider):
    """OpenAI GPT-4oを使ったOCRプロバイダ"""

    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OCR_API_KEY"))
        self.model = "gpt-4o"

    def extract(self, file_bytes: bytes, mime_type: str) -> dict:
        """
        画像またはPDFからデータを抽出する。
        PDFは先頭ページを画像に変換してから送信する。
        """
        if mime_type == "application/pdf":
            image_bytes, image_mime = self._pdf_to_image(file_bytes)
        else:
            image_bytes, image_mime = file_bytes, mime_type

        encoded = base64.b64encode(image_bytes).decode("utf-8")

        prompt = """
この帳票画像からすべての情報を抽出してください。
以下のルールに従ってJSON形式のみで返してください。

ルール:
- キー名は英語のスネークケース（例: item_name, unit_price）
- 数値は文字列ではなく数値型で返す
- 日付は文字列のままでOK
- 複数の明細行がある場合は items キーにリスト形式で格納する
- 抽出できなかった項目はnullにする
- JSONのみ返す（説明文・マークダウン不要）

出力例:
{
  "document_type": "COMMERCIAL INVOICE",
  "invoice_no": "IV-250414",
  "date": "2025/04/15",
  "shipper": "Sample Shipper Co.,Ltd",
  "consignee": "Sample Consignee Co.,Ltd",
  "items": [
    {
      "item_no": "A001",
      "description": "Laptop",
      "quantity": 5,
      "unit_price": 100000.0,
      "amount": 500000.0
    }
  ],
  "total_quantity": 15,
  "total_amount": 1500000.0,
  "currency": "USD"
}
"""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{image_mime};base64,{encoded}"
                            },
                        },
                        {"type": "text", "text": prompt},
                    ],
                }
            ],
            max_tokens=2000,
        )

        raw = response.choices[0].message.content.strip()

        # マークダウンのコードブロックが含まれる場合は除去
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]

        return json.loads(raw)

    def _pdf_to_image(self, pdf_bytes: bytes) -> tuple[bytes, str]:
        """PDFの先頭ページをPNG画像に変換する"""
        import io
        from pdf2image import convert_from_bytes

        images = convert_from_bytes(pdf_bytes, first_page=1, last_page=1, dpi=200)
        buf = io.BytesIO()
        images[0].save(buf, format="PNG")
        return buf.getvalue(), "image/png"
