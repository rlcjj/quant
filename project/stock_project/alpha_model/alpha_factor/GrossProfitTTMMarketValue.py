import pandas as pd
import numpy as np
from quant.stock.stock import Stock
from quant.stock.date import Date
from quant.stock.stock_factor_operate import StockFactorOperate


def GrossProfitTTMMarketValue(beg_date, end_date):

    """
    因子说明: 毛利润TTM/总市值
    披露日期 为 同一披露财报
    """

    # param
    #################################################################################
    factor_name = 'GrossProfitTTMMarketValue'
    ipo_num = 90

    # read data
    #################################################################################
    income = Stock().get_factor_h5("OperatingIncome", None, "primary_mfc")
    cost = Stock().get_factor_h5("OperatingCost", None, "primary_mfc")
    total_mv = Stock().get_factor_h5("TotalMarketValue", None, "alpha_dfc")

    [income, cost] = Stock().make_same_index_columns([income, cost])
    gross_profit = income - cost

    gross_profit = StockFactorOperate().change_quarter_to_daily_with_report_date(gross_profit, beg_date, end_date)

    [total_mv, gross_profit] = Stock().make_same_index_columns([total_mv, gross_profit])
    total_mv /= 100000000

    ratio = gross_profit.div(total_mv)

    # data precessing
    #################################################################################
    pass

    # calculate data daily
    #################################################################################

    res = ratio.T.dropna(how='all').T

    # save data
    #############################################################################
    Stock().write_factor_h5(res, factor_name, "alpha_dfc")
    return res
    #############################################################################


if __name__ == '__main__':

    from datetime import datetime

    beg_date = '2004-01-01'
    end_date = datetime.today()
    data = GrossProfitTTMMarketValue(beg_date, end_date)
    print(data)
