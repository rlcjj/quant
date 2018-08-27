import pandas as pd
import numpy as np
from quant.stock.stock import Stock
from quant.stock.date import Date
from quant.stock.stock_factor_operate import StockFactorOperate


def EBITIncomeBiasDaily(beg_date, end_date):

    """
    因子说明: 息税前利润/营业总收入 环比增长率
    披露日期 为 最近财报
    """

    # param
    #################################################################################
    factor_name = 'EBITIncomeBiasDaily'
    ipo_num = 90

    # read data
    #################################################################################
    ebit = Stock().get_factor_h5("EBIT", None, "primary_mfc")
    income = Stock().get_factor_h5("OperatingIncome", None, "primary_mfc")
    [income, ebit] = Stock().make_same_index_columns([income, ebit])
    margin = ebit.div(income).T
    margin = margin.diff().T

    report_data = Stock().get_factor_h5("NetProfit" + "Daily", "ReportDate", 'primary_mfc')
    margin = StockFactorOperate().change_quarter_to_daily_with_disclosure_date(margin, report_data, beg_date, end_date)

    # data precessing
    #################################################################################
    pass

    # calculate data daily
    #################################################################################
    res = margin.T.dropna(how='all').T

    # save data
    #############################################################################
    Stock().write_factor_h5(res, factor_name, "alpha_dfc")
    return res
    #############################################################################


if __name__ == '__main__':

    from datetime import datetime

    beg_date = '2004-01-01'
    end_date = datetime.today()
    data = EBITIncomeBiasDaily(beg_date, end_date)
    print(data)
