import traceback

class Analyzer:
    def __init__(self, df):
        """

        :param df:
        :param bounds: (min/max, value, %/#, importance)
        """
        self.df = df
        self.bounds = {
            #TODO change bounds to be per indestry
            'Dividend': ('min', 1, '%', 1),
            'Payout Ratio': [('min', 10, '%', 1),
                             ('min', 90, '%', -1)],
            'EPS': ('min', 2, '#', 1),
            'EPS this Y': ('min', 5, '%', 1),
            'EPS past 5Y': ('min', 25, '%', 1),
            'PEG': [('max', 2, '#', 1),
                    ('max', 1, '#', 1)],
            'P/S': ('max', 1, '#', 1),
            'Insider Own': ('min', 10, '%', 1),
            'Short Ratio': [('max', 3, '#', 1),
                            ('min', 10, '%', -2)],  # we dont want a lot of short on the company
            'Curr R': ('min', 2, '#', 1),
            'Quick R': ('min', 1.5, '#', 1),
            'ROE': ('min', 15, '%', 2),
            'LTDebt/Eq': ('max', 0.5, '#', 2),
            'Gross M': ('min', 25, '%', 1),
            'Oper M': ('min', 10, '%', 1),
            'Profit M': ('min', 10, '%', 1),
            'Recom': ('max', 2, '#', 1),
            'Cash-To-Debt': ('min', 2, '#', 1),
            'Piotroski F-Score': ('min', 7, '#', 1),
            'Altman Z-Score': ('min', 3, '#', 1),
            'Beneish M-Score': ('max', 2.5, '#', 1),
            'ROC (Joel Greenblatt) %': ('min', 50, '#', 1),
            'Price-to-Intrinsic-Value-Projected-FCF': ('max', 1, '#', 1),
            'Price-to-Median-PS-Value': ('max', 1, '#', 1),
            'Price-to-Graham-Number': ('max', 1, '#', 2),
            'Forward Rate of Return (Yacktman) %': ('min', 10, '#', 1),
            '52W High': [(max, -10, '%', 2),
                         (max, -20, '%', 2),
                         (max, -30, '%', 2)],
            '50D High': (max, -20, '%', 2),
            'EV-to-EBITDA': ('max', 10, '#', 1),
            'EV-to-EBIT': ('max', 8, '#', 1),
            'EV-to-Revenue': ('max', 5, '#', 1),
        }

    def score(self):
        """
        :param df: pandas Dataframe with stocks data
        :return: df with added columns of score per stock
        """
        self.df['score'] = 0

        # generic score using self.bounds

        for col, bounds in self.bounds.items():
            try:
                if type(bounds) is list:
                    for b in bounds:
                        min, max, percentage, importance = self.process_bounds(b)
                        filtered_df = self.filter(col, min=min, max=max, percentage=percentage)
                        self.point_by_index(filtered_df, importance)
                else:
                    min, max, percentage, importance = self.process_bounds(bounds)
                    filtered_df = self.filter(col, min=min, max=max, percentage=percentage)
                    self.point_by_index(filtered_df, importance)
            except Exception as e:
                print(traceback.format_exc())
                print(e)
                print(f'error in col {col}')



        # special score
        self._gf_value()

        #  scroe with analyst recommendation
        self._score_analyst_recom()

        return self.df

    def _score_analyst_recom(self):
        self.df['score recomm'] = self.df['score']
        # Zacks rank, Zacks value score, Zacks growth score
        self._zacks_score()
        # Financial Strength, Profitability Rank, Valuation Rank, GF value score
        self._gf_score()





    def filter(self, col, min=None, max=None, percentage=False):
        """
        filter rows based in condition
        :param col:
        :param min:
        :param max:
        :param percentage:
        :return: filtered pandas Dataframe
        """
        # clean rows with out data
        col_df = self.df.loc[self.df[col] != '-', [col]]
        col_df.dropna()


        if percentage:
            col_df[col] = col_df[col].str.rstrip('%').astype('float')
        else:
            col_df[col] = col_df[col].astype('float')
        if min:
            col_df = col_df.loc[col_df[col] >= min]
        if max:
            col_df = col_df.loc[col_df[col] <= max]
        return col_df

    def point_by_index(self, index_df, importance):
        """
        add score to df for row with index which are in index_df
        :param index_df: df with good index
        :return: None
        """
        self.df.loc[self.df.index.intersection(index_df.index), 'score'] += importance

    def _zacks_score(self):
        """
        add to score 5 - Zacks rank (1 is best)
        :return:
        """
        self.df.loc[self.df['Zacks rank'].notna(), 'score recomm'] += 5 - self.df.loc[self.df['Zacks rank'].notna(), 'Zacks rank']
        for matric in ['Zacks value score', 'Zacks growth score']:
            self.df[matric] = self._char_to_int(self.df[matric])
            self.df.loc[self.df[matric].notna(), 'score recomm'] += 6 - self.df.loc[self.df[matric].notna(), matric]



    def _gf_score(self):
        """
        add Financial Strength, Profitability Rank, Valuation Rank to scroe
        :return:
        """
        for matric in ['Financial Strength', 'Profitability Rank', 'Valuation Rank', 'GF value score']:
            self.df.loc[self.df[matric].notna(), 'score recomm'] += self.df.loc[self.df[matric].notna(), matric]

    def _gf_value(self):
        # Fairly Valued or none
        self.df['GF value score'] = 0

        # Overvalued
        self.df.loc[self.df['GF Value'] >= 1.5, 'GF value score'] = -5
        self.df.loc[(self.df['GF Value'] >= 1.4) & (self.df['GF Value'] < 1.5), 'GF value score'] = -4
        self.df.loc[(self.df['GF Value'] >= 1.3) & (self.df['GF Value'] < 1.4), 'GF value score'] = -3
        self.df.loc[(self.df['GF Value'] >= 1.2) & (self.df['GF Value'] < 1.3), 'GF value score'] = -2
        self.df.loc[(self.df['GF Value'] >= 1.1) & (self.df['GF Value'] < 1.2), 'GF value score'] = -1

        # Undervalue(d)
        self.df.loc[(self.df['GF Value'] <= 0.9) & (self.df['GF Value'] > 0.8), 'GF value score'] = 1
        self.df.loc[(self.df['GF Value'] <= 0.8) & (self.df['GF Value'] > 0.7), 'GF value score'] = 2
        self.df.loc[(self.df['GF Value'] <= 0.7) & (self.df['GF Value'] > 0.6), 'GF value score'] = 3
        self.df.loc[(self.df['GF Value'] <= 0.6) & (self.df['GF Value'] > 0.5), 'GF value score'] = 4
        # GF Value of 0 is an error
        self.df.loc[(self.df['GF Value'] <= 0.5) & (self.df['GF Value'] > 0.0), 'GF value score'] = 5

    @staticmethod
    def _char_to_int(x):
        """
        map A to 1, B to 2, ect..
        :param x: iterable of chars
        :return: list
        """
        excepted = ['A', 'B', 'C', 'D', 'E', 'F']
        return [int(ord(c) - 64) if c in excepted else None for c in x]


#x = self.df['Zacks value score']


    @staticmethod
    def process_bounds(bounds):
        if bounds[0] == 'min':
            min = bounds[1]
            max = None
        else:
            min = None
            max = bounds[1]
        if bounds[2] == '%':
            percentage = True
        else:
            percentage = False
        importance = bounds[3]
        return min, max, percentage, importance


