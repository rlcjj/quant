import pandas as pd
from calculate_barra_factor.factor_get_data import get_barra_standard_data, get_format_data, get_h5_data
import statsmodels.api as sm
import cvxopt.solvers as sol
from cvxopt import matrix
import matplotlib.pyplot as plt
import numpy as np


def get_barra_factor_exposure(name_list):

    panel = pd.Panel(dict([(name, get_barra_standard_data(name)) for name in name_list]))

    return panel


def multi_barra_factor_return():

    name_list = ["NORMAL_CNE5_SIZE",
                 "NORMAL_CNE5_NON_LINEAR_SIZE",
                 "NORMAL_CNE5_BOOK_TO_PRICE",
                 "NORMAL_CNE5_MOMENTUM",
                 "NORMAL_CNE5_EARNING_YIELD",
                 "NORMAL_CNE5_LIQUIDITY",
                 'NORMAL_CNE5_BETA',
                 "NORMAL_CNE5_RESIDUAL_VOLATILITY",
                 "NORMAL_CNE5_GROWTH",
                 "NORMAL_CNE5_LEVERAGE"
                 ]

    panel = get_barra_factor_exposure(name_list)

    pct_name = '涨跌幅'
    pct = get_format_data(pct_name)

    size_name = '总市值'
    size = get_format_data(size_name)

    industry_name = 'industry_citic1'
    industry = get_h5_data(industry_name)
    industry = industry.applymap(lambda x: x.decode('utf-8'))

    date_series = list(set(list(panel.major_axis)) & set(list(pct.index)) & set(list(industry.index)))
    date_series.sort()

    path = 'E:\\4_代码\\pycharmprojects\\2_风险模型BARRA\\data\\data\\'
    ind = pd.read_csv(path + 'industry.csv', encoding='gbk', index_col=[0])

    columns = ["CTY"]
    columns.extend(name_list)
    columns.extend(list(ind.index))

    factor_return = pd.DataFrame([], index=date_series, columns=columns)

    for i_index in range(0, len(date_series) - 1):

        last_date = date_series[i_index]
        date = date_series[i_index + 1]

        pct_date = pct.ix[date, :]
        pct_date.name = 'Stock_Pct'

        size_date = size.ix[last_date, :]
        size_date.name = 'Size'

        industry_date = industry.ix[last_date, :]
        industry_date.name = 'Industry'

        regression_data = pd.concat([panel.ix[:, last_date, :], pct_date, size_date, pd.get_dummies(industry_date)], axis=1)
        regression_data = regression_data.dropna()

        if len(regression_data) > 50:

            try:
                print(last_date)
                x_col = name_list.copy()
                x_col.extend(list(ind.index))
                y = regression_data['Stock_Pct'].values
                x = regression_data[x_col].values
                yes_size = regression_data['Size'].values

                x_add = sm.add_constant(x, has_constant='add')
                model = sm.WLS(y, x_add, weights=np.sqrt(yes_size)).fit()
                print(model.params[:])
                factor_return.ix[date, :] = model.params[:]
            except:
                pass

            # w = np.diag((1.0 / np.sqrt(today_size)))
            # w_inv = np.linalg.inv(w)
            # mat = np.linalg.inv(np.dot(np.dot(np.transpose(x_add), w_inv), x_add))
            # param = np.dot(np.dot(np.dot(mat, np.transpose(x_add)), w_inv), y)

    path = 'E:\\4_代码\\pycharmprojects\\2_风险模型BARRA\\data\\barra_factor_return\\'
    factor_return = factor_return.dropna()
    factor_return.to_csv(path + 'Factor_Return_Total.csv')
    factor_return = factor_return.ix["2010-01-06":, :]
    factor_return_cumsum = factor_return.cumsum()
    factor_return_cumsum.to_csv(path + 'Factor_Return_Total_CumSum.csv')


if __name__ == '__main__':

    multi_barra_factor_return()
