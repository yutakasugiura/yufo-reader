from colored import fg, bg, attr
import shutil
import glob
import csv
import json
import os

class CreateHistoricalJson:

    CSV_DIR = 'csv/history/'
    JSON_DIR = 'json/history/'
    CREATED_DIR = 'csv/history/createdJson/'

    def execute(self):
        print('%s%s 処理を開始します %s' % (fg('black'), bg('grey_93'), attr('reset')))
        CreateHistoricalJson.importCsv(self)
        print('%s%s 処理を完了しました %s' % (fg('black'), bg('green'), attr('reset')))

    def importCsv(self) -> list:
        csvList = glob.glob(self.CSV_DIR + "*.csv")
        if len(csvList) == 0:
            print('CSVファイルが存在しません')
        
        for csvFilePath in csvList:
            stockCodeHasPage = os.path.split(csvFilePath)[1]
            stockCode = int(stockCodeHasPage[:4])

            CreateHistoricalJson.readCsv(self, csvFilePath, stockCode)

    def readCsv(self, csvFilePath: str, stockCode: int) -> None:
        print('証券コード' + str(stockCode) + 'を読み込んでいます')

        csvFile = open(csvFilePath, "r", encoding="utf-8")
        historicalEvents = csv.reader(csvFile, delimiter=",", doublequote=True, lineterminator="\r\n", quotechar='"', skipinitialspace=True)

        try: 
            historicalLEventList = []
            for count, historicalEvent in enumerate(historicalEvents):
                # 自動タグ付与
                eventTags = CreateHistoricalJson.suggestTag(historicalEvent[1], count)
                # 年月をYYYY/MM or YYYYに変換 （これは使わない方向でいく）
                # if '月' in historicalEvent[0]:
                #     formattedYear = historicalEvent[0].replace('年', '/')
                #     formattedDate = formattedYear.replace('月', '')
                # else:
                #     formattedYear = historicalEvent[0].replace('年', '')
                
                eventObject = {
                    "year": historicalEvent[0], # 年月をYYYY-mmに統一（将来的に...）
                    "summary": historicalEvent[1],
                    "detail": None,
                    "tag": eventTags
                }
                historicalLEventList.append(eventObject)

            # Json出力（数字4桁の証券コードで出力）
            CreateHistoricalJson.createJson(self, historicalLEventList, stockCode)

            # csvを完了ファイルに移動
            shutil.move(csvFilePath, self.CREATED_DIR)
        except:
            print('%s%s csvの読み込みに失敗しました。CSVの内容が正しい形式かどうか確認してください %s' % (fg('white'), bg('red'), attr('reset')))

    def suggestTag(historicalEvent, count: int) -> list:
        suggestionTags = []

        # 連想ワードリストを読み込む
        tagMasters = CreateHistoricalJson.readSuggestWordList()

        # タグの特殊処理 沿革の最初は必ず「創業」のみとする
        if count == 0:
            suggestionTags.append('創業')
        else:
            for tagMaster in tagMasters:
                if tagMaster['word'] in historicalEvent:
                    suggestionTags.append(tagMaster['tag'])

        #重複タグを解消して返却
        return list(set(suggestionTags))

    # 自動タグ付与機能（追加したいときはcsvにかいてね）
    # csvの書き方（０行目=含むか検査したい文字列, １行目=付与するタグ） 
    # ex. 設立, 関係会社設立
    def readSuggestWordList() -> list:
        fileName = 'suggestTag.csv'
        csvFile = open("Domain/tool/" + fileName, "r", encoding="utf-8")
        suggestTags = csv.reader(csvFile, delimiter=",", doublequote=True, lineterminator="\r\n", quotechar='"', skipinitialspace=True)

        suggestTagList = []
        for suggestTag in suggestTags:
            eventObject = {
                "word": suggestTag[0],
                "tag": suggestTag[1],
            }
            suggestTagList.append(eventObject)

        return suggestTagList

    def createJson(self, historicalEventLists: list, stockCode: int) -> None:
        fw = open(self.JSON_DIR + str(stockCode) + ".json",'w')
        json.dump(historicalEventLists,fw,indent=2, ensure_ascii=False)

#execute
CreateHistoricalJson().execute()