import requests
from bs4 import BeautifulSoup
import pandas as pd
from user_agent import generate_user_agent


class GFScraper:
    def __init__(self):
        self.columns = ['Ticker', 'Cash-To-Debt', 'Equity-to-Asset', 'Debt-to-Equity',
       'Debt-to-EBITDA', 'Interest Coverage', 'Piotroski F-Score',
       'Altman Z-Score', 'Beneish M-Score',
       'Operating Margin %', 'Net Margin %', 'ROE %', 'ROA %',
       'ROC (Joel Greenblatt) %', '3-Year Revenue Growth Rate',
       '3-Year EBITDA Growth Rate', '3-Year EPS without NRI Growth Rate',
       'Price-to-Owner-Earnings',
       'PB Ratio', 'PS Ratio', 'Price-to-Free-Cash-Flow',
       'Price-to-Operating-Cash-Flow', 'EV-to-EBIT', 'EV-to-EBITDA',
       'EV-to-Revenue', 'PEG Ratio', 'Shiller PE Ratio', 'Current Ratio',
       'Quick Ratio', 'Days Inventory', 'Days Sales Outstanding',
       'Days Payable', 'Dividend Yield %', 'Dividend Payout Ratio',
       '3-Year Dividend Growth Rate', 'Forward Dividend Yield %',
       '5-Year Yield-on-Cost %', '3-Year Average Share Buyback Ratio',
       'Price-to-Tangible-Book', 'Price-to-Intrinsic-Value-Projected-FCF',
       'Price-to-Median-PS-Value', 'Price-to-Graham-Number',
       'Earnings Yield (Greenblatt) %', 'Forward Rate of Return (Yacktman) %']

    def gf_scrape(self, ticker):
        # summary page scrape

        df = pd.DataFrame({'Ticker':[ticker]})
        df = self._summery_scrape(df, ticker)
        df = self._gf_value_scrape(df, ticker)
        return df


    def _summery_scrape(self, df, ticker):
        url = f'https://www.gurufocus.com/stock/{ticker}/summary'
        page = requests.get(url)
        soup = BeautifulSoup(page.content, 'html.parser')
        stock_indicator_tables = soup.findAll('table', {'class': 'stock-indicator-table'})
        for table in stock_indicator_tables:
            list_table = tableDataText(table)[1:]
            data = {l[0]: [l[1]] for l in list_table}
            df = pd.concat([df, pd.DataFrame(data)], axis=1)
        # get all wanted columns that actually exists
        df = df[df.columns.intersection(self.columns)]
        # Cash-To-Debt special value
        if 'Cash-To-Debt' in df.columns:
            if 'No Debt' in df['Cash-To-Debt'].values:
                df.loc[df['Cash-To-Debt'] == 'No Debt', 'Cash-To-Debt'] = 10

        header_tables = soup.findAll('table', {'class': 'header-table'})
        for table in header_tables:
            try:
                list_table = tableDataText(table)[0]
                if '/10' in list_table[1]:
                    df[list_table[0]] = int(list_table[1].split('/')[0])
            except Exception as e:
                print(e)
                continue
        return df

    def _gf_value_scrape(self, df, ticker):
        try:
            url = f'https://www.gurufocus.com/term/gf_value/{ticker}/GF-Value'
            page = requests.get(url)
            soup = BeautifulSoup(page.content, 'html.parser')
            strongs = soup.findAll("strong")
            gf_value = None
            if len(strongs) >= 7:
                if strongs[7].text:
                    gf_value = float(strongs[7].text)
        except Exception as e:
            print(e)
            gf_value = None
        df['GF Value'] = gf_value
        return df






class ZacksScraper:
    def __init__(self):
        self.header = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:32.0) Gecko/20100101 Firefox/32.0'}

    def rank(self, ticker):
        """
        get Zacks rank, Value score, Growth score
        :param ticker:
        :return: dict
        """
        results = {'Zacks rank' : None,
                   'Zacks value score': None,
                   'Zacks growth score': None}
        url = f'https://www.zacks.com/stock/research/{ticker}/all-news/zacks'
        page = requests.get(url, headers=self.header)
        soup = BeautifulSoup(page.text, 'html.parser')
        rank = soup.select_one('.rank_view')
        if not rank:
            return results
        rank = rank.text.strip()[:5]
        # Still rank empty..
        if not rank:
            return results
        results['Zacks rank'] = int(rank[0])
        rank_views = soup.find_all('p', {'class': 'rank_view'})
        if len(rank_views) >= 1:
            styles = rank_views[1]
            results['Zacks value score'] = styles.contents[1].text
            results['Zacks growth score'] = styles.contents[5].text
        return results







def tableDataText(table):
    """Parses a html segment started with tag <table> followed
    by multiple <tr> (table rows) and inner <td> (table data) tags.
    It returns a list of rows with inner columns.
    Accepts only one <th> (table header/data) in the first row.
    """

    def rowgetDataText(tr, coltag='td'):  # td (data) or th (header)
        return [td.get_text(strip=True) for td in tr.find_all(coltag)]

    rows = []
    trs = table.find_all('tr')
    headerow = rowgetDataText(trs[0], 'th')
    if headerow:  # if there is a header row include first
        rows.append(headerow)
        trs = trs[1:]
    for tr in trs:  # for every table row
        rows.append(rowgetDataText(tr, 'td'))  # data row
    return rows
