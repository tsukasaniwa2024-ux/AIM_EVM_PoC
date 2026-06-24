# EVM 輸入帳票自動化システム

中国→日本 輸入業務における経理帳票の手作業処理を自動化するWebアプリケーションです。  
PDFおよび画像ファイルからOCRでデータを抽出し、計算処理を行ったうえでCSV・Excelへ出力します。

---

## 概要

| 項目 | 内容 |
|------|------|
| プロジェクト名 | EVM 輸入帳票自動化システム |
| 対象業務 | 中国→日本 輸入に関する経理帳票処理 |
| 開発形態 | グループ開発（GitHub管理） |
| 実行環境 | Docker（ローカル） |
| 本番環境（予定） | AIM社内イントラネット |

---

## 機能概要

1. **ファイルアップロード**：PDFファイル1件 + 画像ファイル1件をブラウザから指定
2. **OCR抽出**：各ファイルから必要な数値・テキストを自動抽出
3. **計算処理**：抽出データをもとに輸入コスト関連の計算を実施
4. **画面プレビュー**：計算結果をブラウザ上に表示
5. **ファイル出力**：CSV / Excel（.xlsx）形式でダウンロード
6. **DB保存**：処理結果をSQLite（開発）/ PostgreSQL（本番予定）に保存・蓄積

---

## 技術スタック

| レイヤー | 技術 |
|----------|------|
| フロントエンド | HTML / CSS / JavaScript（バニラ） |
| バックエンド | Python 3.11 / FastAPI |
| OCR | OCR API（未定、抽象化レイヤーで差し替え可能） |
| DB | SQLite（開発） / PostgreSQL（本番予定） |
| ORM | SQLAlchemy |
| 出力 | pandas / openpyxl |
| コンテナ | Docker / Docker Compose |

---

## ディレクトリ構成

```
evm-import-system/
├── docker-compose.yml
├── .env.example
├── README.md
├── docs/
│   ├── 要件定義書.docx
│   └── 基本設計書.docx
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── main.py                  # FastAPIエントリポイント
│   ├── routers/
│   │   └── upload.py            # アップロード・処理エンドポイント
│   ├── services/
│   │   ├── ocr/
│   │   │   ├── base.py          # OCR抽象基底クラス
│   │   │   └── google_vision.py # Google Cloud Vision実装（差し替え可能）
│   │   ├── extractor.py         # データ抽出・正規化
│   │   └── calculator.py        # 計算ロジック
│   ├── models/
│   │   └── import_record.py     # SQLAlchemyモデル
│   ├── schemas/
│   │   └── result.py            # Pydanticスキーマ
│   ├── db/
│   │   └── database.py          # DB接続設定
│   └── output/
│       └── exporter.py          # CSV / Excel出力
└── frontend/
    ├── index.html
    ├── style.css
    └── app.js
```

---

## セットアップ・起動手順

### 前提条件

- Docker Desktop がインストールされていること
- OCR API キーが取得済みであること

### 1. リポジトリのクローン

```bash
git clone https://github.com/<your-org>/evm-import-system.git
cd evm-import-system
```

### 2. 環境変数の設定

```bash
cp .env.example .env
# .env を編集して OCR_API_KEY などを設定
```

`.env.example` の内容：

```
OCR_API_KEY=your_api_key_here
OCR_PROVIDER=google_vision   # google_vision | aws_textract | azure
DATABASE_URL=sqlite:///./evm_import.db
```

### 3. Dockerで起動

```bash
docker-compose up --build
```

### 4. ブラウザでアクセス

```
http://localhost:8000
```

---

## 使い方

1. ブラウザで `http://localhost:8000` を開く
2. **「PDFファイルを選択」** ボタンでPDF帳票を1件選択
3. **「画像ファイルを選択」** ボタンで画像帳票を1件選択
4. **「OCR解析・計算実行」** ボタンをクリック
5. 画面下部に計算結果のプレビューが表示される
6. **「CSVで出力」** または **「Excelで出力」** ボタンでファイルをダウンロード

---

## OCR差し替えについて

`backend/services/ocr/base.py` に抽象基底クラス `OcrProvider` が定義されています。  
新しいOCRプロバイダを追加する場合は `base.py` を継承したクラスを作成し、  
`.env` の `OCR_PROVIDER` を変更するだけで切り替えられます。

```python
# base.py
class OcrProvider(ABC):
    @abstractmethod
    def extract_text(self, file_bytes: bytes, mime_type: str) -> str:
        ...
```

---

## ブランチ運用（Git）

| ブランチ | 用途 |
|----------|------|
| `main` | リリース済み・動作確認済みコード |
| `develop` | 統合開発ブランチ |
| `feature/<名前>` | 各機能の開発ブランチ |

プルリクエストは `feature/*` → `develop` へ。  
動作確認後に `develop` → `main` へマージします。

---

## 開発メンバー・担当

| 担当 | 領域 |
|------|------|
| （メンバー名） | バックエンド / OCR |
| （メンバー名） | フロントエンド |
| （メンバー名） | DB / 出力処理 |
| （メンバー名） | ドキュメント / テスト |

---

## ライセンス

社内利用限定 / AIM株式会社
