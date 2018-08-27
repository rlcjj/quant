import pandas as pd
import numpy as np
from quant.stock.stock import Stock
from quant.stock.date import Date
from quant.stock.stock_factor_operate import StockFactorOperate


def EPQuarter(beg_date, end_date):

    """
    因子说明: 当季净利润EP
    披露日期 为 最近财报
    """

    # param
    #################################################################################
    factor_name = 'EPQuarter'
    ipo_num = 90

    # read data
    #################################################################################
    netprofit = Stock().get_factor_h5("NetProfit", None, "primary_mfc")
    total_mv = Stock().get_factor_h5("TotalMarketValue", None, "alpha_dfc")

    netprofit = StockFactorOperate().change_quarter_to_daily_with_report_date(netprofit, beg_date, end_date)

    [total_mv, netprofit] = Stock().make_same_index_columns([total_mv, netprofit])
    total_mv /= 100000000

    ratio = netprofit.div(total_mv)

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
    data = EPQuarter(beg_date, end_date)
    print(data)
