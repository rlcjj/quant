import pandas as pd
import numpy as np
from quant.stock.stock import Stock
from quant.stock.date import Date
from quant.stock.stock_factor_operate import StockFactorOperate


def GrossProfitYOYDaily(beg_date, end_date):

    """
    因子说明: 当季毛利润的同比增长
    披露日期 为 最近财报
    """

    # param
    #################################################################################
    factor_name = 'GrossProfitYOYDaily'
    ipo_num = 90

    # read data
    #################################################################################
    income = Stock().get_factor_h5("OperatingIncome", None, "primary_mfc").T
    cost = Stock().get_factor_h5("OperatingCost", None, "primary_mfc").T
    [income, cost] = Stock().make_same_index_columns([income, cost])
    gross_profit = income - cost
    gross_profit_4 = gross_profit.shift(4)
    gross_profit_yoy = gross_profit / gross_profit_4 - 1.0

    gross_profit_yoy = gross_profit_yoy.T
    report_data = Stock().get_factor_h5("OperatingIncomeDaily", "ReportDate", 'primary_mfc')
    gross_profit_yoy = StockFactorOperate().change_quarter_to_daily_with_disclosure_date(gross_profit_yoy, report_data, beg_date, end_date)

    # data precessing
    #################################################################################
    pass

    # calculate data daily
    #################################################################################

    res = gross_profit_yoy.T.dropna(how='all').T

    # save data
    #############################################################################
    Stock().write_factor_h5(res, factor_name, "alpha_dfc")
    return res
    #############################################################################


if __name__ == '__main__':

    from datetime import datetime

    beg_date = '2004-01-01'
    end_date = datetime.today()
    data = GrossProfitYOYDaily(beg_date, end_date)
    print(data)
