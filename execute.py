from colored import fg, bg, attr

class Execute:

    def execute():
        print('実行する処理を数字で入力してください')
        print('==========')
        print('1: 有価証券報告書pdfから財務サマリの読み込み')
        print('2: 有価証券報告書pdfから沿革データの読み込み')

        select = int(input('半角数字>> '))
        if select == 1:
            print(1)
        if select == 2:
            print(2)





# execute
Execute.execute()