from colored import fg, bg, attr
import datetime as dt
import shutil
import glob
import csv
import json

class CreateHistoricalJson:
    def execute():
        print('%s%s 処理を開始します %s' % (fg('black'), bg('grey_93'), attr('reset')))
        CreateHistoricalJson.importCsv()
        print('%s%s 処理を完了しました %s' % (fg('black'), bg('green'), attr('reset')))

    def importCsv() -> list:
        csvList = glob.glob("csv/history/*.csv")
        if len(csvList) == 0:
            print('CSVファイルが存在しません')
        
        for csvFilePath in csvList:
            CreateHistoricalJson.readCsv(csvFilePath)

    def readCsv(csvFilePath: str) -> None:
        print(csvFilePath + 'を読み込んでいます')

        csvFile = open(csvFilePath, "r", encoding="utf-8")
        historicalEvents = csv.reader(csvFile, delimiter=",", doublequote=True, lineterminator="\r\n", quotechar='"', skipinitialspace=True)

        try: 
            historicalLEventList = []
            for historicalEvent in historicalEvents:
                # 自動タグ付与
                eventTags = CreateHistoricalJson.suggestTag(historicalEvent[1])
                eventObject = {
                    "year": historicalEvent[0], # 年月をYYYY-mmに統一（将来的に...）
                    "summary": historicalEvent[1],
                    "detail": None,
                    "tag": eventTags
                }
                historicalLEventList.append(eventObject)

            # Json出力
            CreateHistoricalJson.createJson(historicalLEventList)

            # csvを完了ファイルに移動
            shutil.move(csvFilePath, "csv/history/createdJson/")
        except:
            print('%s%s csvの読み込みに失敗しました。CSVの内容が正しい形式かどうか確認してください %s' % (fg('white'), bg('red'), attr('reset')))

    def suggestTag(historicalEvent) -> list:
        suggestionTags = []

        # 連想ワードリストを読み込む
        tagMasters = CreateHistoricalJson.readSuggestWordList()

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

    def createJson(historicalEventLists: list) -> None:
        fw = open('json/history/' + "test" + ".json",'w')
        json.dump(historicalEventLists,fw,indent=2, ensure_ascii=False)

#execute
CreateHistoricalJson.execute()