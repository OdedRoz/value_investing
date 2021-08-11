"""
this module gets all the data the main process needs from 3rd party's
"""

from value_investing import scrape as scrape
from finviz.screener import Screener
from finvizfinance.group.valuation import Valuation
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import reduce


def collect_ticker_data(ticker):
    # GF
    gf_scraper = scrape.GFScraper()
    gf_ticker_df = gf_scraper.scrape(ticker)

    # Zacks
    zacks_scraper = scrape.ZacksScraper()
    zacks_rank = zacks_scraper.rank(ticker)
    zacks_ticker_df = pd.DataFrame({'Ticker': [ticker], **zacks_rank})

    # quickfs
    quickfs_scraper = scrape.QuickFSScraper()
    quickfs_ticker_df = quickfs_scraper.get_data(ticker)

    df = reduce(lambda left, right: pd.merge(left, right, on='Ticker'), [gf_ticker_df, zacks_ticker_df, quickfs_ticker_df])
    return df



def collect_data(tickers=None, filters=None, custom=None, parallel=True):
    stocks = Screener(tickers=tickers, filters=filters, order='Ticker', custom=custom)
    df = pd.DataFrame(stocks.data)

    # data frame for all of the collected scrped data
    scrape_df = pd.DataFrame()
    # for faster concat df
    dict_list = []
    if parallel:
        with ThreadPoolExecutor() as pool:
            futures = []
            for ticker in df['Ticker'].values:
                futures.append(pool.submit(collect_ticker_data, ticker))

            for f in as_completed(futures):
                ticker_df = f.result()
                dict_list.extend(ticker_df.to_dict('records'))
            scrape_df = pd.DataFrame.from_dict(dict_list)

    else:
        count = 1
        total = len(df)
        for ticker in df['Ticker'].values:

            ticker_df = collect_ticker_data(ticker)
            scrape_df = scrape_df.append(ticker_df)

            print(f'scraped {count}/{total} tickers')
            count += 1


    # marge df
    df = pd.merge(df, scrape_df, on='Ticker')
    #df = pd.merge(df, zack_df, on='Ticker')
    return df


def sector_data():
    valuation = Valuation()
    return valuation.ScreenerView(group='Sector')
