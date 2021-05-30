import tabula
from colored import fg, bg, attr
import glob, os

# 読み込むためのファイル命名ルール（history/about.md）
class CreateRawHistoricalData:

    PDF_DIR = 'yufo/history/'
    CSV_DIR = 'csv/history/'
    PDF_EXTENTION = '.pdf'
    CSV_EXTENTION = '.csv'

    def __init__ (self) -> None:
        # csv格納ディレクトリの生成
        dir = self.CSV_DIR
        if not os.path.exists(dir):
            os.mkdir(dir)

    def execute(self) -> list:
        # 処理実行
        print('%s%s 処理を開始します %s' % (fg('black'), bg('grey_93'), attr('reset')))
        financialPdfList = CreateRawHistoricalData.importPdf(self)

        # CSV出力（JSON対応したい場合は下記に記載すること）
        CreateRawHistoricalData.createFinancialData(self, financialPdfList)

        print('%s%s 処理を完了しました %s' % (fg('black'), bg('green'), attr('reset')))
 
    # 沿革が複数ページにおよぶ可能性を考慮してインポート
    # ex 7203p7-8.pdf
    def importPdf(self) -> list:
        pdfList = glob.glob(self.PDF_DIR + '*.pdf')
        financialPdfList = []
        for pdf in pdfList:
            removeExtention = pdf.replace(self.PDF_EXTENTION, '')
            removedFileName = removeExtention.replace(self.PDF_DIR, '')
            # 複数ページの場合（p7-8）
            readPages = []
            if '-' in removedFileName:
                firstPageIndex = removedFileName.find('p')
                lastPageIndex = removedFileName.find('-')

                firstPage = int(removedFileName[firstPageIndex + 1:lastPageIndex])         
                lastPage = int(removedFileName[lastPageIndex + 1:])
                readPages = list(range(firstPage, lastPage + 1, 1))
            else:
                readPages = [removedFileName[5:]]

            # コードが冗長になるので連続した2ページのみ対応（いつか改修せねば）
            financialPdfList.append({
                 'stockCode': removedFileName[:4],
                 'readPages': readPages,
                 'path': pdf
            })
        return financialPdfList
    
    def createFinancialData(self, financialPdfList: list) -> list:
        for pdf in financialPdfList:
            for page in pdf['readPages']:
                financialDataObject = CreateRawHistoricalData.readPdf(self, pdf, page)
                CreateRawHistoricalData.createCsv(self, financialDataObject, pdf['stockCode'], page)
            
    def readPdf(self, financialPdf: object, page: int) -> object:
        print(financialPdf['stockCode'] + ': 読み込みを開始します')
        try:
            dfs = tabula.read_pdf(financialPdf['path'], lattice=False, pages=str(page), encoding="utf-8")
            print(financialPdf['stockCode'] + ': 読み込みに成功しました')
            return dfs[0]
        except:
            print('%s%s pdfの読み込みに失敗しました。ページ指定を見直してください %s' % (fg('white'), bg('red'), attr('reset')))

    def createCsv(self, financialDataObject: object, fileName: str, page: int) -> None:
        dir = self.CSV_DIR
        try:
            dir = self.CSV_DIR
            financialDataObject.to_csv(dir + '/' + fileName + 'p' + str(page) + self.CSV_EXTENTION, index=None)
            print(fileName + ': csvの作成を完了しました')
        except:
            print('%s%s csvの作成に失敗しました。ページ指定を見直してください %s' % (fg('white'), bg('red'), attr('reset')))

# execute
CreateRawHistoricalData().execute()