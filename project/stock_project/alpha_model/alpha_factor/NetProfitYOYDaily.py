import pandas as pd
import numpy as np
from quant.stock.stock import Stock
from quant.stock.date import Date
from quant.stock.stock_factor_operate import StockFactorOperate


def NetProfitYOYDaily(beg_date, end_date):

    """
    因子说明: 当季净利润的同比增长
    披露日期 为 最近财报
    """

    # param
    #################################################################################
    factor_name = 'NetProfitYOYDaily'
    ipo_num = 90

    # read data
    #################################################################################
    net_profit = Stock().get_factor_h5("NetProfit", None, "primary_mfc").T
    net_profit_4 = net_profit.shift(4)
    netprofit_yoy = net_profit / net_profit_4 - 1.0

    netprofit_yoy = netprofit_yoy.T
    report_data = Stock().get_factor_h5("NetProfit" + "Daily", "ReportDate", 'primary_mfc')
    netprofit_yoy = StockFactorOperate().change_quarter_to_daily_with_disclosure_date(netprofit_yoy, report_data, beg_date, end_date)

    # data precessing
    #################################################################################
    pass

    # calculate data daily
    #################################################################################

    res = netprofit_yoy.T.dropna(how='all').T

    # save data
    #############################################################################
    Stock().write_factor_h5(res, factor_name, "alpha_dfc")
    return res
    #############################################################################


if __name__ == '__main__':

    from datetime import datetime

    beg_date = '2004-01-01'
    end_date = datetime.today()
    data = NetProfitYOYDaily(beg_date, end_date)
    print(data)
