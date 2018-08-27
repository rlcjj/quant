import pandas as pd
import numpy as np
from quant.stock.stock import Stock
from quant.stock.date import Date
from quant.stock.stock_factor_operate import StockFactorOperate


def CFNOYOYDaily(beg_date, end_date):

    """
    因子说明: 经营活动产生的现金流量净额(同比增长率)
    披露日期 为 最近财报
    """

    # param
    #################################################################################
    factor_name = 'CFNOYOYDaily'
    ipo_num = 90

    # read data
    #################################################################################
    operate_cash_yoy = Stock().get_factor_h5("NetOperateCashFlowYoY", None, "primary_mfc")

    report_data = Stock().get_factor_h5("OperatingIncome" + "Daily", "ReportDate", 'primary_mfc')
    operate_cash_yoy = StockFactorOperate().change_quarter_to_daily_with_disclosure_date(operate_cash_yoy, report_data, beg_date, end_date)

    # data precessing
    #################################################################################
    pass

    # calculate data daily
    #################################################################################

    res = operate_cash_yoy.T.dropna(how='all').T

    # save data
    #############################################################################
    Stock().write_factor_h5(res, factor_name, "alpha_dfc")
    return res
    #############################################################################


if __name__ == '__main__':

    from datetime import datetime

    beg_date = '2004-01-01'
    end_date = datetime.today()
    data = CFNOYOYDaily(beg_date, end_date)
    print(data)
