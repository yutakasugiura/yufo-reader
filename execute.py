import tabula
import re, os, glob, json, shutil, datetime

# pdf形式の有価証券報告書を、csvに変換する
def createFinancialCsv(closingYear, targetPage):
    fileName = closingYear[:4]
    path = 'yufo/' + closingYear
    data = readFinancialPdf(path + ".pdf", targetPage)
    # CSVが出力したい時
    data.to_csv('csv/' + fileName + ".csv", index=None)
    # 一時ファイルを出力
    data.to_json('json/tmp/' + fileName + ".json", force_ascii=False, orient='split')
    readFinancialJson(fileName)
    # 一時ファイルを削除
    # shutil.rmtree('json/tmp/')
    # os.mkdir('json/tmp')

def readFinancialPdf(path, targetPage):
    # 沿革読み取りの場合はFalse指定
    try:
        print(path + 'を読み込んでいます')
        dfs = tabula.read_pdf(path, lattice=False, pages=targetPage, encoding="utf-8")
        return dfs[0]
    except ZeroDivisionError as e:
        print('有価証券報告書のページの指定が正しくないか、読み込めないデータです')

# データをクレンジングしたJsonを出力する
def readFinancialJson(fileName):

    openJson = open('json/tmp/' + fileName + ".json", 'r')
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
            # 平成表記の西暦化
            if '平成' in formatByBar:
                formattedYear = convertYear(formatByBar)
            else:
                formattedYear = formatByBar
            # 臨時従業員数の除去
            formatByEmployee = formattedYear # TODO
            # int or float型に変換
            hasNumeric = is_num(formatByEmployee)
            if hasNumeric:
                formatLast = int(formatByEmployee)
                #単位変換
                formatLast
            else:
                formatLast = formatByEmployee     
            # 配列に格納
            if formatLast is not None:
                resultRecords.append(formatLast)

        result.append({'title' : header, 'data': resultRecords})

    #決算年月がない場合に推測取得
    hasYear = False
    for searchYears in result:
        if '決算' in searchYears['title']:
            hasYear = True
    if hasYear == False:
        for suggestYears in result:
            result.append({'title': '決算', 'data': suggestYears['data']})
            break
    
    fw = open('json/tmp/' + fileName + ".json",'w')
    json.dump(result,fw,indent=2, ensure_ascii=False)

    createJsonForShashi(result, fileName)

def convertYear(japaneseYear):
    # 年数を取得（ex平成20年X月期。なお平成一桁・令和昭和はないと仮定）
    termInfo = japaneseYear[4:]
    removeHeisei = japaneseYear[2:4]
    numericYear = int(removeHeisei)
    # 平成の西暦を計算
    year =  numericYear + 1988
    return str(year) + termInfo

# The社史向けに必要データを抽出
def createJsonForShashi(jsonData, fileName):
    result = []
    print('========json========')
    # print(jsonData)

    for data in jsonData:
        # print(data)
        if '営業収益' in data['title']:
            result.append({'title': data['title'], 'data': data['data']});
        if '売上' in data['title']:
            result.append({'title': data['title'], 'data': data['data']})
        if '利益' in data['title']:
            result.append({'title': data['title'], 'data': data['data']})
        if '従業員' in data['title']:
            result.append({'title': '従業員数', 'data': data['data']})
        if '決算' in data['title']:
            result.append({'title': 'closing_years', 'data': data['data']})
    fw = open('json/tmp_shashi/' + fileName + ".json",'w')
    json.dump(result,fw,indent=4, ensure_ascii=False)

def readManyData():
    files = glob.glob("yufo/*")
    sortedfiles = sorted(files, reverse=False)
    for file in sortedfiles:
        cutDirName = file.replace('yufo/' ,'')
        closingYear = cutDirName.replace('.pdf' ,'')
        readPage = closingYear.find('p')
        if readPage == 4:
            targetPage = closingYear[readPage+len('p'):]
            createFinancialCsv(closingYear, targetPage)
        else:
            createFinancialCsv(closingYear,'2')
    # jsonファイルのマージ        
    mergeJsonData()

# 複数ファイルのjsonを結合する
def mergeJsonData():
    files = glob.glob("json/tmp_shashi/*")
    sortedfiles = sorted(files, reverse=False)
    all = []
    for file in sortedfiles:
        openJson = open(file, 'r')
        data = json.load(openJson)
        all.append({'id': file, 'data': data})

    targetSignals = []
    for signalAll in all:
        for signal in signalAll['data']:
            targetSignals.append(signal['title'])

    uniqueSignals = list(set(targetSignals))

    result = []

    # 有報1枚単位に分割
    for records in all:
        # 存在する勘定科目を取得
        partSignals = []
        for record in records['data']:
            partSignals.append(record['title'])

        # 差分から存在しない勘定科目を取得
        undefinedSignals = list(set(uniqueSignals) - set(partSignals))
        if undefinedSignals is not None:
            # 存在しない勘定科目に、年度分のnullデータを格納
            
            length = len(records['data'][0]['data'])
            emptyLists = []
            for num in range(length):
                emptyLists.append('-')

            for undefinedSignal in undefinedSignals:
                records['data'].append({'title': undefinedSignal, 'data': emptyLists})

    for title in uniqueSignals:
        tmp = []
        for finalRecords in all:
            # 決算年月の配列格納数を取得
            for finalRecord in finalRecords['data']:
                if finalRecord['title'] == title:
                    tmp.append(finalRecord['data'])

        result.append({title: sum(tmp, [])})

    name = datetime.datetime.now().strftime('%Y-%m-%d_%H:%M') + '_created'
    fw = open('json/' + name + ".json",'w')
    json.dump(result,fw,indent=2, ensure_ascii=False)

    shutil.rmtree('json/tmp_shashi/')
    os.mkdir('json/tmp_shashi/')

# 負の値を数字判定する
def is_num(a):
    try:
        int(a)
    except:
        return False
    return True

# execute
readManyData()
