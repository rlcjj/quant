import pandas as pd
import numpy as np
from quant.stock.stock import Stock
from quant.stock.date import Date
from quant.stock.stock_factor_operate import StockFactorOperate


def DividendYield12m(beg_date, end_date):

    """
    因子说明: 最近12月的股息率
    披露日期 为 最近财报
    """

    # param
    #################################################################################
    factor_name = 'DividendYield12m'
    ipo_num = 90

    # read data
    #################################################################################
    dividendyield2 = Stock().get_factor_h5("dividendyield2", None, "primary_mfc")
    beg_date = Date().change_to_str(beg_date)
    end_date = Date().change_to_str(end_date)
    dividendyield2 = dividendyield2.ix[:, beg_date:end_date]

    # data precessing
    #################################################################################
    pass

    # calculate data daily
    #################################################################################
    res = dividendyield2.T.dropna(how='all').T

    # save data
    #############################################################################
    Stock().write_factor_h5(res, factor_name, "alpha_dfc")
    return res
    #############################################################################


if __name__ == '__main__':

    from datetime import datetime

    beg_date = '2004-01-01'
    end_date = datetime.today()
    data = DividendYield12m(beg_date, end_date)
    print(data)
