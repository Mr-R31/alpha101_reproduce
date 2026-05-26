import pandas as pd
import numpy as np
from scipy.stats import rankdata
def alpha_rank(values,method='percentile'):
    """
    横截面排名函数
    values : 1D array-like
    method : 'ordinal'  -> 原始整数排名 (1-based, 并列按出现顺序)
             'average'  -> 平均排名 (1-based)
             'percentile' -> 百分比排名 (0~1, 最小为0, 最大为1)
             'pct'       -> 百分比排名 (最小为1/N, 最大为1)
    """
    arr = np.asarray(values, dtype=float)
    if method in ('ordinal', 'average', 'min', 'max', 'dense'):
        # 返回 1‑based 排名
        ranks = rankdata(arr, method=method)
        return ranks
    elif method == 'percentile':
        # (rank - 1) / (N - 1)   ->  [0, 1]
        ranks = rankdata(arr, method='average')           # 平均排名，处理并列
        return (ranks - 1) / (len(arr) - 1)
    elif method == 'pct':
        # rank / N   ->  [1/N, 1]
        ranks = rankdata(arr, method='average')
        return ranks / len(arr)
    else:
        raise ValueError(f"Unknown method: {method}")