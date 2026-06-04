#Alpha009: ((0 < ts_min(delta(close, 1), 5)) ? delta(close, 1) : ((ts_max(delta(close, 1), 5) < 0) ?delta(close, 1) : (-1 * delta(close, 1))))
import pandas as pd
import numpy as np
from utils.time_series import delta_vec
def alpha_009(full_df):
    """
    full_df: 长表，含 date, code, close。
    这个是单股票因子
    输出：df，包含所有日期的alpha_009的结果，数据不足的日子为nan
    """


    ts_m_days= 5
    delta_days=1
    # 构建日期索引字典
    date_index_dic = {}
    full_df = full_df.sort_values(['code', 'date']).copy()

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

    full_df['alpha_009'] = np.select([cond_all_pos, cond_all_neg],
                            [full_df[col], full_df[col]],
                            default=-full_df[col]
                            )
    # 数据不足 ts_m_days 天的行，强制 NaN
    full_df.loc[full_df['ts_min'].isna(), 'alpha_009'] = np.nan

    return full_df.pivot(index='date', columns='code', values='alpha_009')