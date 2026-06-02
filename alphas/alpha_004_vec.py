import pandas as pd
import numpy as np
#(-1 * Ts_Rank(rank(low), 9))
def alpha_004(full_df):
    """
    full_df: 长表，含 date, code, low。

    输出：df，包含所有日期的alpha_004的结果，数据不足的日子为nan
    """

    full_df = full_df.sort_values(['code', 'date']).copy()

    rolling_window=9
    full_df['rank_low']=full_df.groupby('date')['low'].rank(pct=True)
    ts_rank=full_df.groupby('code')['rank_low'].rolling(window=rolling_window,min_periods=rolling_window).rank(pct=True)
    full_df['ts_rank']=ts_rank.reset_index(level=0, drop=True)
    full_df['alpha_004']=-1*full_df['ts_rank']

    # 数据不足 rolling_window 天的行，强制 NaN
    full_df.loc[full_df['ts_rank'].isna(), 'alpha_004'] = np.nan


    return full_df.pivot(index='date', columns='code', values='alpha_004')
