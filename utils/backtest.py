import pandas as pd
import numpy as np
def factor_to_weights(factor_df, top_n=2, bottom_n=3 ,method='equal'):
    """
    factor_df: index=date, columns=code
    每天做多因子值最高的 top_n 只，做空最低的 bottom_n 只，方式有 equal(等权)
    """
    weights = pd.DataFrame(0.0, index=factor_df.index, columns=factor_df.columns)
    if method == 'equal':
        for date in factor_df.index:
            ranked = factor_df.loc[date].rank(ascending=False)
            longs = ranked.nlargest(top_n).index
            shorts = ranked.nsmallest(bottom_n).index
            weights.loc[date, longs] = 1.0 / top_n
            weights.loc[date, shorts] = -1.0 / bottom_n
    return weights

def compute_pnl(weights_df, fwd_ret_df):
    """
    weights_df: 每日仓位，fwd_ret_df: 每日未来收益
    返回每日组合收益率
    """
    return (weights_df * fwd_ret_df).sum(axis=1)

def equity_curve(daily_pnl):
    equity = (1 + daily_pnl).cumprod()
    sharpe = daily_pnl.mean() / daily_pnl.std() * np.sqrt(252)
    max_dd = (equity / equity.cummax() - 1).min()
    return equity, sharpe, max_dd

def back_test_plot(dfs,dates,alphas):
    # 回测(单日因子循环版)
    from utils.evaluation import build_factor_panel, build_forward_return_panel
    import matplotlib.pyplot as plt
    for name, module_path, func_name, single, extra_kwargs in alphas:
        mod = __import__(module_path, fromlist=["dummy"])
        alpha_func = getattr(mod, func_name)
        f_df = build_factor_panel(alpha_func, dfs, dates,
                              single_stock=single, **extra_kwargs)
        fwd = build_forward_return_panel(dfs, dates)
        valid = f_df.dropna(how='all').index.intersection(fwd.dropna(how='all').index)
        f_df, fwd = f_df.loc[valid], fwd.loc[valid]

        w = factor_to_weights(f_df, top_n=2, bottom_n=2)
        pnl = compute_pnl(w, fwd)
        curve, sharpe, dd = equity_curve(pnl)

        curve.plot(title=f"Sharpe={sharpe:.2f}, MaxDD={dd:.2%}")
        plt.savefig(f"{name}_equity.png")
        plt.close()


def back_test_plot_vec(full_df,dates,alphas):

    # 回测（向量化版）
    from utils.evaluation import  build_forward_return_panel_vec
    import matplotlib.pyplot as plt
    full_df = full_df.sort_values(['code', 'date']).copy()
    for name, module_path, func_name, single, extras in alphas:
        mod = __import__(module_path+'_vec', fromlist=["dummy"])
        alpha_func = getattr(mod, func_name)
        f_df = alpha_func(full_df)
        f_df = f_df.loc[f_df.index.isin(dates)]      # 限制回测范围



        full_df = build_forward_return_panel_vec(full_df)
        fwd = full_df.pivot(index='date', columns='code', values='fwd_ret')
        fwd = fwd.loc[fwd.index.isin(dates)]
        valid = f_df.dropna(how='all').index.intersection(fwd.dropna(how='all').index)
        f_df, fwd = f_df.loc[valid], fwd.loc[valid]

        w = factor_to_weights(f_df, top_n=2, bottom_n=2)
        pnl = compute_pnl(w, fwd)
        curve, sharpe, dd = equity_curve(pnl)

        curve.plot(title=f"Sharpe={sharpe:.2f}, MaxDD={dd:.2%}")
        plt.savefig(f"{name}_equity_vec.png")
        plt.close()
