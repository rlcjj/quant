import pandas as pd
import numpy as np
from quant.stock.stock import Stock
from quant.stock.date import Date
from quant.stock.stock_factor_operate import StockFactorOperate


def GrossProfitRateBiasDaily(beg_date, end_date):

    """
    因子说明：当季 毛利率TTM - 上季度 毛利率TTM
    毛利率TTM = （营业收入TTM - 营业成本TTM）/ 营业收入TTM
    披露日期 为 最近财报
    """

    # param
    #################################################################################
    factor_name = 'GrossProfitRateBiasDaily'
    ipo_num = 90

    # read data
    #################################################################################
    income = Stock().get_factor_h5("OperatingIncome", None, "primary_mfc")
    cost = Stock().get_factor_h5("OperatingCost", None, "primary_mfc")
    income_ttm = StockFactorOperate().change_single_quarter_to_ttm_quarter(income).T
    cost_ttm = StockFactorOperate().change_single_quarter_to_ttm_quarter(cost).T

    gross_margin = (income_ttm - cost_ttm) / cost_ttm

    gross_margin_qoq = gross_margin.diff().T

    report_data = Stock().get_factor_h5("OperatingCost" + "Daily", "ReportDate", 'primary_mfc')
    gross_margin_qoq = StockFactorOperate().\
        change_quarter_to_daily_with_disclosure_date(gross_margin_qoq, report_data, beg_date, end_date)

    # data precessing
    #################################################################################
    pass

    # calculate data daily
    #################################################################################

    res = gross_margin_qoq.T.dropna(how='all').T

    # save data
    #############################################################################
    Stock().write_factor_h5(res, factor_name, "alpha_dfc")
    return res
    #############################################################################


if __name__ == '__main__':

    from datetime import datetime

    beg_date = '2004-01-01'
    end_date = datetime.today()
    data = GrossProfitRateBiasDaily(beg_date, end_date)
    print(data)
