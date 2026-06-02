import pandas as pd
import numpy as np
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.calculators import returns_calculator

#alpha 001 (rank(Ts_ArgMax(SignedPower(((returns < 0) ? stddev(returns, 20) : close), 2.), 5)) -0.5)
def alpha_001(full_df):
    """
    full_df: 长表，含 date, code, open, volume, colse。

    输出：df，包含所有日期的alpha_001的结果，数据不足的日子为nan
    """

    full_df = full_df.sort_values(['code', 'date']).copy()
    full_df =returns_calculator(full_df)
    ts_argmax_window=5
    cond=full_df['returns']<0

    if 'roll_std_20' not in full_df.columns:
        full_df['roll_std_20'] = full_df.groupby('code')['returns'].transform(
        lambda x : x.rolling(window=20, min_periods=20).std(ddof=1)
        )
    full_df['tendency'] = np.where(cond,
                                   full_df['roll_std_20'],
                                   full_df['close'])

    full_df['square_tendency']=np.sign(full_df['tendency'])*np.square(full_df['tendency'])

    full_df['ts_argmax']=full_df.groupby('code')['square_tendency'].transform(
        lambda x : x.rolling(window=ts_argmax_window, min_periods=ts_argmax_window).apply(lambda arr: np.argmax(arr)+1)
    )
    full_df['alpha_001']=full_df.groupby('date')['ts_argmax'].rank(pct=True)

    full_df.loc[full_df['ts_argmax'].isna(), 'alpha_001'] = np.nan

    return full_df.pivot(index='date', columns='code', values='alpha_001')

