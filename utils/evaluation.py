import pandas as pd
import numpy as np
from scipy.stats import spearmanr
from utils.calculators import date_index_locator

def build_forward_return_panel(dfs, dates):
    """
    构建未来收益面板数据。

    对每个日期 T，未来收益 = close_{T+1} / close_T - 1

    参数
    ----------
    dfs : list of pd.DataFrame，每个须含 date、code、close 三列
    dates : list-like，日期序列（str 或 datetime）

    返回
    -------
    pd.DataFrame : 行为日期、列为股票代码、值为未来一日收益率
    """
    codes = [df['code'].iloc[0] for df in dfs]
    panel = {}

    for df in dfs:
        code = df['code'].iloc[0]
        col = {}
        for date in dates:
            date_ts = pd.to_datetime(date)
            try:
                idx = date_index_locator(df, date_ts)
                close_today = df.loc[idx, 'close']
                close_next = df.loc[idx + 1, 'close']
                col[date_ts] = close_next / close_today - 1
            except (IndexError, KeyError):
                col[date_ts] = np.nan
        panel[code] = pd.Series(col)

    result = pd.DataFrame(panel)
    result.index = pd.to_datetime(result.index)
    return result.sort_index()


def build_factor_panel(alpha_func, dfs, dates, single_stock=False, **alpha_kwargs):
    """
    构建因子值面板数据。

    参数
    ----------
    alpha_func : callable，因子函数，接受 **kwargs（dfs, date_measure, ...）
    dfs : list of pd.DataFrame
    dates : list-like，日期序列（str 或 datetime）
    single_stock : bool
        True  → 逐只股票调用 alpha_func(dfs=[df], ...)，适用于 alpha_007、alpha_009
        False → 一次传入全部股票调用 alpha_func(dfs=dfs, ...)，适用于 alpha_001~006、008、010
    **alpha_kwargs : 转发给因子函数的额外参数（如 correlation_day、ts_rank_day、type 等）

    返回
    -------
    pd.DataFrame : 行为日期、列为股票代码、值为因子值
    """
    codes = [df['code'].iloc[0] for df in dfs]
    panel = {code: {} for code in codes}

    for date in dates:
        date_ts = pd.to_datetime(date)
        try:
            if single_stock:
                for df in dfs:
                    code = df['code'].iloc[0]
                    try:
                        val = alpha_func(dfs=[df], date_measure=date_ts, **alpha_kwargs)
                        panel[code][date_ts] = val
                    except (ValueError, IndexError, KeyError):
                        panel[code][date_ts] = np.nan
            else:
                result = alpha_func(dfs=dfs, date_measure=date_ts, **alpha_kwargs)
                for code, val in zip(codes, result):
                    panel[code][date_ts] = val
        except (ValueError, IndexError, KeyError):
            for code in codes:
                panel[code][date_ts] = np.nan

    result = pd.DataFrame(panel)
    result.index = pd.to_datetime(result.index)
    return result.sort_index()


def compute_rank_ic_series(factor_panel, forward_panel):
    """
    逐日计算 rank IC（Spearman 秩相关系数）。

    每日剔除 NaN 配对后，至少需要 3 个有效股票才计算 IC，否则返回 NaN。
    若因子值或收益率为常数（标准差为 0），同样返回 NaN。

    参数
    ----------
    factor_panel : pd.DataFrame，行为日期、列为股票代码
    forward_panel : pd.DataFrame，行为日期、列为股票代码

    返回
    -------
    pd.Series : 每日 rank IC 值
    """
    common_dates = factor_panel.index.intersection(forward_panel.index)
    ic_values = {}

    for date in common_dates:
        factor_row = factor_panel.loc[date]
        fwd_row = forward_panel.loc[date]

        mask = factor_row.notna() & fwd_row.notna()
        # 有效股票数不足 3 只，跳过
        if mask.sum() < 3:
            ic_values[date] = np.nan
            continue

        f = factor_row[mask]
        r = fwd_row[mask]
        # 因子值或收益率为常数，相关系数无定义，跳过
        if np.std(f) == 0 or np.std(r) == 0:
            ic_values[date] = np.nan
            continue

        ic, _ = spearmanr(f, r)
        ic_values[date] = ic

    return pd.Series(ic_values).sort_index()


def ic_summary(ic_series):
    """
    计算 IC 汇总统计量（样本标准差）。

    参数
    ----------
    ic_series : pd.Series

    返回
    -------
    dict : {mean_ic, std_ic, ic_ir}，IC_IR = mean / std
    """
    valid = ic_series.dropna()
    if len(valid) == 0:
        return {'mean_ic': np.nan, 'std_ic': np.nan, 'ic_ir': np.nan}

    mean_ic = valid.mean()
    std_ic = valid.std(ddof=1)
    ic_ir = mean_ic / std_ic if std_ic > 0 else np.nan

    return {'mean_ic': mean_ic, 'std_ic': std_ic, 'ic_ir': ic_ir}

def build_price_panel(dfs, dates):
    """
    构建价格面板，供 AlphaPurify 使用。

    参数
    ----------
    dfs : list of pd.DataFrame，每只股票的日线数据
    dates : list-like，日期序列（str 或 datetime）

    返回
    -------
    pd.DataFrame : 行为日期、列为股票代码、值为 close 价格
    """
    price_dates = pd.to_datetime(dates)
    panel = {}
    for df in dfs:
        code = df['code'].iloc[0]
        s = df.set_index('date')['close'].reindex(price_dates)
        panel[code] = s
    return pd.DataFrame(panel)


def factor_panel_to_long(factor_panel, price_panel):
    """
    把 evaluation 的宽表面板转为 AlphaPurify 需要的长表格式。

    返回 pd.DataFrame，列: date, code, close, factor_value
    """
    # factor_panel: index=dates, columns=stock codes
    # price_panel:  index=dates, columns=stock codes

    df = factor_panel.stack().reset_index()
    df.columns = ["date", "code", "factor_value"]
    price_long = price_panel.stack().reset_index()
    price_long.columns = ["date", "code", "close"]
    return df.merge(price_long, on=["date", "code"])


def evaluation_alphapurify(dfs,dates,alphas):
    from alphapurify import FactorAnalyzer 
    for name, module_path, func_name, single, extras in alphas:
        # 动态导入因子函数
        mod = __import__(module_path, fromlist=["dummy"])
        alpha_func = getattr(mod, func_name)

        # 构建因子面板
        f_df = build_factor_panel(alpha_func, dfs, dates,single_stock=single,**extras)
        p_df = build_price_panel(dfs, dates)

        #转长表
        long_df = factor_panel_to_long(f_df, p_df)

        #评估
        analyzer = FactorAnalyzer.simple(
            df=long_df,
            factor_name='factor_value',
            trade_date_col="date",
            symbol_col="code",
            price_col="close",
        )
        analyzer.run()

        # 4. 查看可视化
        fig = analyzer.create_single_fac_ic_sheet(return_fig=True) # IC 面板
        fig_1=analyzer.create_long_short_return_sheet(return_fig=True)# 多空收益曲线
        fig.write_html(f"ic_sheet_{name}.html")
        fig_1.write_html(f'return_sheet_{name}.html')
