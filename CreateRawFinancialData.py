import tabula
from colored import fg, bg, attr
import glob, os

class CreateRawFinancialData:

    PDF_DIR = 'yufo/financial/'
    CSV_DIR = 'csv/financial/'
    PDF_EXTENTION = '.pdf'
    CSV_EXTENTION = '.csv'

    def execute(self) -> list:
        # 処理準備
        companyName = CreateRawFinancialData.inputCompanyName(self)
        # 処理実行
        print('%s%s 処理を開始します %s' % (fg('black'), bg('grey_93'), attr('reset')))
        financialPdfList = CreateRawFinancialData.importPdf(self)

        # CSV出力（JSON対応したい場合は下記に記載すること）
        CreateRawFinancialData.createFinancialData(self, financialPdfList, companyName)

        print('%s%s 処理を完了しました %s' % (fg('black'), bg('green'), attr('reset')))

    def inputCompanyName(self) -> str:
        print('企業名or証券コードを入力してください')
        companyName = input('> ')

        if companyName == '':
            companyName =  'undefined'
        
        # csv格納ディレクトリの生成
        dir = self.CSV_DIR + companyName + '/'
        print(dir)
        if not os.path.exists(dir):
            os.mkdir(dir)
        
        return companyName
 
    def importPdf(self) -> list:
        pdfList = glob.glob(self.PDF_DIR + '*.pdf')
        financialPdfList = []
        for pdf in pdfList:
            # ex. yufo/2020p5.pdf: 5ページ目を読み込む
            removeExtention = pdf.replace(self.PDF_EXTENTION, '')
            removeDir = removeExtention.replace(self.PDF_DIR, '')

            financialPdfList.append({
                 'closingYear': removeDir[:4],
                 'targetPage': removeDir[5:],
                 'path': pdf
            })
        return financialPdfList
    
    def createFinancialData(self, financialPdfList: list, companyName: str) -> list:
        for pdf in financialPdfList:
            financialDataObject = CreateRawFinancialData.readPdf(self, pdf)
            CreateRawFinancialData.createCsv(self, financialDataObject, companyName, pdf['closingYear'])
            
    def readPdf(self, financialPdf: object) -> object:
        print(financialPdf['closingYear'] + ': 読み込みを開始します')
        try:
            dfs = tabula.read_pdf(financialPdf['path'], lattice=False, pages=financialPdf['targetPage'], encoding="utf-8")
            print(financialPdf['closingYear'] + ': 読み込みに成功しました')
            return dfs[0]
        except:
            print('%s%s pdfの読み込みに失敗しました。ページ指定を見直してください %s' % (fg('white'), bg('red'), attr('reset')))

    def createCsv(self, financialDataObject: object, dirName: str, fileName: str) -> None:
        try:
            dir = self.CSV_DIR + '/' + dirName
            financialDataObject.to_csv(dir + '/' + fileName + self.CSV_EXTENTION, index=None)
            print(fileName + ': csvの作成を完了しました')
        except:
            print('%s%s csvの作成に失敗しました。ページ指定を見直してください %s' % (fg('white'), bg('red'), attr('reset')))

# execute
CreateRawFinancialData().execute()