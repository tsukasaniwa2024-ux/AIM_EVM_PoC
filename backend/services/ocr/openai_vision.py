import base64
import json
import os

from openai import OpenAI

from .base import OcrProvider


class OpenAIVisionOcr(OcrProvider):
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
この帳票画像から経理処理に必要な情報を抽出してください。
JSONのみ返す（説明文・マークダウン不要）。
数値はカンマ除去して数値型で返す。抽出できない項目はnull。

以下の形式で返してください：

{
  "basic_info": {
    "document_type": "COMMERCIAL INVOICE または PACKING LIST",
    "invoice_no": "...",
    "packing_no": "...",
    "date": "...",
    "shipper": "...",
    "consignee": "...",
    "vessel": "...",
    "departure_date": "...",
    "from": "...",
    "to": "...",
    "currency": "...",
    "terms_of_payment": "...",
    "country_of_origin": "...",
    "total_quantity": 数値,
    "total_amount": 数値,
    "total_box": 数値,
    "total_piece": 数値,
    "total_net_weight": 数値,
    "total_gross_weight": 数値,
    "total_volume_m3": 数値,
    "remark": "..."
  },
  "items": [
    {
      "item_no": "...",
      "description": "...",
      "hs_code": "...",
      "quantity": 数値,
      "unit_price": 数値,
      "amount": 数値,
      "quantity_box": 数値,
      "quantity_piece": 数値,
      "net_weight": 数値,
      "gross_weight": 数値,
      "volume_m3": 数値
    }
  ]
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
                            "image_url": {"url": f"data:{image_mime};base64,{encoded}"},
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
