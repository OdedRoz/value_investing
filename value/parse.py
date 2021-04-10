"""
parse strings for needed patterns
"""

import math


def get_sector_filters(data, ratio_filters=None):
    results = []
    if not ratio_filters:
        return results
    sector_name = data['Name']
    sector_name = sector_name.lower().replace(' ', '')
    results.append(f'sec_{sector_name}')
    if 'pe' in ratio_filters:
        sector_pe = data['P/E']
        pe_limit = round_up(sector_pe, 5)
        results.append(f'fa_pe_u{pe_limit}')
    if 'ps' in ratio_filters:
        sector_ps = data['P/S']
        ps_limit = round_up(sector_ps, 1)
        results.append(f'fa_ps_u{ps_limit}')
    return results


def round_up(x, base=5):
    return int(base * math.ceil(x / base))
