from pydantic import BaseModel


# APIレスポンス形式
#
# 将来的にB/C担当の結果を返すための定義
class ProcessResult(BaseModel):

    # DB保存後のID
    record_id: int | None = None


    # 処理結果
    # ok / error など
    status: str


    # 補足メッセージ
    message: str | None = None