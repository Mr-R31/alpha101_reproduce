import pandas as pd
import numpy as np

from utils.calculators import changing_rate_calculator

from utils.time_series import delta_vec
#Alpha002: (-1 * correlation(rank(delta(log(volume), 2)), rank(((close - open) / open)), 6))

def alpha_002(full_df):
    """
    full_df: 长表，含 date, code, open, volume, colse。

    输出：df，包含所有日期的alpha_002的结果，数据不足的日子为nan
    """

    full_df = full_df.sort_values(['code', 'date']).copy()

    cor_window=6
    delta_day=2
    log_con='log_vol'
    full_df[log_con]=np.log(full_df['volume'])
    full_df['delta_va']=delta_vec(full_df,
                                  day=delta_day,
                                  delta_colum=log_con)
    full_df['x_va']=full_df.groupby('date')['delta_va'].rank()

    full_df=changing_rate_calculator(
        full_df )
    full_df['y_va']=full_df.groupby('date')['changing_rate'].rank()

    corr_v=full_df.groupby('code')[['x_va','y_va']].rolling(window=cor_window,min_periods=cor_window).corr()
    full_df['alpha_002']=-1*corr_v.unstack().loc[:,('x_va','y_va')].droplevel(0)


    return full_df.pivot(index='date', columns='code', values='alpha_002')
