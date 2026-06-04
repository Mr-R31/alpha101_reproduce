import pandas as pd
from utils.cross_section import alpha_rank
from utils.time_series import Ts_ArgMax , returns_adjuster
from utils.calculators import returns_calculator, date_index_locator , SignedPower

#alpha 001 (rank(Ts_ArgMax(SignedPower(((returns < 0) ? stddev(returns, 20) : close), 2.), 5)) -0.5)
def alpha_001(**kwargs):
    """
    两个参数
    dfs:股票数据df组成的列表
    data_measure:Y-M-D形式的str,输入的日期代表计算第二天的选股
    """
    dfs=kwargs.get('dfs')
    date_measure=pd.to_datetime(kwargs.get('date_measure'))

    alpha_list=[]
    for df in dfs:
        df=returns_calculator(df)
        date_index=date_index_locator(df,date_measure)
        arg_list=[]
        for i in range(date_index,date_index-5,-1):
            x= returns_adjuster(df,i)
            arg_list.append(SignedPower(x))

        alpha_list.append(Ts_ArgMax(arg_list))

    ranked = alpha_rank(alpha_list,method='percentile')
    return ranked

