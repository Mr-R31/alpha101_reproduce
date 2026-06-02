#Alpha010: rank(((0 < ts_min(delta(close, 1), 4)) ? delta(close, 1) : ((ts_max(delta(close, 1), 4) < 0)? delta(close, 1) : (-1 * delta(close, 1)))))
import pandas as pd
import os
import numpy as np
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.cross_section import alpha_rank
from utils.time_series import delta
from utils.calculators import  date_index_locator

def alpha_010(**kwargs):
    """
    两个参数
    dfs:股票数据df组成的列表，数据从data_measue给的日期最起码要有前5日(包括当天)的数据，不然会报错
    data_measure:Y-M-D形式的str,输入的日期代表计算第二天的选股,不能是节假日

    """
    dfs=kwargs.get('dfs')
    date_measure=pd.to_datetime(kwargs.get('date_measure'))

    ts_m_days= 4
    delta_days= 1
    # 构建日期索引字典
    date_index_dic = {}
    rank_val=[]

    for df in dfs:
        code = df['code'].iloc[0]           # 或 df['code'].iloc[0]
        date_index_dic[code] = date_index_locator(df, date_measure)
    # 检查历史数据（需要至少 5 天）
    for code, idx in date_index_dic.items():
        if idx < ts_m_days+delta_days-1:                  # 因为索引从0开始，至少需要 idx >= 4
            raise ValueError(f"股票 {code} 历史数据不足，需要至少 {delta_days+ts_m_days} 天，当前只有 {idx+1} 天")

    for df in dfs:
        code = df['code'].iloc[0]
        date_index = date_index_dic[code]
        delta_val =[]
        for i in range(0,ts_m_days):
            delta_val.append(delta(df,day=delta_days,date_index=date_index-i,delta_colum='close'))
        ts_min  =np.min(delta_val)
        if ts_min >0:
            rank_val.append(delta_val[0])
        else:
            ts_max = np.max(delta_val)
            if ts_max <0:
                rank_val.append(delta_val[0])
            else:
                rank_val.append(delta_val[0]*-1)

    result = alpha_rank(rank_val)
    return result
