import pandas as pd
import numpy as np
from quant.stock.stock import Stock
from quant.stock.date import Date
from quant.stock.stock_factor_operate import StockFactorOperate


def BP(beg_date, end_date):

    """
    因子说明: 净资产/总市值, 根据最新财报更新数据
    披露日期 为 最近财报
    """

    # param
    #################################################################################
    factor_name = 'BP'
    ipo_num = 90

    # read data
    #################################################################################
    holder = Stock().get_factor_h5("TotalShareHoldeRequity", None, "primary_mfc")
    total_mv = Stock().get_factor_h5("TotalMarketValue", None, "alpha_dfc")

    report_data = Stock().get_factor_h5("OperatingIncome" + "Daily", "ReportDate", 'primary_mfc')
    holder = StockFactorOperate().change_quarter_to_daily_with_disclosure_date(holder, report_data, beg_date, end_date)

    [holder, total_mv] = Stock().make_same_index_columns([holder, total_mv])
    holder_price = holder.div(total_mv)

    # data precessing
    #################################################################################
    pass

    # calculate data daily
    #################################################################################

    res = holder_price.T.dropna(how='all').T

    # save data
    #############################################################################
    Stock().write_factor_h5(res, factor_name, "alpha_dfc")
    return res
    #############################################################################


if __name__ == '__main__':

    from datetime import datetime

    beg_date = '2004-01-01'
    end_date = datetime.today()
    data = BP(beg_date, end_date)
    print(data)
