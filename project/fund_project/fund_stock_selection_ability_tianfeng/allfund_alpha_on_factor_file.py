from quant.project.fund_project.fund_stock_selection_ability_tianfeng.fund_alpha_on_factor_file import *
from quant.fund.fund import Fund
from quant.utility_fun.pandas_fun import pandas_add_row


def GetAllFundAlphaOnFactorFile(stock_alpha, fund_holding_date, factor_name, report_date):

    """
    计算所有基金 在某个日期 在 Factor 上的alpha
    """

    # params
    ###################################################################################
    # report_date = '20171231'
    # path = 'E:\\3_Data\\4_fund_data\\7_fund_select_stock\\StockAlpha\\'
    # factor_name = "TotalMarketValue"
    #
    # stock_alpha = GetStockAlphaAtFactorFile(path, factor_name)
    # fund_holding_all = Fund().get_fund_holding_all()
    # fund_holding_date = fund_holding_all[fund_holding_all['Date'] == report_date]

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

        fund_holding = fund_holding_date[fund_holding_date['FundCode'] == fund_code]
        fund_holding.index = fund_holding['StockCode']
        fund_holding = fund_holding.ix[~fund_holding.index.duplicated(), :]
        fund_holding = fund_holding.dropna(subset=['Weight'])

        alpha = GetFundAlphaAtFactorFile(stock_alpha, fund_holding, report_date)
        result.ix[fund_code, report_date] = alpha
        if fund_code == "229002.OF":
            print(fund_holding)
        print(" Alpha Fund %s At Date %s On Factor %s is %s" % (fund_code, report_date, factor_name, str(alpha)))

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

