import pandas as pd
import numpy as np
from quant.stock.stock import Stock
from quant.stock.date import Date
from quant.stock.stock_factor_operate import StockFactorOperate


def NetprofitYOYBias(beg_date, end_date):

    """
    因子说明：当季 净利润 同比增长 的 环减值
    TTM 为统一财报期
    """

    # param
    #################################################################################
    factor_name = 'NetprofitYOYBias'
    ipo_num = 90

    # read data
    #################################################################################
    profit = Stock().get_factor_h5("NetProfit", None, "primary_mfc").T
    profit_4 = profit.shift(4)
    profit_yoy = profit / profit_4 - 1.0
    profit_yoy_speed = profit_yoy.diff().T
    profit_yoy_speed = StockFactorOperate().change_quarter_to_daily_with_report_date(profit_yoy_speed, beg_date, end_date)

    # data precessing
    #################################################################################
    pass

    # calculate data daily
    #################################################################################

    res = profit_yoy_speed.T.dropna(how='all').T

    # save data
    #############################################################################
    Stock().write_factor_h5(res, factor_name, "alpha_dfc")
    return res
    #############################################################################


if __name__ == '__main__':

    from datetime import datetime

    beg_date = '2004-01-01'
    end_date = datetime.today()
    data = NetprofitYOYBias(beg_date, end_date)
    print(data)
