import pandas as pd
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.calculators import date_index_locator , correlation_calculator


#Alpha006: (-1 * correlation(open, volume, 10))
def alpha_006(**kwargs):
    """
    三个参数
    dfs:股票数据df组成的列表，数据从data_measue给的日期最起码要有前10日(包括当天)的数据，不然会报错
    data_measure:Y-M-D形式的str,输入的日期代表计算第二天的选股,不能是节假日
    correlation_day:最后一步相关系数计算的日期长度int值，公式的为10

    """
    result=[]
    dfs=kwargs.get('dfs')
    date_measure=pd.to_datetime(kwargs.get('date_measure'))
    correlation_day=kwargs.get('correlation_day')-1
    # 构建日期索引字典
    date_index_dic = {}
    for df in dfs:
        code = df['code'].iloc[0]              # 或 df['code'].iloc[0]
        date_index_dic[code] = date_index_locator(df, date_measure)
    # 检查历史数据（需要至少 10 天）
    for code, idx in date_index_dic.items():
        if idx < correlation_day:                  # 因为索引从0开始，至少需要 idx >= 9
            raise ValueError(f"股票 {code} 历史数据不足，需要至少 {correlation_day} 天，当前只有 {idx+1} 天")

    for df in dfs:
        code = df['code'].iloc[0]
        date_index = date_index_dic[code]
        open_val = df.loc[date_index-correlation_day:date_index, 'open']
        volume_val = df.loc[date_index-correlation_day:date_index, 'volume']
        result.append(-1*(correlation_calculator(open_val, volume_val)[0,1]))
    return result
