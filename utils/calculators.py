import pandas as pd
import numpy as np
#计算 回报率 将回报率放表格里
def returns_calculator(df):
    if 'returns' not in df.columns:
        df['returns']=(df['close'] - df['preclose']) / df['preclose']
    return df

#计算变化率的函数
def changing_rate_calculator(df):
    if 'changing_rate' not in df.columns:
        df['changing_rate'] = (df['close']-df['open'])/df['open']
    else:
        pass

#计算x和y向量的相关系数
def correlation_calculator(arrx, arry):
    # 检查序列方差是否为 0
    if np.std(arrx) == 0 or np.std(arry) == 0:
        return np.full((2, 2), np.nan)
    return np.corrcoef(arrx, arry)

#返回date_measure日期对应的检索值
def date_index_locator(df,date_measure):
    return df.loc[df['date'] == date_measure].index[0]

#计算数据的vwap（成交量加权平均价格），type='d'，计算日线的近似值(high+low+close)/3）
def vwap_calculator(df, data_type='d', roll_window=10):
    if 'typical_price' not in df.columns:
        df['typical_price'] = (df['high'] + df['close'] + df['low']) / 3

    if data_type == 'd':
        df['vwap'] = df['typical_price']
        # 直接生成 10 日均值列（方便后续取用）
        df[f'vwap_mean_{roll_window}'] = df['vwap'].rolling(window=roll_window, min_periods=roll_window).mean()
    else:
        # 如果是分钟线，你可以后期扩展
        raise NotImplementedError("目前只支持日线 data_type='d'")
    return df

#SignedPower(x1,2)将x保留符号的平方
def SignedPower(x,date_index=21):
    x_sign=np.sign(x)
    x_squre=np.square(x)
    return x_squre*x_sign

#计算整个列表的指定 [variable] 的每 [days] 日的平均值 默认值为20日的volume平均值
def adv_calculator(df,days=20,variable='volume'):
    if f'{variable}_adv_{days}' not in df.columns:
        df[f'{variable}_adv_{days}'] = df[variable].rolling(window=days, min_periods=days).mean()

    return df
