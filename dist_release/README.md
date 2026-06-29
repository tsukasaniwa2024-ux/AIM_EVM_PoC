# dist_release（配布用フォルダ）

このフォルダのファイルをユーザーに渡してください。

## 配布ファイル

```
EVM_Import_Tool.exe   ← exe_build\build.batでビルド後にここに配置
.env.example          ← .envにリネームしてAPIキーを設定
取扱説明書.md         ← ユーザー向け取扱説明書
```

## ビルド手順

1. `exe_build\build.bat` を実行
2. 生成された `exe_build\dist\EVM_Import_Tool.exe` をこのフォルダにコピー
3. 3ファイルをまとめてユーザーに配布
