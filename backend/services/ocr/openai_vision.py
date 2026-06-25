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
        if mime_type == "application/pdf":
            image_bytes, image_mime = self._pdf_to_image(file_bytes)
        else:
            image_bytes, image_mime = file_bytes, mime_type

        encoded = base64.b64encode(image_bytes).decode("utf-8")

        prompt = """
この帳票画像から経理処理に必要な情報のみを抽出してください。

## 抽出ルール
- JSONのみ返す（説明文・マークダウン不要）
- キー名は英語のスネークケース
- 数値は数値型で返す（カンマ区切りは除去）
- 抽出できない項目はnullにする

## COMMERCIAL INVOICE の場合、以下を抽出
{
  "document_type": "COMMERCIAL INVOICE",
  "invoice_no": "...",
  "date": "...",
  "shipper": "...",
  "consignee": "...",
  "items": [
    {
      "item_no": "...",
      "description": "...",
      "hs_code": "...",
      "quantity": 数値,
      "unit_price": 数値,
      "amount": 数値
    }
  ],
  "total_quantity": 数値,
  "total_amount": 数値,
  "currency": "...",
  "terms_of_payment": "...",
  "remark": "..."
}

## PACKING LIST の場合、以下を抽出
{
  "document_type": "PACKING LIST",
  "packing_no": "...",
  "date": "...",
  "shipper": "...",
  "consignee": "...",
  "items": [
    {
      "pkg_no": 数値,
      "item_no": "...",
      "description": "...",
      "quantity_box": 数値,
      "quantity_piece": 数値,
      "net_weight": 数値,
      "gross_weight": 数値,
      "volume_m3": 数値
    }
  ],
  "total_box": 数値,
  "total_piece": 数値,
  "total_net_weight": 数値,
  "total_gross_weight": 数値,
  "total_volume_m3": 数値,
  "country_of_origin": "...",
  "marks_no": "...",
  "remark": "..."
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

        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]

        return json.loads(raw)

    def _pdf_to_image(self, pdf_bytes: bytes) -> tuple[bytes, str]:
        import io
        from pdf2image import convert_from_bytes

        images = convert_from_bytes(pdf_bytes, first_page=1, last_page=1, dpi=200)
        buf = io.BytesIO()
        images[0].save(buf, format="PNG")
        return buf.getvalue(), "image/png"
