import pandas as pd
import numpy as np
from utils.cross_section import alpha_rank
from utils.calculators import  date_index_locator
#(-1 * Ts_Rank(rank(low), 9))
def alpha_004(**kwargs):
    """
    三个参数
    dfs:股票数据df组成的列表，数据从data_measue给的日期最起码要有9日(包括当天)的数据，不然会报错
    data_measure:Y-M-D形式的str,输入的日期代表计算第二天的选股,不能是节假日
    correlation_day:最后一步相关系数计算的日期长度int值，公式的为9

    """

    dfs=kwargs.get('dfs')
    date_measure=pd.to_datetime(kwargs.get('date_measure'))
    ts_rank_day=kwargs.get('ts_rank_day')

    result=[]
    rank_low=[]
    date_index_dic={}
    for df in dfs:
        date_index_dic[df['code'].iloc[0]]=date_index_locator(df,date_measure)
    for code, idx in date_index_dic.items():
        if idx < ts_rank_day - 1:
            raise ValueError(f"股票 {code} 历史数据不足，需要至少 {ts_rank_day} 天，当前只有 {idx+1} 天")
    for i in range(0,ts_rank_day):
        low_datas=[]
        for df in dfs:
            date_index=date_index_dic.get(df['code'].iloc[0])

            low_datas.append(df.loc[date_index-i,'low'])
        rank_low.append(alpha_rank(low_datas))
    rank_low=np.array(rank_low)
    for i in range(0,len(dfs)):
        ts_ranks=alpha_rank(
            rank_low[:,i],
                                    )

        result.append(-1 * ts_ranks[0])
    return result