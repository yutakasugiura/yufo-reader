import tabula
import re, os, glob, json

# pdf形式の有価証券報告書を、csvに変換する
def createFinancialCsv(closingYear, targetPage):
    fileName = closingYear[:4]
    path = 'yufo/' + closingYear
    data = readFinancialPdf(path + ".pdf", targetPage)
    # CSVが出力したい時
    data.to_csv('csv/' + fileName + ".csv", index=None)
    # 一時ファイルを出力
    data.to_json('yufo/' + fileName + "_tmp.json", force_ascii=False, orient='split')
    readFinancialJson(fileName)
    # 一時ファイルを削除
    os.remove('yufo/' + fileName + "_tmp.json")

def readFinancialPdf(path, targetPage):
    # 沿革読み取りの場合はFalse指定
    dfs = tabula.read_pdf(path, lattice=False, pages = targetPage, encoding="utf-8")
    return dfs[0]

# データをクレンジングしたJsonを出力する
def readFinancialJson(fileName):

    openJson = open('yufo/' + fileName + "_tmp.json", 'r')
    financialAll = json.load(openJson)
    result = []
    # レコードの処理
    for records in financialAll['data']:
        if (records[0] is None):
            header = 'undefined'
        else:
            header = re.sub(r"[(百千万円名人%\r,△・)]", "", records[0])
        records.pop(0)

        # 業績数値のクレンジング
        resultRecords = []
        # カラムの処理
        for record in records:
            if record is None:
                record = 'undefined'
            # space削除
            formatBySpace = record.replace(' ' ,'')
            # ３桁区切りカンマの除去
            formatByFirst = formatBySpace.replace(',' ,'')
            # マイナス表記
            formatBySecond = formatByFirst.replace('△' ,'-')
            formatByBar = re.sub('-－﹣−‐⁃‑‒–—﹘―⎯⏤ーｰ─━' ,'-', formatBySecond)
            # 臨時従業員数の除去
            formatByEmployee = formatByBar # TODO
            # int or float型に変換
            hasNumeric = is_num(formatByEmployee)
            if hasNumeric:
                formatLast = int(formatByEmployee)
            else:
                formatLast = formatByEmployee     
            # 配列に格納
            if formatLast is not None:
                resultRecords.append(formatLast)

        result.append({header: resultRecords})

    fw = open('json/' + fileName + ".json",'w')
    json.dump(result,fw,indent=4, ensure_ascii=False)

def readManyData():
    files = glob.glob("yufo/*")
    for file in files:
        cutDirName = file.replace('yufo/' ,'')
        closingYear = cutDirName.replace('.pdf' ,'')
        readPage = closingYear.find('p')
        if readPage == 4:
            targetPage = closingYear[readPage+len('p'):]
            createFinancialCsv(closingYear, targetPage)
        else:
            createFinancialCsv(closingYear,'2')

# 複数のjsonを統合
def mergeJsonList():
    files = glob.glob("json/*")
    for file in files:
            

# 負の値を数字判定する
def is_num(a):
    try:
        int(a)
    except:
        return False
    return True

# execute
# createFinancialCsv('2020','4')
readManyData()