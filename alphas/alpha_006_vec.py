import pandas as pd
import numpy as np



#Alpha006: (-1 * correlation(open, volume, 10))
def alpha_006(full_df):

    """
    full_df: 长表，含 date, code, open,volume。

    输出：df，包含所有日期的alpha_006的结果，数据不足的日子为nan
    """
    full_df = full_df.sort_values(['code', 'date']).copy()

    correlation_day = 10

    cor_m=full_df.groupby('code')[['open','volume']].rolling(window=correlation_day,min_periods=correlation_day).corr()
    full_df['raw']=cor_m.unstack().loc[:,('open','volume')].droplevel(0)
    full_df['alpha_006']=-1*full_df['raw']


    return full_df.pivot(index='date', columns='code', values='alpha_006')

