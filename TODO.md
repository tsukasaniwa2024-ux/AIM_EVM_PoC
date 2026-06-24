# 作業TODO

> 完了したらチェックを入れる（`- [ ]` → `- [x]`）  
> 担当が決まったら名前を記入する

---

## 1. Docker環境・プロジェクト雛形

- [ ] `docker-compose.yml` 作成
- [ ] `backend/Dockerfile` 作成
- [ ] `backend/requirements.txt` 作成
- [ ] `backend/main.py` 最小構成（FastAPI起動確認）
- [ ] `.env.example` 作成
- [ ] `.gitignore` 作成
- [ ] `docker-compose up --build` で全員起動確認

---

## 2. バックエンド実装

### OCR
- [ ] `services/ocr/base.py`（抽象基底クラス）
- [ ] `services/ocr/mock.py`（開発用モック）
- [ ] `services/ocr/google_vision.py`（APIキー確定後）

### 抽出
- [ ] `config/extraction.yml`（抽出フィールド定義）
- [ ] `services/extractor.py`（YAMLを読んで動的抽出）

### 計算
- [ ] `services/calculator.py`（計算ロジック）

### DB
- [ ] `db/database.py`（SQLite接続設定）
- [ ] `models/import_session.py`（セッションテーブル）
- [ ] `models/import_field.py`（key-valueテーブル）

### 出力
- [ ] `output/exporter.py`（CSV / Excel出力）

### API
- [ ] `routers/upload.py`（`POST /api/process`）
- [ ] `routers/upload.py`（`GET /api/export/csv/{id}`）
- [ ] `routers/upload.py`（`GET /api/export/excel/{id}`）

---

## 3. フロントエンド実装

- [ ] `frontend/index.html`（画面レイアウト）
- [ ] `frontend/style.css`（スタイル）
- [ ] `frontend/app.js`（ファイル選択・API呼び出し・プレビュー表示・ダウンロード）

---

## 4. 結合・動作確認

- [ ] `docker-compose up --build` で起動できる
- [ ] PDF・画像を選択して実行できる
- [ ] 抽出結果が抽出元付きでプレビューに表示される
- [ ] 重複フィールドがマージ戦略に従って処理される
- [ ] CSVファイルがダウンロードできる
- [ ] Excelファイルがダウンロードできる
- [ ] DBにレコードが保存されている

---

## 5. GitHub最終提出

- [ ] developブランチをmainにマージ
- [ ] READMEの担当者欄を記入
- [ ] 不要ブランチの削除
- [ ] 動作確認済みをチームで確認

---

## メモ

- OCR APIキーは別途共有予定（$20枠）
- APIキー確定までは `OCR_PROVIDER=mock` で開発を進める
- ブランチ運用: `feature/*` → `develop` → `main`
