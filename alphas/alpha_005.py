import pandas as pd
import os
import numpy as np
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.cross_section import alpha_rank
from utils.calculators import  date_index_locator , vwap_calculator
#(rank((open - (sum(vwap, 10) / 10))) * (-1 * abs(rank((close - vwap)))))
def alpha_005(**kwargs):
    """
    两个参数
    dfs:股票数据df组成的列表，数据从data_measue给的日期最起码要有10日(包括当天)的数据，不然会报错
    data_measure:Y-M-D形式的str,输入的日期代表计算第二天的选股,不能是节假日

    """
    dfs = kwargs.get('dfs')
    date_measure = pd.to_datetime(kwargs.get('date_measure'))
    data_type = kwargs.get('type', 'd')          # 默认日线
    vwap_days = 10
    # 构建日期索引字典
    date_index_dic = {}
    for df in dfs:
        code = df['code'].iloc[0]            # 或 df['code'].iloc[0]
        date_index_dic[code] = date_index_locator(df, date_measure)
    # 检查历史数据（需要至少 10 天）
    for code, idx in date_index_dic.items():
        if idx < vwap_days - 1:                  # 因为索引从0开始，至少需要 idx >= 9
            raise ValueError(f"股票 {code} 历史数据不足，需要至少 {vwap_days} 天，当前只有 {idx+1} 天")
    x_datas = []
    y_datas = []
    for df in dfs:
        code = df['code'].iloc[0]
        date_index = date_index_dic[code]
        # 确保 vwap 及均值列已计算
        if f'vwap_mean_{vwap_days}' not in df.columns:
            df = vwap_calculator(df, data_type=data_type, roll_window=vwap_days)
        # x = open - mean(vwap, 10)
        open_val = df.loc[date_index, 'open']
        vwap_mean = df.loc[date_index, f'vwap_mean_{vwap_days}']
        x_datas.append(open_val - vwap_mean)
        # y = close - today's vwap (即当日典型价格)
        close_val = df.loc[date_index, 'close']
        today_vwap = df.loc[date_index, 'vwap']
        y_datas.append(close_val - today_vwap)
    # 横截面排名
    rank_x = alpha_rank(x_datas)                # 返回 [0,1] 百分比排名
    rank_y = alpha_rank(y_datas)
    # 最终因子值
    result = rank_x * (-1 * np.abs(rank_y))
    return result

