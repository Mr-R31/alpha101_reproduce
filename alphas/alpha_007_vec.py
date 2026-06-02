import pandas as pd
import os
import numpy as np
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.time_series import delta_vec
from utils.calculators import adv_calculator




#((adv20 < volume) ? ((-1ts_rank(abs(delta(close, 7)), 60))sign(delta(close, 7))) : (-1*1))
def alpha_007(full_df):
    """
    full_df: 长表，含 date, code, close,volume。
    这个是单股票因子
    输出：df，包含所有日期的alpha_007的结果，数据不足的日子为nan

    """
    full_df = full_df.sort_values(['code', 'date']).copy()

    rank_days= 60
    delta_days=7
    adv_variable='volume'
    adv_days=20

    #delta(close, 7) 和 abs
    col=f'delta_close_{delta_days}'
    abs_col=f'abs_delta_close_{delta_days}'
    full_df[col] = delta_vec(full_df, day=delta_days, delta_colum='close')
    full_df[abs_col] = full_df[col].abs()

    #ts_rank(abs_col,60)
    ts_rank=full_df.groupby('code')[abs_col].rolling(rank_days,min_periods=rank_days).rank(pct=True)
    full_df['ts_rank']=ts_rank.reset_index(level=0,drop=True)

    #adv20
    adv_col =f'{adv_variable}_adv_{adv_days}'
    full_df=adv_calculator(full_df,adv_days,adv_variable,)


    cond=full_df[adv_col]<full_df[adv_variable]
    full_df['alpha_007']=np.where(cond,
                                  -1*full_df['ts_rank'] * np.sign(full_df[col])
                                  ,-1)
    full_df.loc[full_df['ts_rank'].isna() | full_df[adv_col].isna(), 'alpha_007'] = np.nan
    return full_df.pivot(index='date', columns='code', values='alpha_007')