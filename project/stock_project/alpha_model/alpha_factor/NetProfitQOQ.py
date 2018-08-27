import pandas as pd
import numpy as np
from quant.stock.stock import Stock
from quant.stock.date import Date
from quant.stock.stock_factor_operate import StockFactorOperate


def NetProfitQOQ(beg_date, end_date):

    """
    因子说明: 净利润环比增长率
    披露日期 为 最近财报
    """

    # param
    #################################################################################
    factor_name = 'NetProfitQOQ'
    ipo_num = 90

    # read data
    #################################################################################
    netprofit = Stock().get_factor_h5("NetProfit", None, "primary_mfc").T
    netprofit_1 = netprofit.shift(1)
    netprofit_qoq = netprofit.div(netprofit_1) - 1.0
    netprofit_qoq = netprofit_qoq.T

    netprofit_qoq = StockFactorOperate().change_quarter_to_daily_with_report_date(netprofit_qoq, beg_date, end_date)

    # data precessing
    #################################################################################
    pass

    # calculate data daily
    #################################################################################
    res = netprofit_qoq.T.dropna(how='all').T

    # save data
    #############################################################################
    Stock().write_factor_h5(res, factor_name, "alpha_dfc")
    return res
    #############################################################################


if __name__ == '__main__':

    from datetime import datetime

    beg_date = '2004-01-01'
    end_date = datetime.today()
    data = NetProfitQOQ(beg_date, end_date)
    print(data)
