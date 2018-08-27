from quant.project.fund_project.fund_stock_selection_ability_tianfeng.allfund_alpha_on_factor_file import *
from quant.project.fund_project.fund_stock_selection_ability_tianfeng.allstock_alpha_on_factor import *


if __name__ == '__main__':

    # GetAllStockAllDateAlpha
    ################################################################################
    path = 'E:\\3_Data\\4_fund_data\\7_fund_select_stock\\StockAlpha\\'
    factor_name_list = ["TotalMarketValue", "BP", "IncomeYOYDaily", "ROETTMDaily"]
    beg_date = "20140101"
    end_date = "20170730"
    date_series = Date().get_normal_date_series(beg_date, end_date, "S")
    print(date_series)

    GetAllStockAllDateAlpha(path, factor_name_list, date_series)

    # GetAllFundAllDateFactorAlphaFile
    ################################################################################

    in_path = 'E:\\3_Data\\4_fund_data\\7_fund_select_stock\\StockAlpha\\'
    out_path = 'E:\\3_Data\\4_fund_data\\7_fund_select_stock\\FundSelectStockAlpha\\'

    factor_name_list = ["TotalMarketValue", "BP", "IncomeYOYDaily", "ROETTMDaily", "Industry"]

    beg_date = "20170530"
    end_date = "20180630"
    date_series = Date().get_normal_date_series(beg_date, end_date, "S")
    GetAllFundAllDateFactorAlphaFile(in_path, out_path, factor_name_list, date_series)
    ################################################################################