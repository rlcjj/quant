import pandas as pd
import os
import numpy as np
from quant.utility_fun.factor_preprocess import FactorPreProcess


def BiggerThanPercent(a, val=0.05):

    n = 0
    for i in range(len(a)):
        if a[i] > val:
            n += 1
    return n / len(a)


def FundAlphaScore():

    factor_name_list = ["TotalMarketValue", "BP", "IncomeYOYDaily", "ROETTMDaily", "Industry"]
    T = 4
    alpha = 0.025
    Weight = [0.2, 0.2, 0.2, 0.2, 0.3]

    for i_factor in range(len(factor_name_list)):

        factor_name = factor_name_list[i_factor]
        path = 'E:\\3_Data\\4_fund_data\\7_fund_select_stock\\FundSelectStockAlpha\\'
        filename = os.path.join(path, 'FundSelectStockAlpha_' + factor_name + '.csv')
        data = pd.read_csv(filename, index_col=[0], encoding='gbk')
        data.index = data.index.map(str)

        data_mean = data.rolling(window=T).mean()
        data_ir = data_mean / data.rolling(window=T).std() * np.sqrt(T - 1)
        data_percent = data.rolling(window=T).apply(lambda x: BiggerThanPercent(x, alpha))

        data_mean = data_mean.T
        data_mean = FactorPreProcess().remove_extreme_value_std(data_mean)
        data_mean = FactorPreProcess().standardization(data_mean)
        filename = os.path.join(path, 'FundSelectStockAlphaMean_' + factor_name + '.csv')
        data_mean.to_csv(filename)

        data_ir = data_ir.T
        data_ir = FactorPreProcess().remove_extreme_value_std(data_ir)
        data_ir = FactorPreProcess().standardization(data_ir)
        filename = os.path.join(path, 'FundSelectStockAlphaIR_' + factor_name + '.csv')
        data_ir.to_csv(filename)

        data_percent = data_percent.T
        data_percent = FactorPreProcess().remove_extreme_value_std(data_percent)
        data_percent = FactorPreProcess().standardization(data_percent)
        filename = os.path.join(path, 'FundSelectStockAlphaPercent_' + factor_name + '.csv')
        data_percent.to_csv(filename)

        result = 0.25 * data_mean + 0.5 * data_ir + 0.25 * data_percent
        result = result.sort_values(by=['20171231'],ascending=False)

        filename = os.path.join(path, 'FundSelectStockScore_' + factor_name + '.csv')
        result.to_csv(filename)

    for i_factor in range(len(factor_name_list)):

        factor_name = factor_name_list[i_factor]
        w = Weight[i_factor]
        path = 'E:\\3_Data\\4_fund_data\\7_fund_select_stock\\FundSelectStockAlpha\\'
        filename = os.path.join(path, 'FundSelectStockScore_' + factor_name + '.csv')
        data = pd.read_csv(filename, index_col=[0], encoding='gbk')
        data.columns = data.columns.map(str)

        if i_factor == 0:
            result = data * w
        else:
            result = result + data * w

    result = result.sort_values(by=['20171231'], ascending=False)
    filename = os.path.join(path, 'TotalScore' + '.csv')
    result.to_csv(filename)


def FundAlphaCorr():

    factor_name_list = ["TotalMarketValue", "BP", "IncomeYOYDaily", "ROETTMDaily", "Industry"]

    for i_factor in range(len(factor_name_list)):

        factor_name = factor_name_list[i_factor]
        path = 'E:\\3_Data\\4_fund_data\\7_fund_select_stock\\FundSelectStockAlpha\\'
        filename = os.path.join(path, 'FundSelectStockAlpha_' + factor_name + '.csv')
        data = pd.read_csv(filename, index_col=[0], encoding='gbk')
        data.index = data.index.map(str)
        data = data.T
        data_corr = data.corr()

        corr = []
        for i in range(len(data_corr)-1):
            corr.append(data_corr.iloc[i, i+1])

        corr_mean = np.median(corr)
        print(corr_mean, factor_name)

    path = 'E:\\3_Data\\4_fund_data\\7_fund_select_stock\\FundSelectStockAlpha\\'
    filename = os.path.join(path, 'TotalScore' + '.csv')
    data = pd.read_csv(filename, index_col=[0], encoding='gbk')
    data_corr = data.corr()

    corr = []
    for i in range(len(data_corr) - 1):
        corr.append(data_corr.iloc[i, i + 1])

    corr_mean = pd.DataFrame(corr).median()
    print(corr_mean, "TotalScore")

if __name__ == '__main__':

    a = [0.2, 0.4, -0.2]
    print(BiggerThanPercent(a, 0.1))
    # FundAlphaScore()
    FundAlphaCorr()

