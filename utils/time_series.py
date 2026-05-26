import pandas as pd
import numpy as np
#Ts_ArgMax(x2)
def Ts_ArgMax(arg_list):

    return np.argmax(arg_list)+1




#求day前日到当日delta_colum对应列的变化量，默认为alpha002的log(volume)
def delta(df,day=2,date_index=21,delta_colum='log_volume'):
    x = df.loc[date_index,delta_colum] - df.loc[date_index-day,delta_colum]
    return x

#(returns < 0) ? stddev(returns, 20) : close)
def returns_adjuster(df, date_index=21):
    """
    对于给定的 date_index，返回：
    - 如果该行的 returns < 0，则返回该行的 20 日标准差（含当天）
    - 否则返回该行的 close
    """
    # 1. 计算全序列的 20 日滚动标准差（只算一次）
    if 'roll_std_20' not in df.columns:
        df['roll_std_20'] = df['returns'].rolling(window=20, min_periods=1).std(ddof=1)

    # 2. 按 date_index 取出对应值
    if df.loc[date_index, 'returns'] < 0:
        x = df.loc[date_index, 'roll_std_20']
    else:
        x = df.loc[date_index, 'close']
    return x