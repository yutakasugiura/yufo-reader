import tabula
from colored import fg, bg, attr
import re, os, glob, json, shutil, datetime

class ReadFinancialPdf:

    PDF_DIR = 'yufo/'
    CSV_DIR = 'csv/'
    PDF_EXTENTION = '.pdf'
    CSV_EXTENTION = '.csv'

    def execute(self) -> list:
        # 処理準備
        companyName = ReadFinancialPdf.inputCompanyName()

        # 本番処理
        print('%s%s 処理を開始します %s' % (fg('black'), bg('grey_93'), attr('reset')))
        financialPdfList = ReadFinancialPdf.importPdf(self)
        financialObject = ReadFinancialPdf.createFinancialData(self, financialPdfList, companyName)
        print('%s%s 処理を完了しました %s' % (fg('black'), bg('green'), attr('reset')))

    def inputCompanyName() -> str:
        print('企業名or証券コードを入力してください')
        companyName = input('> ')
        if companyName == '':
            return 'undefined_'
        return companyName + '_'
 
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
            financialDataObject = ReadFinancialPdf.readPdf(self, pdf)
            ReadFinancialPdf.createCsv(self, financialDataObject, companyName + str(pdf['closingYear']))
            
    def readPdf(self, financialPdf: object) -> object:
        print(financialPdf['closingYear'] + ': 読み込みを開始します')
        try:
            dfs = tabula.read_pdf(financialPdf['path'], lattice=False, pages=financialPdf['targetPage'], encoding="utf-8")
            print(financialPdf['closingYear'] + ': 読み込みに成功しました')
            return dfs[0]
        except:
            print('%s%s pdfの読み込みに失敗しました。ページ指定を見直してください %s' % (fg('white'), bg('red'), attr('reset')))

    def createCsv(self, financialDataObject: object, fileName: str) -> None:
        try:
            financialDataObject.to_csv(self.CSV_DIR + fileName + self.CSV_EXTENTION, index=None)
            print(fileName + ': csvの作成を完了しました')
        except:
            print('%s%s csvの作成に失敗しました。ページ指定を見直してください %s' % (fg('white'), bg('red'), attr('reset')))

                

# execute
ReadFinancialPdf().execute()