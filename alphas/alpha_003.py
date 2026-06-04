import pandas as pd
import numpy as np
from utils.cross_section import alpha_rank
from utils.calculators import  date_index_locator , correlation_calculator
#Alpha003: (-1 * correlation(rank(open), rank(volume), 10))
def alpha_003(**kwargs):
    """
    三个参数
    dfs:股票数据df组成的列表，数据从data_measue给的日期最起码要有10日(包括当天)的数据，不然会报错
    data_measure:Y-M-D形式的str,输入的日期代表计算第二天的选股,不能是节假日
    correlation_day:最后一步相关系数计算的日期长度int值，公式的为10

    """
    dfs=kwargs.get('dfs')
    date_measure=pd.to_datetime(kwargs.get('date_measure'))
    correlation_day=kwargs.get('correlation_day')
    rank_open=[]
    rank_volume=[]
    result=[]
    for i in range(0,correlation_day):
        open_datas=[]
        volume_datas=[]
        for df in dfs:
            date_index=date_index_locator(df,date_measure)
            if date_index - correlation_day <-1:
                raise ValueError(f'{df.loc[1,'code']}out of index')
            open_datas.append(df.loc[date_index-i,'open'])
            volume_datas.append(df.loc[date_index-i,'volume'])
        rank_open.append(alpha_rank(open_datas))
        rank_volume.append(alpha_rank(volume_datas))
    rank_open=np.array(rank_open)
    rank_volume=np.array(rank_volume)
    for i in range(0,len(dfs)):
        result.append(-1*correlation_calculator(rank_open[0:,i],rank_volume[0:,i])[0,1])

    return result