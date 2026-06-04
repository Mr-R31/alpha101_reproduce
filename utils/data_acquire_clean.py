import baostock as bs
import pandas as pd
import numpy as np
#### 登陆系统 ####
def acquire_stock(code='sh.600000',data_type='d',start_date='2024-07-01',end_date='2024-12-31'):
    lg = bs.login()
    # 显示登陆返回信息
    print('login respond error_code:'+lg.error_code)
    print('login respond  error_msg:'+lg.error_msg)

    #### 获取沪深A股历史K线数据 ####
    # 详细指标参数，参见"历史行情指标参数"章节；"分钟线"参数与"日线"参数不同。"分钟线"不包含指数。
    # 分钟线指标：date,time,code,open,high,low,close,volume,amount,adjustflag
    # 周月线指标：date,code,open,high,low,close,volume,amount,adjustflag,turn,pctChg
    #日线指标：date,code,open,high,low,close,preclose,volume,amount,adjustflag,turn,tradestatus,pctChg,isST
    data_aquire_list=({
                          'd':"date,code,open,high,low,close,preclose,volume,amount,adjustflag,turn,tradestatus,pctChg,isST",
                          'm':'date,code,open,high,low,close,volume,amount,adjustflag,turn,pctChg',
                          '5':'date,time,code,open,high,low,close,volume,amount,adjustflag'
                      }.get(data_type))
    rs = bs.query_history_k_data_plus(code,
        data_aquire_list,
        start_date, end_date,
        frequency=data_type, adjustflag="3")
    print('query_history_k_data_plus respond error_code:'+rs.error_code)
    print('query_history_k_data_plus respond  error_msg:'+rs.error_msg)

    #### 打印结果集 ####
    data_list = []
    while (rs.error_code == '0') & rs.next():
        # 获取一条记录，将记录合并在一起
        data_list.append(rs.get_row_data())
    result = pd.DataFrame(data_list, columns=rs.fields)

    #### 登出系统 ####
    bs.logout()
    return result


#清洗数据模块    data_type代表获取的是日线还是分钟线(D,M)不区分大小写
def data_clean(df,data_type):
    data_type=data_type.upper()
    data_list_group_by_type={'D':{'price_cols': ['open', 'high', 'low', 'close','preclose'],
                                  'volume_cols':['volume', 'amount','turn'],
                                  'unic_cols':['pctChg','tradestatus']
                                  },
                             'M':{'price_cols':['open', 'high', 'low', 'close'], #关于日和分钟线的交易量相关数据的表头与价格相关数据的表头
                                  'volume_cols':['volume', 'amount']
                                  }
                             }
    price_cols = data_list_group_by_type[data_type]['price_cols']
    volume_cols = data_list_group_by_type[data_type]['volume_cols']
    unic_cols=data_list_group_by_type[data_type].get('unic_cols',[])
    for col in price_cols + volume_cols + unic_cols + ['adjustflag']:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    #转化为时间序列
    #分钟线：df['time'] = pd.to_datetime(df['time'],format='%Y%m%d%H%M%S%f')
    #日线：df['date'] = pd.to_datetime(df['date'])
    if data_type =='D':
        df['date'] = pd.to_datetime(df['date'])
    elif data_type =='M':
        df['time'] = pd.to_datetime(df['time'],format='%Y%m%d%H%M%S%f')
    #检测是否有数据缺失，若有缺失则向前一个数据填充
    df['code'] = df['code'].ffill()
    df['open'] = df.groupby('code')['open'].ffill()
    df['high'] = df.groupby('code')['high'].ffill()
    df['low'] = df.groupby('code')['low'].ffill()
    df['close'] = df.groupby('code')['close'].ffill()
    df['preclose'] = df.groupby('code')['preclose'].ffill()
    #价格指标负数处理，若为负数则标记为nan
    for col in price_cols:
        df.loc[df[col] <= 0, col] = np.nan
    #规定停牌时的换手率和涨跌幅为0
    mask_stop = (df['tradestatus'] == 0)
    df.loc[mask_stop, 'turn'] = 0.0
    df.loc[mask_stop, 'pctChg'] = 0.0


    #  删除所有价格或成交量全为空的行
    df.dropna(subset=['close', 'volume'], how='all', inplace=True)
    #若high<low，则两者对调
    df['high'], df['low'] = np.where(df['high'] < df['low'],
                                 [df['low'], df['high']],
                                 [df['high'], df['low']])
    #保证low<=open,close<=high,超出则对应用low或high代替
    df['open'] = np.where(df['open'] > df['high'], df['high'], df['open'])
    df['open'] = np.where(df['open'] < df['low'], df['low'], df['open'])
    df['close'] = np.where(df['close'] > df['high'], df['high'], df['close'])
    df['close'] = np.where(df['close'] < df['low'], df['low'], df['close'])

    #更改所有无成交量 负成交量 无成交额 负成交额 为0
    df['volume'] = df['volume'].fillna(0).clip(lower=0)
    df['amount'] = df['amount'].fillna(0).clip(lower=0)

#异常量检测

    #通过 成交量*收盘价 估算 成交额 计算 与成交额的差距百分比 ，并标记误差超过10%的（day）
    df['amount_est'] = df['volume'] * df['close']
    df['amount_error_ratio'] = abs(df['amount'] - df['amount_est']) / df['amount_est'].replace(0, np.nan)
    df['amount_suspicious'] = df['amount_error_ratio'] > 0.10

    #涨跌幅缺失且正常交易时，计算涨跌幅
    df.loc[df['pctChg'].isna() & (df['tradestatus'] == 1), 'pctChg'] = df.loc[df['pctChg'].isna() & (df['tradestatus'] == 1), 'close'] / df.loc[df['pctChg'].isna() & (df['tradestatus'] == 1), 'preclose'] -1

    #换手率通常在0到0.8之间，超过的数据截断
    df.loc[(df['tradestatus'] == 1) & (df['turn'] > 0.8), 'turn'] = 0.8
    df.loc[(df['tradestatus'] == 1) & (df['turn'] < 0), 'turn'] = 0.0

    #删除同一时间的同股票代码数据，仅保留最后一项
    #分钟线：df.drop_duplicates(subset=['time', 'code'], keep='last', inplace=True)
    #日线：df.drop_duplicates(subset=['date', 'code'], keep='last', inplace=True)
    if data_type == 'D':
        df.drop_duplicates(subset=['date', 'code'], keep='last', inplace=True)
    elif data_type =='M':
        df.drop_duplicates(subset=['time', 'code'], keep='last', inplace=True)
    return df

#获取对应baoshock里的对应股票代码的数据，清洗，存储为csv文件
def result_to_csv(result,data_type):
    result=data_clean(result,data_type=data_type)

    fname = "{}_{}_to_{}_{}.csv".format(
        result.loc[0,'code'],
        result.loc[0,'date'].date(),
        result.loc[result.index[-1],'date'].date(),
        data_type)
    result.to_csv(fname, index=False)
    return result

#读取csv文件，转化为时间序列
def csv_read(csv_path):
    df = pd.read_csv(csv_path)
    df['date'] = pd.to_datetime(df['date'])
    return df.copy()