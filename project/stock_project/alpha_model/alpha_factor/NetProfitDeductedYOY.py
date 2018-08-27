import pandas as pd
import numpy as np
from quant.stock.stock import Stock
from quant.stock.date import Date
from quant.stock.stock_factor_operate import StockFactorOperate


def NetProfitDeductedYOY(beg_date, end_date):

    """
    因子说明: 归属母公司股东的净利润-扣除非经常损益(同比增长率)
    披露日期 为 最近财报
    """

    # param
    #################################################################################
    factor_name = 'NetProfitDeductedYOY'
    ipo_num = 90

    # read data
    #################################################################################
    netprofit_yoy = Stock().get_factor_h5("YoyNetProfit_Deducted", None, "primary_mfc")
    netprofit_yoy = StockFactorOperate().change_quarter_to_daily_with_report_date(netprofit_yoy, beg_date, end_date)

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
    data = NetProfitDeductedYOY(beg_date, end_date)
    print(data)
