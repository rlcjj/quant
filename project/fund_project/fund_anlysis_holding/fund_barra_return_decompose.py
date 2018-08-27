import pandas as pd
import numpy as np
from quant.stock.barra import Barra
from quant.stock.date import Date
import os
from quant.fund.fund import Fund
from quant.utility_fun.pandas_fun import pandas_add_row


def FundBarraDecomposeReturnQuarter(fund_holding_date, report_date):

    """
    计算在给定时间点前后一个月 基金 拆分的 特异收益 风格收益 行业收益 和 市场收益
    """

    # params
    ###################################################################################
    report_date = '20171231'
    fund_code = '000001.OF'
    path = 'E:\\3_Data\\4_fund_data\\7_fund_select_stock\\'
    fund_holding_all = Fund().get_fund_holding_all()
    fund_holding_date = fund_holding_all[fund_holding_all['Date'] == report_date]
    fund_holding = fund_holding_date[fund_holding_date['FundCode'] == fund_code]
    fund_holding.index = fund_holding['StockCode']
    fund_holding = fund_holding.ix[~fund_holding.index.duplicated(), :]
    fund_holding = fund_holding.dropna(subset=['Weight'])
    fund_holding = fund_holding.sort_values(by=['Weight'], ascending=False)

    file = os.path.join(path, "StockBarraDecomposeReturnQuarter", "StockBarraDecomposeReturnQuarter" + report_date + '.csv')
    stock_decompose_return = pd.read_csv(file, index_col=[0], encoding='gbk')

    stock_decompose_return = stock_decompose_return.ix[fund_holding.index, :]
    weight_mat = np.transpose(np.tile(fund_holding['Weight'].values, (len(stock_decompose_return.columns), 1)))
    weight_pd = pd.DataFrame(weight_mat, index=fund_holding.index, columns=stock_decompose_return.columns)



    ####################################################################################
    return result


def GetAllFundAllDateFactorAlphaFile(in_path, out_path, factor_name_list, date_series):

    # params
    ####################################################################################

    # in_path = 'E:\\3_Data\\4_fund_data\\7_fund_select_stock\\StockAlpha\\'
    # out_path = 'E:\\3_Data\\4_fund_data\\7_fund_select_stock\\FundSelectStockAlpha\\'
    #
    # factor_name_list = ["TotalMarketValue", "BP", "IncomeYOYDaily", "ROETTMDaily", "Industry"]
    #
    # beg_date = "20170530"
    # end_date = "20180630"
    # date_series = Date().get_normal_date_series(beg_date, end_date, "S")

    if not os.path.exists(out_path):
        os.makedirs(out_path)
    # read data
    ###################################################################################

    fund_code_list = Fund().get_fund_pool_code(date=report_date, name="基金持仓基准基金池")
    fund_code_list3 = Fund().get_fund_pool_code(date=report_date,name="量化基金")
    fund_code_list2 = Fund().get_fund_pool_code(date="20180630", name="东方红基金")
    fund_code_list.extend(fund_code_list2)
    fund_code_list.extend(fund_code_list3)
    result = pd.DataFrame([], index=fund_code_list, columns=[report_date])

    # cal fund alpha on style
    ####################################################################################
    for i in range(0, len(fund_code_list)):

        fund_code = fund_code_list[i]
    # read data
    ####################################################################################
    fund_holding_all = Fund().get_fund_holding_all()

    # cal alpha
    ####################################################################################
    for i_factor in range(len(factor_name_list)):

        factor_name = factor_name_list[i_factor]
        stock_alpha = GetStockAlphaAtFactorFile(in_path, factor_name)

        for i_date in range(len(date_series)):

            report_date = date_series[i_date]
            fund_holding_date = fund_holding_all[fund_holding_all['Date'] == report_date]
            alpha_date = GetAllFundAlphaOnFactorFile(stock_alpha, fund_holding_date, factor_name, report_date)
            if i_date == 0:
                new_data = alpha_date
            else:
                new_data = pd.concat([new_data, alpha_date], axis=1)

        new_data = new_data.T.dropna(how="all")
        filename = os.path.join(out_path, 'FundSelectStockAlpha_' + factor_name + '.csv')
        if os.path.exists(filename):
            old_data = pd.read_csv(filename, index_col=[0], encoding='gbk')
            old_data.index = old_data.index.map(str)
            result = pandas_add_row(old_data, new_data)
        else:
            result = new_data
        result.to_csv(filename)
    ####################################################################################


if __name__ == "__main__":

    # GetAllFundAlphaOnFactorFile
    ##################################################################################
    # report_date = '20171231'
    #
    # path = 'E:\\3_Data\\4_fund_data\\7_fund_select_stock\\StockAlpha\\'
    # factor_name = "TotalMarketValue"
    # stock_alpha = GetStockAlphaAtFactorFile(path, factor_name)
    #
    # fund_holding_all = Fund().get_fund_holding_all()
    # fund_holding_date = fund_holding_all[fund_holding_all['Date'] == report_date]
    #
    # data = GetAllFundAlphaOnFactorFile(stock_alpha, fund_holding_date, factor_name, report_date)
    # print(data)
    ##################################################################################

    # GetAllFundAllDateFactorAlphaFile
    ##################################################################################

    in_path = 'E:\\3_Data\\4_fund_data\\7_fund_select_stock\\StockAlpha\\'
    out_path = 'E:\\3_Data\\4_fund_data\\7_fund_select_stock\\FundSelectStockAlpha\\'

    factor_name_list = ["TotalMarketValue", "BP", "IncomeYOYDaily", "ROETTMDaily", "Industry"]

    beg_date = "20040101"
    end_date = "20180630"
    date_series = Date().get_normal_date_series(beg_date, end_date, "S")
    GetAllFundAllDateFactorAlphaFile(in_path, out_path, factor_name_list, date_series)
    ##################################################################################


def StockBarraDecomposeReturnQuarter(report_date):

    """

    """

    T = 20
    beg_date = Date().get_trade_date_offset(report_date, -T)
    end_date = Date().get_trade_date_offset(report_date, T)
    date_series = Date().get_trade_date_series(beg_date, end_date)

    result = {}
    for i in range(len(date_series)):

        date = date_series[i]
        residual = Barra().get_stock_residual_return_date(date)
        riskfactor = Barra().get_stock_riskfactor_return_date(date)

        all_return = pd.concat([residual, riskfactor], axis=1)
        result[date] = all_return

    result_panel = pd.Panel(result)
    pct_sum = result_panel.sum(axis=0)

    barra_name = Barra().get_factor_name(['STYLE'])
    barra_name = list(barra_name['NAME_EN'].values)
    pct_sum['STYLE'] = pct_sum.ix[:, barra_name].sum(axis=1)

    barra_name = Barra().get_factor_name(['INDUSTRY'])
    barra_name = list(barra_name['NAME_EN'].values)
    pct_sum['INDUSTRY'] = pct_sum.ix[:, barra_name].sum(axis=1)

    print(" StockBarraDecomposeReturnQuarter %s" % report_date)

    pct_sum.to_csv(file)


def StockBarraDecomposeReturnAllQuarter():

    """
    计算所有季报时间点 前后一个月 所有股票 拆分的 特异收益 风格收益 行业收益 和 市场收益
    """

    beg_date = "20040101"
    end_date = "20180815"
    date_series = Date().get_normal_date_series(beg_date, end_date, "Q")

    for i in range(len(date_series)):
        date = date_series[i]
        StockBarraDecomposeReturnQuarter(report_date=date)

    return True

if __name__ == '__main__':

    StockBarraDecomposeReturnAllQuarter()
