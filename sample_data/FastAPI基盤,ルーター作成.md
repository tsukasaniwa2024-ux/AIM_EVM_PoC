# 実装内容

FastAPI基盤＋ルーター作成

## 実施内容

### 1. FastAPIアプリケーション基盤作成

* FastAPIアプリを作成
* APIサーバー起動用の `main.py` を作成
* アプリケーション名・バージョンを設定
* ルーターを登録する仕組みを実装

### 2. APIルーター作成

* `routers/upload.py` を作成
* 帳票処理用APIエンドポイントを追加

作成API:

```
POST /api/process
```

役割:

* PDFファイル受信
* 画像ファイル受信
* 後続処理（OCR・抽出・計算処理）へ渡す入口を作成

### 3. ファイルアップロード処理実装

* FastAPIの `UploadFile` を使用
* multipart/form-data形式でファイル受信可能にした

対応ファイル:

* PDF帳票
* 画像帳票

### 4. APIレスポンス形式作成

* `schemas/result.py` を作成
* APIレスポンスの基本形式を定義

管理項目:

* 処理状態
* レコードID
* メッセージ

### 5. Docker起動対応

* FastAPI起動に必要な依存ライブラリを定義

使用ライブラリ:

* fastapi
* uvicorn
* python-multipart

### 6. 動作確認環境作成

確認可能:

```
GET /
```

結果:

```
EVM Import System API
```

また、

```
POST /api/process
```

でPDF・画像アップロード確認可能。

---

## 担当の成果

完成した流れ:

ブラウザ
↓
PDF / 画像アップロード
↓
FastAPI
↓
uploadルーター
↓
B担当 OCR処理
↓
C担当 計算・DB・CSV/Excel出力


