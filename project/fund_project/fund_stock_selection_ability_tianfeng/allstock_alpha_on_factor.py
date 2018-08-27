from quant.project.fund_project.fund_stock_selection_ability_tianfeng.stock_alpha_on_factor import *
from quant.utility_fun.pandas_fun import pandas_add_row


def GetAllStockAllDateAlpha(path, factor_name_list, date_series):

    ####################################################################################
    # path = 'E:\\3_Data\\4_fund_data\\7_fund_select_stock\\FundSelectStockAlpha\\'
    # factor_name_list = ["TotalMarketValue", "BP", "IncomeYOYDaily", "ROETTMDaily"]
    # beg_date = "20170530"
    # end_date = "20180630"
    # date_series = Date().get_normal_date_series(beg_date, end_date, "S")

    # params
    ####################################################################################
    code_list = Stock().get_all_stock_code_now()
    if not os.path.exists(path):
        os.makedirs(path)

    # read data
    ####################################################################################
    industry = Stock().get_factor_h5("industry_citic1", None, "primary_mfc")
    price = Stock().get_factor_h5("PriceCloseAdjust", None, 'alpha_dfc')

    # cal fund alpha all date all fund all factor
    ####################################################################################
    for i_factor in range(len(factor_name_list)):

        factor_name = factor_name_list[i_factor]
        factor = Stock().get_factor_h5(factor_name, None, "alpha_dfc")
        new_data = pd.DataFrame([], index=code_list, columns=date_series)

        for i_date in range(len(date_series)):
            report_date = date_series[i_date]
            for i_stock in range(len(code_list)):
                code = code_list[i_stock]
                alpha = GetStockAlphaAtFactor(factor, price, code, report_date)
                new_data.ix[code, report_date] = alpha
                print(code, report_date, factor_name, alpha)

        new_data = new_data.T.dropna(how="all")
        filename = os.path.join(path, 'StockAlpha_' + factor_name + '.csv')
        if os.path.exists(filename):
            old_data = pd.read_csv(filename, index_col=[0], encoding='gbk')
            old_data.index = old_data.index.map(str)
            result = pandas_add_row(old_data, new_data)
        else:
            result = new_data
        result.to_csv(filename)

    # cal fund alpha all date all fund on industry
    ####################################################################################
    factor_name = "Industry"
    new_data = pd.DataFrame([], index=code_list, columns=date_series)

    for i_date in range(len(date_series)):
        report_date = date_series[i_date]
        for i_stock in range(len(code_list)):
            code = code_list[i_stock]
            alpha = GetStockAlphaAtIndustry(industry, price, code, report_date)
            new_data.ix[code, report_date] = alpha
            print(code, report_date, factor_name, alpha)

    new_data = new_data.T.dropna(how="all")
    filename = os.path.join(path, 'StockAlpha_' + factor_name + '.csv')
    if os.path.exists(filename):
        old_data = pd.read_csv(filename, index_col=[0], encoding='gbk')
        old_data.index = old_data.index.map(str)
        result = pandas_add_row(old_data, new_data)
    else:
        result = new_data
    result.to_csv(filename)
    ####################################################################################




if __name__ == '__main__':

    path = 'E:\\3_Data\\4_fund_data\\7_fund_select_stock\\StockAlpha\\'
    factor_name_list = ["TotalMarketValue", "BP", "IncomeYOYDaily", "ROETTMDaily"]
    beg_date = "20040101"
    end_date = "20051230"
    date_series = Date().get_normal_date_series(beg_date, end_date, "S")
    print(date_series)

    # GetAllStockAllDateAlpha(path, factor_name_list, date_series)

    code_list = Stock().get_all_stock_code_now()
    if not os.path.exists(path):
        os.makedirs(path)

    # read data
    ####################################################################################
    industry = Stock().get_factor_h5("industry_citic2", None, "primary_mfc")
    price = Stock().get_factor_h5("PriceCloseAdjust", None, 'alpha_dfc')
    factor_name = "Industry2"
    new_data = pd.DataFrame([], index=code_list, columns=date_series)

    for i_date in range(len(date_series)):
        report_date = date_series[i_date]
        for i_stock in range(len(code_list)):
            code = code_list[i_stock]
            alpha = GetStockAlphaAtIndustry(industry, price, code, report_date)
            new_data.ix[code, report_date] = alpha
            print(code, report_date, factor_name, alpha)

    new_data = new_data.T.dropna(how="all")
    filename = os.path.join(path, 'StockAlpha_' + factor_name + '.csv')
    if os.path.exists(filename):
        old_data = pd.read_csv(filename, index_col=[0], encoding='gbk')
        old_data.index = old_data.index.map(str)
        result = pandas_add_row(old_data, new_data)
    else:
        result = new_data
    result.to_csv(filename)
