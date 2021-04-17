import value_investing.analyze
import pandas as pd
from value_investing.parse import get_sector_filters
from value_investing.data_collect import collect_data, sector_data
from value_investing.export import export
from value_investing.dividend_aristocrats import dividend_tickers



def find_analyze(tickers, filters, sector_ratio_filters, custom, parallel):
    data = pd.DataFrame()

    # process inputs
    custom = [str(i) for i in custom]
    filters = filters.split(',')

    # sector data
    sector_df = sector_data()

    # screen each sector separately
    for sector_row in sector_df.iterrows():
        try:
            print(f"Sector: {sector_row[1]['Name']}")
            sec_filters = get_sector_filters(sector_row[1], sector_ratio_filters)
            sec_filters.extend(filters)
            sec_df = collect_data(filters=sec_filters, custom=custom, parallel=parallel)
            data = data.append(sec_df)
        except Exception as e:
            print(e)

    # add specific tickers if not already found
    if tickers:
        tickers = [t for t in tickers if t.upper() not in data['Ticker'].values]
    # get data for specific filters
    if tickers:
        print('Specific tickers')
        tic_df = collect_data(tickers=tickers, custom=custom, parallel=parallel)
        data = data.append(tic_df)

    # analyze
    analyzer = analyze.Analyzer(data)
    data = analyzer.score()

    export(data, method='csv', order_by='score')


if __name__ == '__main__':
    """
    tickers:
        specific tickers to add if the filter dont find them
    filters:
        fa_ltdebteq_u0.5: Long Term Debt/Equity < 0.5
        fa_roe_o15: Return on Equity > 15%
        fa_curratio_o2: Current Ratio > 2
        fa_div_pos: Dividend Yield > 0%
        fa_eps5years_o10: EPS growth past 5 years > 10%
    sector_ratio_filters:
        ['pe', 'ps']
    custom:
        columns number can be found in 
    """
    import time
    start_time = time.time()
    tickers = ['aapl', 'fb', 'tsla', 'momo', 'baba', 'stla']
    tickers.extend(dividend_tickers)
    filters = 'fa_ltdebteq_u0.8,fa_roe_o10,fa_curratio_o1'
    sector_ratio_filters = ['pe']
    custom = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 13, 14, 15, 16, 17, 18, 19, 20, 21, 26, 27, 31, 33,
              35, 36, 37, 38, 39, 40, 41, 55, 56, 57, 58, 62, 65, 67, 69]
    find_analyze(tickers, filters, sector_ratio_filters, custom, parallel=True)
    print("--- %s seconds ---" % (time.time() - start_time))
