# yufo-reader
 - 有価証券報告書pdfをcsvに変換するツール
   1. from pdf to csv
   2. formatted csv (手動でデータ整形すること)
   3. from csv to json
# 準備
 - yufoディレクトリに読み込みたい有価証券報告書をpdfで格納
 - 読み込みたい年度（数字4桁）+決算ページ（p+数字）
    - ex. yufo/2020p4.pdf 
    - 指定ページがない場合は、2ページ目を自動で読み込む

# 環境
 - python 3.9.5
 - java 15.0.2
 - pipenv 2010.11.15

# 実行方法
```
Domainディレクトリのファイルを実行
python Domain/CreateRawFinancialData.py
python Domain/CreateRawHistoricalData.py
python Domain/CreateHistoricalJson.py
```
