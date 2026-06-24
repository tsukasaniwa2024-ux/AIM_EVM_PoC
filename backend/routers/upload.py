from fastapi import APIRouter, UploadFile, File


# Router作成
# APIエンドポイントをここに定義する
router = APIRouter()



# 帳票処理API
#
# 役割:
# ・PDF受信
# ・画像受信
# ・後続処理(B OCR / C 計算DB出力)へ渡す入口
#
# 現時点ではファイル受信確認のみ
@router.post("/process")
async def process(

    # PDF帳票ファイル
    pdf_file: UploadFile = File(...),

    # 画像帳票ファイル
    image_file: UploadFile = File(...)

):

    # ファイル内容取得
    # 後でOCR処理へ渡す
    pdf_bytes = await pdf_file.read()

    image_bytes = await image_file.read()


    # 現時点では受信確認のみ
    # B担当のOCR処理、
    # C担当の計算・DB保存処理をここへ追加する
    return {

        # 処理状態
        "status": "ok",

        # 受け取ったファイル名
        "pdf": pdf_file.filename,

        "image": image_file.filename,

        # サイズ確認用
        "pdf_size": len(pdf_bytes),

        "image_size": len(image_bytes)
    }