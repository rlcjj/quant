import pandas as pd
import numpy as np
from quant.stock.stock import Stock
from quant.stock.date import Date
from quant.stock.stock_factor_operate import StockFactorOperate


def ROEQuarterDaily(beg_date, end_date):

    """
    因子说明: ROE 单季
    披露日期 为 最近财报
    """

    # param
    #################################################################################
    factor_name = 'ROEQuarterDaily'
    ipo_num = 90
    beg_date = Date().get_trade_date_offset(beg_date, -250)

    # read data
    #################################################################################
    net_profit = Stock().get_factor_h5("NetProfit", None, "primary_mfc")
    holder = Stock().get_factor_h5("TotalShareHoldeRequity", None, "primary_mfc")

    [net_profit, holder] = Stock().make_same_index_columns([net_profit, holder])
    roe = net_profit.div(holder)

    report_data = Stock().get_factor_h5("NetProfit" + "Daily", "ReportDate", 'primary_mfc')
    roe = StockFactorOperate().change_quarter_to_daily_with_disclosure_date(roe, report_data, beg_date, end_date)

    # data precessing
    #################################################################################
    pass

    # calculate data daily
    #################################################################################

    res = roe.T.dropna(how='all').T

    # save data
    #############################################################################
    Stock().write_factor_h5(res, factor_name, "alpha_dfc")
    return res
    #############################################################################


if __name__ == '__main__':

    from datetime import datetime

    beg_date = '2004-01-01'
    end_date = datetime.today()
    data = ROEQuarterDaily(beg_date, end_date)
    print(data)
