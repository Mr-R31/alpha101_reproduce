import pandas as pd
import numpy as np
from utils.cross_section import alpha_rank
from utils.time_series import delta
from utils.calculators import  date_index_locator ,adv_calculator




#((adv20 < volume) ? ((-1ts_rank(abs(delta(close, 7)), 60))sign(delta(close, 7))) : (-1*1))
def alpha_007(**kwargs):
    """
    两个参数
    dfs:股票数据df组成的列表,007是对单只股票的计算，所以列表里只有一只股票，数据从data_measue给的日期最起码要有前67日(包括当天)的数据，不然会报错
    data_measure:Y-M-D形式的str,输入的日期代表计算第二天的选股,不能是节假日

    """
    dfs=kwargs.get('dfs')
    date_measure=pd.to_datetime(kwargs.get('date_measure'))

    rank_days= 60
    delta_days=7
    adv_variable='volume'
    adv_days=20
    # 构建日期索引字典
    date_index_dic = {}


    for df in dfs:
        code = df['code'].iloc[0]           # 或 df['code'].iloc[0]
        date_index_dic[code] = date_index_locator(df, date_measure)
    # 检查历史数据（需要至少 67 天）
    for code, idx in date_index_dic.items():
        if idx < rank_days+delta_days-1:                  # 因为索引从0开始，至少需要 idx >= 66
            raise ValueError(f"股票 {code} 历史数据不足，需要至少 {rank_days+delta_days} 天，当前只有 {idx+1} 天")

    for df in dfs:
        code = df['code'].iloc[0]
        date_index = date_index_dic[code]
        df= adv_calculator(df,days=adv_days,variable=adv_variable)
        volume_today=df.loc[date_index,'volume']
        if df.loc[date_index,f'{adv_variable}_adv_{adv_days}']<volume_today:
            delta_vals=[]
            for i in range(0,rank_days):
                delta_vals.append(delta(df,day=delta_days,date_index=date_index-i,delta_colum='close'))

            delta_vals=np.array(delta_vals)
            rank_val = -1*alpha_rank(np.abs(delta_vals))
            result=np.sign(delta_vals[0])*rank_val[0]
            return result
        else:
            return -1