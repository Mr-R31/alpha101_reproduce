import pandas as pd
import os
import numpy as np
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.cross_section import alpha_rank
from utils.time_series import delta
from utils.calculators import changing_rate_calculator, date_index_locator , correlation_calculator
#Alpha002: (-1 * correlation(rank(delta(log(volume), 2)), rank(((close - open) / open)), 6))
def alpha_002(**kwargs):
    """
    三个参数
    dfs:股票数据df组成的列表，数据从data_measue给的日期最起码要有前8日(包括当天)的数据，不然会报错
    data_measure:Y-M-D形式的str,输入的日期代表计算第二天的选股,不能是节假日
    correlation_day:最后一步相关系数计算的日期长度int值，公式的为6

    """
    result=[]
    day=2
    dfs=kwargs.get('dfs')
    date_measure=pd.to_datetime(kwargs.get('date_measure'))
    correlation_day=kwargs.get('correlation_day')
    x_ranks = []
    y_ranks = []
    for i in range(0,correlation_day):
        x_list=[]
        y_list=[]
        for df in dfs:
            date_index=date_index_locator(df,date_measure)
            if date_index - correlation_day - day <-1:
                raise ValueError(f'{df.loc[1,'code']}out of index')
            #计算log_volume(仅一次)
            if 'log_volume' not in df.columns:
                df['log_volume'] = np.log(df['volume'])

            changing_rate_calculator(df)

            x_list.append(delta(df,
                                day=day,
                                date_index=date_index-i
                                )
                          )
            y_list.append(df.loc[date_index-i,'changing_rate'])
        x_ranks.append(alpha_rank(y_list,
                            method='percentile'
                            )
                       )
        y_ranks.append(alpha_rank(x_list,
                            method='percentile'
                            )
                       )
        x=np.array(x_ranks)
        y=np.array(y_ranks)
    for i in range(0,len(dfs)):
        result.append(-1*correlation_calculator(x[0:,i],y[0:,i])[0,1])
    return result