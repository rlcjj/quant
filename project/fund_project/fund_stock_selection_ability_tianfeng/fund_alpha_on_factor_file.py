import pandas as pd
import numpy as np
from quant.stock.date import Date
from quant.stock.stock import Stock
from quant.fund.fund import Fund
import os


def GetStockAlphaAtFactorFile(path, factor_name):

    """
    从 文件当中得到 所有股票 所有日期 在Factor上的Alpha
    """

    # path = 'E:\\3_Data\\4_fund_data\\7_fund_select_stock\\StockAlpha\\'
    # factor_name = "TotalMarketValue"

    filename = os.path.join(path, 'StockAlpha_' + factor_name + '.csv')

    if os.path.exists(filename):
        data = pd.read_csv(filename, index_col=[0], encoding='gbk').T
        data.columns = data.columns.map(str)
    else:
        data = None

    return data


def GetFundAlphaAtFactorFile(stock_alpha, fund_holding, report_date):

    ###################################################################################
    # report_date = "20171231"
    # fund_code = '000001.OF'
    #
    # path = 'E:\\3_Data\\4_fund_data\\7_fund_select_stock\\StockAlpha\\'
    # factor_name = "TotalMarketValue"
    # stock_alpha = GetStockAlphaAtFactorFile(path, factor_name)
    # fund_holding_all = Fund().get_fund_holding_all()
    #
    # ###################################################################################
    # fund_holding = fund_holding_all[fund_holding_all['FundCode'] == fund_code]
    # fund_holding = fund_holding[fund_holding['Date'] == report_date]
    # fund_holding.index = fund_holding['StockCode']
    # fund_holding = fund_holding.ix[~fund_holding.index.duplicated(), :]

    ###################################################################################
    if report_date in stock_alpha.columns:

        concat_data = pd.concat([fund_holding['Weight'], stock_alpha[report_date]], axis=1)
        concat_data.columns = ['Weight', 'Alpha']
        concat_data = concat_data.dropna()
        concat_data = concat_data.sort_values(by=['Weight'],ascending=False)
        if len(concat_data) > 0:
            alpha = (concat_data['Weight'] * concat_data['Alpha']).sum() / concat_data['Weight'].sum()
        else:
            alpha = np.nan
    else:
        alpha = np.nan
    ###################################################################################

    return alpha

if __name__ == "__main__":

    # GetStockAlphaAtFactorFile
    ####################################################################################
    report_date = "20171231"
    fund_code = '229002.OF'

    path = 'E:\\3_Data\\4_fund_data\\7_fund_select_stock\\StockAlpha\\'
    factor_name = "Industry"
    stock_alpha = GetStockAlphaAtFactorFile(path, factor_name)

    # GetFundAlphaAtFactorFile
    ###################################################################################
    fund_holding_all = Fund().get_fund_holding_all()
    fund_holding = fund_holding_all[fund_holding_all['FundCode'] == fund_code]
    fund_holding = fund_holding[fund_holding['Date'] == report_date]
    fund_holding.index = fund_holding['StockCode']
    fund_holding = fund_holding.ix[~fund_holding.index.duplicated(), :]

    alpha = GetFundAlphaAtFactorFile(stock_alpha, fund_holding, report_date)
    print(alpha)

    ####################################################################################
