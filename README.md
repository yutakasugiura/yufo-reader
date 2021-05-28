# yufo-reader
 - 有価証券報告書pdfをcsvとjsonに変換するツール
  
# 準備
 - yufoディレクトリに読み込みたい有価証券報告書をpdfで格納
 - 読み込みたい年度（数字4桁）+決算ページ（p+数字）
    - ex. yufo/2020p4.pdf 
    - 指定ページがない場合は、2ページ目を自動で読み込む

# 環境
 - python
 - pipenv（パッケージ管理）
 - java（ライブラリーのtabla実行）

# 実行方法
``
python execute.py
```
