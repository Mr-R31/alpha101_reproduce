import pandas as pd
import os
import numpy as np
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.calculators import   vwap_calculator
#(rank((open - (sum(vwap, 10) / 10))) * (-1 * abs(rank((close - vwap)))))
def alpha_005(full_df):
    """
    full_df: 长表，含 date, code, close, high, close, low 。

    输出：df，包含所有日期的alpha_005的结果，数据不足的日子为nan
    """

    full_df = full_df.sort_values(['code', 'date']).copy()

    vwap_type='d'
    rolling_window=10
    div_col=f'vwap_mean_{rolling_window}'
    x_col='var_x'
    y_col='var_y'
    rank_col='cl_vw_rank'
    #求vwap

    full_df = vwap_calculator(full_df,data_type=vwap_type,roll_window=rolling_window)

    #open-sum(vwap, 10) / 10
    #rank((open - (sum(vwap, 10) / 10))
    full_df['rank_var'] = full_df['open'] - full_df[div_col]
    full_df[x_col]=full_df.groupby('date')['rank_var'].rank(pct=True)

    #rank((close - vwap))
    full_df[rank_col]=(full_df['close']-full_df['vwap'])

    full_df[y_col] = -1*abs(full_df.groupby('date')[rank_col].rank(pct=True))



    full_df['alpha_005']=full_df[x_col]*full_df[y_col]
    # 数据不足 rolling_window 天的行，强制 NaN
    full_df.loc[full_df[div_col].isna(), 'alpha_005'] = np.nan

    return full_df.pivot(index='date', columns='code', values='alpha_005')
