#Alpha008: (-1 * rank(((sum(open, 5) * sum(returns, 5)) - delay((sum(open, 5) * sum(returns, 5)),10))))
import pandas as pd
import numpy as np
from utils.calculators import   returns_calculator
def alpha_008(full_df):
    """
    full_df: 长表，含 date, code,open,close。

    输出：df，包含所有日期的alpha_008的结果，数据不足的日子为nan
    """
    full_df = full_df.sort_values(['code', 'date']).copy()

    sum_days= 5
    delay_days=10

    open_col=f'open_{sum_days}_sum'
    delay_col=f'delay_{delay_days}_minus'
    return_col=f'return_{sum_days}'
    full_df = returns_calculator(full_df)
    full_df[open_col]=full_df.groupby('code')['open'].transform(
        lambda x:x.rolling(window=sum_days,min_periods=sum_days).sum()
    )
    full_df[return_col] = full_df.groupby('code')['returns'].transform(
        lambda x:x.rolling(window=sum_days,min_periods=sum_days).sum()
    )
    full_df['prod'] = full_df[open_col] * full_df[return_col]

    full_df[delay_col] = full_df.groupby('code')['prod'].diff(delay_days)


    # 数据不足 sum_days+delay_days 天的行，强制 NaN
    full_df.loc[full_df.groupby('code')['date'].cumcount() < sum_days + delay_days - 1, delay_col] = np.nan

    r = full_df.groupby('date')[delay_col].rank(method='average')
    n = full_df.groupby('date')[delay_col].transform('count')
    full_df['alpha_008'] = -1 * (r - 1) / (n - 1)

    return full_df.pivot(index='date', columns='code', values='alpha_008')
