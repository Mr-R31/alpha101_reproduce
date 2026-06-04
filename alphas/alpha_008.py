#Alpha008: (-1 * rank(((sum(open, 5) * sum(returns, 5)) - delay((sum(open, 5) * sum(returns, 5)),10))))
import pandas as pd
import numpy as np
from utils.cross_section import alpha_rank
from utils.calculators import  date_index_locator , returns_calculator
def alpha_008(**kwargs):
    """
    两个参数
    dfs:股票数据df组成的列表，数据从data_measue给的日期最起码要有前15日(包括当天)的数据，不然会报错
    data_measure:Y-M-D形式的str,输入的日期代表计算第二天的选股,不能是节假日

    """
    dfs=kwargs.get('dfs')
    date_measure=pd.to_datetime(kwargs.get('date_measure'))

    sum_days= 5
    delay_days=10
    # 构建日期索引字典
    date_index_dic = {}


    for df in dfs:
        code = df['code'].iloc[0]           # 或 df['code'].iloc[0]
        date_index_dic[code] = date_index_locator(df, date_measure)
    # 检查历史数据（需要至少 15 天）
    for code, idx in date_index_dic.items():
        if idx < sum_days+delay_days-1:                  # 因为索引从0开始，至少需要 idx >= 14
            raise ValueError(f"股票 {code} 历史数据不足，需要至少 {sum_days+delay_days} 天，当前只有 {idx+1} 天")
    rank_val=[]
    for df in dfs:
        code = df['code'].iloc[0]
        date_index = date_index_dic[code]
        df = returns_calculator(df)
        tendency_val =np.sum(df['open'].iloc[date_index-sum_days+1:date_index+1])*np.sum(df['returns'].iloc[date_index-sum_days+1:date_index+1])-np.sum(df['open'].iloc[date_index-sum_days+1-delay_days:date_index-delay_days+1])*np.sum(df['returns'].iloc[date_index-sum_days+1-delay_days:date_index-delay_days+1])
        rank_val.append(tendency_val)

    result=alpha_rank(rank_val)*-1
    return result
