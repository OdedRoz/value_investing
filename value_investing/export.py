"""
export the created data
"""

from datetime import datetime
import pathlib
import os

def export(data, method='csv', order_by='score'):
    # clean index
    data = data.drop('No.', axis=1)
    data = data.reset_index(drop=True)

    # reorder columns
    first_cols = ['Ticker', 'Company', 'Sector', 'Industry', 'Country', 'Price',
                  'score', 'score recomm',
                  'Zacks rank', 'Zacks value score', 'Zacks growth score',
                  'GF Value', 'GF value score',
                  'Financial Strength', 'Profitability Rank', 'Valuation Rank',
                  'ROE', 'Curr R', 'LTDebt/Eq']

    data = data[first_cols + [col for col in data.columns if col not in first_cols]]

    if order_by:
        data = data.sort_values(by=order_by, ascending=False)

    if method == 'csv':
        # create folder if not exists
        output_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'output'))
        pathlib.Path(output_path).mkdir(parents=True, exist_ok=True)

        # csv file name
        now = datetime.now()
        date_time = now.strftime("%m-%d-%Y_%H-%M-%S")
        path = os.path.join(output_path, f'data_{date_time}.csv')
        print(path)

        # export
        data.to_csv(path, index=False)
