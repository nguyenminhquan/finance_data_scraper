from queue import Queue
from threading import Thread
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from convert import unicode_to_ascii
from html_to_list import table_to_list

class Scraper:
    def __init__(self):
        self.stockList = 'src/stock.txt'
        self.numberOfWorker = 10

    def setSrc(self, file_name):
        self.stockList = 'src/%s.txt' % file_name

    def exportCSV(self, table, name):
        with open('data/%s.csv' % name, 'w') as f:
            for row in table:
                f.write(','.join(row)+'\n')

class BaoViet(Scraper):

    def __init__(self):
        super().__init__()
        self.view = '1'
        self.report = '7'
        self.unit = '1000000'
        self.year = '2019'
        self.target = {}

    def setOptions(self, view, report, unit, year):
        self.view = view
        self.report = report
        self.unit = unit
        self.year = year

    def setTarget(self, target):
        self.target = target

    def parseTable(self, stock_symbol):
        key = 'Cart_ctl00_webPartManager_wp1629714544_wp1440203596_cbFinanceReport_Callback_Param'
        url = 'http://www.bvsc.com.vn/FinancialStatements.aspx'

        payload = [('SymbolList', stock_symbol), ('Symbol', stock_symbol),
                   (key, self.view), (key, self.report), (key, self.unit), (key, self.year)]

        r = requests.post(url, data=payload)

        # Processing Html document
        html_doc = unicode_to_ascii(str(r.text)).replace(',', '')
        html_doc = html_doc.strip('                    ]]></CallbackContent>')
        html_doc = html_doc.strip('<CallbackContent><![CDATA[')

        return table_to_list(html_doc)

    def dowork(self, symbol):

        dic = self.target.copy()
        try:
            lst = self.parseTable(symbol)

            for key in dic:
                dic[key] = list(lst[dic[key]])

            for key in dic:
                var = dic[key]
                for i in range(len(var)-1, 1, -1):
                    var.insert(i, lst[0][i])
                var.insert(0, symbol)
            print(symbol)
            return dic

        except BaseException as e:
            print(symbol, end=' - ')
            print(e)
            for k in dic:
                dic[k] = [symbol, 'N/A']
            return dic
    
    def startScraping(self):
        # Load stock list into the queue
        try:
            q = Queue()
            with open(self.stockList, 'r') as f:
                for line in f:
                    q.put(line.strip())
        except FileNotFoundError:
            print('%s is missing!' % self.stockList)
            raise SystemExit

        lst = []
        dic = {}

        def create_job():
            while True:
                item = q.get()
                lst.append(self.dowork(item))
                q.task_done()

        # Create jobs
        for _ in range(self.numberOfWorker):
            t = Thread(target=create_job)
            t.daemon = True
            t.start()

        q.join()

        print('Download finished')

        for k in lst[0].keys():
            dic[k] = list(dic[k] for dic in lst)

        for k in dic:
            print('Exporting to %s.csv' % k)
            self.exportCSV(dic[k], k)


class VietStock(Scraper):

    def __init__(self):
        super().__init__()
        self.pages = ['1']

    def setPages(self, pages):
        self.pages = pages

    def dowork(self, symbol):
        all_tables = []
        all_soups = []

        male_num = [symbol]
        female_num = [symbol]
        share = [symbol]
        hdqt = [symbol]

        for page in self.pages:
            try:
                url = 'http://finance.vietstock.vn/%s/%s/ban-lanh-dao.htm' % (
                    symbol, page)
                r = requests.get(url)
                # html_doc = unicode_to_ascii(str(r.text))
                soup = BeautifulSoup(r.text, 'html.parser')
                page_soups = soup.find_all('table', {'id': "table370"})
                all_soups += page_soups
            except:
                print('failed-'+symbol+'-'+page)

        for soup in all_soups:
            table = table_to_list(soup)
            sub_soup = soup.find('table')
            sub_table = table_to_list(sub_soup)

            valid_table = [table[1][0]]

            for row in sub_table:
                if row[4] == '':
                    valid_table.append([row[0], row[1], '0'])
                else:
                    valid_table.append([row[0], row[1], row[4].replace(',', '')])

            all_tables.append(valid_table)

        def getData(table):
            male_num = 0
            female_num = 0
            share_number = 0
            hdqt_number = 0

            date = table[0].replace('/', '-')
            # date = datetime.strptime(table[0], '%y/%d/%m')

            for row in table:
                if not isinstance(row, str):
                    if 'HĐQT' in row[1]:
                        share_number += int(row[2])

                # if 'Ông' in row[0] and 'HĐQT' in row[1]:
                #     male_num += 1
                # elif 'Bà' in row[0] and 'HĐQT' in row[1]:
                #     female_num += 1
                # else:
                #     pass
                if 'HĐQT' in row[1]:
                    hdqt_number += 1
              

            return date, str(share_number), str(male_num), str(female_num), str(hdqt_number)

        for table in all_tables:
            _date, _share_number, _male_num, _female_num, _hdqt_number = getData(table)
            male_num.append(_date)
            male_num.append(_male_num)

            female_num.append(_date)
            female_num.append(_female_num)

            share.append(_date)
            share.append(_share_number)

            hdqt.append(_date)
            hdqt.append(_hdqt_number)

        return male_num, female_num, share, hdqt


    def startScraping(self):

        # Load stock list into the queue
        try:
            q = Queue()
            with open(self.stockList, 'r') as f:
                for line in f:
                    q.put(line.strip())
        except FileNotFoundError:
            print('%s is missing!' % self.stockList)
            raise SystemExit

        male_num = []
        female_num = []
        share = []
        hdqt = []

        def create_job():
            while True:
                item = q.get()

                _male_num, _female_num, _share, _hdqt = self.dowork(item)

                male_num.append(_male_num)
                female_num.append(_female_num)
                share.append(_share)
                hdqt.append(_hdqt)

                print(item)
                q.task_done()

        # Create jobs
        for _ in range(self.numberOfWorker):
            t = Thread(target=create_job)
            t.daemon = True
            t.start()

        q.join()

        print('Exporting...')

        # with open('data/so_nam.csv', 'w') as f:
        #     for item in male_num:
        #         f.write(','.join(item)+'\n')

        # with open('data/so_nu.csv', 'w') as f:
        #     for item in female_num:
        #         f.write(','.join(item)+'\n')

        # with open('data/share.csv', 'w') as f:
        #     for item in share:
        #         f.write(','.join(item)+'\n')
        with open('data/so_tvhdqt.csv', 'w') as f:
            for item in hdqt:
                f.write(','.join(item)+'\n')

        print('Finished!')


class CafeF(Scraper):
    def __init__(self):
        super().__init__()
        self.target = []
        self.results = {}

    def setTarget(self, target):
        self.target = list(target)
        for var in target:
            self.results[var] = []

    def dowork(self, symbol):
        url = 'http://e.cafef.vn/fi.ashx'
        payload = {'symbol':symbol}
       
        while True:
            try:
                r = requests.get(url, params=payload)
                js = r.json()
                
                for var in self.target:
                    row = [symbol]
                    for item in js:
                        row.append(str(item['Year']))
                        row.append(str(item[var]))
                    self.results[var].append(row)
                return
            except:
                pass

    def startScraping(self):
        # Load stock list into the queue
        try:
            q = Queue()
            with open(self.stockList, 'r') as f:
                for line in f:
                    q.put(line.strip())
        except FileNotFoundError:
            print('%s is missing!' % self.stockList)
            raise SystemExit

        def create_job():
            while True:
                # global lst
                item = q.get()
                self.dowork(item)
                print(item)
                q.task_done()

        # Create jobs
        for _ in range(self.numberOfWorker):
            t = Thread(target=create_job)
            t.daemon = True
            t.start()

        q.join()

        print('Done')
    
    def export(self):
        for var in self.results:
            self.exportCSV(self.results[var], var)
