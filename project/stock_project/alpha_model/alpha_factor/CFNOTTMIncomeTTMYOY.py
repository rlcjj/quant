import pandas as pd
import numpy as np
from quant.stock.stock import Stock
from quant.stock.date import Date
from quant.stock.stock_factor_operate import StockFactorOperate


def CFNOTTMIncomeTTMYOY(beg_date, end_date):

    """
    因子说明: 经营活动现金净流量(TTM)/营业收入(TTM)  同比增速
    披露日期 为 最近财报
    """

    # param
    #################################################################################
    factor_name = 'CFNOTTMIncomeTTMYOY'
    ipo_num = 90

    # read data
    #################################################################################
    operate_cash = Stock().get_factor_h5("NetOperateCashFlow", None, "primary_mfc")
    income = Stock().get_factor_h5("OperatingIncome", None, "primary_mfc")

    operate_cash_ttm = StockFactorOperate().change_single_quarter_to_ttm_quarter(operate_cash)
    income_ttm = StockFactorOperate().change_single_quarter_to_ttm_quarter(income)

    [operate_cash_ttm, income_ttm] = Stock().make_same_index_columns([operate_cash_ttm, income_ttm])
    ratio = operate_cash_ttm.div(income_ttm).T
    ratio_4 = ratio.shift(4)
    ratio_yoy = ratio / ratio_4 - 1.0
    ratio_yoy = ratio_yoy.T
    ratio_yoy = StockFactorOperate().change_quarter_to_daily_with_report_date(ratio_yoy, beg_date, end_date)

    # data precessing
    #################################################################################
    pass

    # calculate data daily
    #################################################################################

    res = ratio_yoy.T.dropna(how='all').T

    # save data
    #############################################################################
    Stock().write_factor_h5(res, factor_name, "alpha_dfc")
    return res
    #############################################################################


if __name__ == '__main__':

    from datetime import datetime

    beg_date = '2004-01-01'
    end_date = datetime.today()
    data = CFNOTTMIncomeTTMYOY(beg_date, end_date)
    print(data)
