# Alpha 101 复现

对 Alpha 101 因子（001-010）的复现，包含逐股和向量化两种实现，以及基于 AlphaPurify 的因子评估框架。

## Setup

```bash
git clone <repo-url>
cd git
pip install -r requirements.txt
```

所有脚本须从项目根目录运行，以便 `from utils.xxx import ...` 路径正确解析。

## 使用

主程序为 `Alpha 101_reproduce.ipynb`。初次使用需从头到尾运行以获取数据，此后除 Import 栏外，只需从 csv_read 开始运行即可。

已有功能：
- 001-010 的向量化和单日因子计算
- IC 值计算
- 基于 AlphaPurify 的可视化因子评估
- 一个轻量的对因子回测的引擎