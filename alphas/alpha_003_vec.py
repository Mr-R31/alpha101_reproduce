import pandas as pd
import numpy as np

#Alpha003: (-1 * correlation(rank(open), rank(volume), 10))
def alpha_003(full_df):
    """
    full_df: 长表，含 date, code, open, volume。

    输出：df，包含所有日期的alpha_003的结果，数据不足的日子为nan
    """

    full_df = full_df.sort_values(['code', 'date']).copy()

    cor_window=10

    full_df['rank_open']=full_df.groupby('date')['open'].transform (lambda x:
                                                           x.rank(pct=True))
    full_df['rank_volume'] = full_df.groupby('date')['volume'].transform (lambda x:
                                                                          x.rank(pct=True))
    corr_v=full_df.groupby('code')[['rank_open','rank_volume']].rolling(window=cor_window,min_periods=cor_window).corr()
    full_df['corr_v']=corr_v.unstack().loc[:,('rank_open','rank_volume')].droplevel(0)

    full_df['alpha_003']=full_df['corr_v']*-1

    return full_df.pivot(index='date', columns='code', values='alpha_003')
