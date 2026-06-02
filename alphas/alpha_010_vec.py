#Alpha010: rank(((0 < ts_min(delta(close, 1), 4)) ? delta(close, 1) : ((ts_max(delta(close, 1), 4) < 0)? delta(close, 1) : (-1 * delta(close, 1)))))
import pandas as pd
import os
import numpy as np
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.time_series import  delta_vec

def alpha_010(full_df):
    """
    full_df: 长表，含 date, code, close。

    输出：df，包含所有日期的alpha_010的结果，数据不足的日子为nan
    """
    full_df = full_df.sort_values(['code', 'date']).copy()

    ts_m_days= 4
    delta_days= 1
    col = f'delta_close_{delta_days}'
    full_df[col]=delta_vec(full_df,day=delta_days,delta_colum='close')
    full_df['ts_min']= full_df.groupby('code')[col].transform(
        lambda x:x.rolling(window=ts_m_days,min_periods=ts_m_days).min()
    )
    full_df['ts_max']= full_df.groupby('code')[col].transform(
        lambda x:x.rolling(window=ts_m_days,min_periods=ts_m_days).max()
    )
    # 条件逻辑 — 一行 np.select 替代多层 if
    cond_all_pos = full_df['ts_min'] > 0  # 4 天 delta 全正
    cond_all_neg = full_df['ts_max'] < 0  # 4 天 delta 全负

    full_df['raw'] = np.select([cond_all_pos, cond_all_neg],
                            [full_df[col], full_df[col]],
                            default=-full_df[col]
                            )
    # 数据不足 ts_m_days 天的行，强制 NaN
    full_df.loc[full_df['ts_min'].isna(), 'raw'] = np.nan

    full_df['alpha_010'] = full_df.groupby('date')['raw'].rank(pct=True)
    return full_df.pivot(index='date', columns='code', values='alpha_010')
