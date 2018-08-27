import pandas as pd
import numpy as np
from quant.stock.stock import Stock
from quant.stock.date import Date
from quant.stock.stock_factor_operate import StockFactorOperate


def TotalAssetTurnBias(beg_date, end_date):

    # 总资产周转率环减
    # 因子说明：当季度（营业收入TTM / 总资产加权）- 本季度（营业收入TTM / 总资产加权）
    # TTM 为统一财报期

    # param
    #################################################################################
    factor_name = 'TotalAssetTurnBias'
    ipo_num = 90

    # read data
    #################################################################################

    income_q = Stock().get_factor_h5("OperatingIncome", None, 'primary_mfc')
    total_asset = Stock().get_factor_h5("TotalAsset", None, 'primary_mfc')
    total_asset = StockFactorOperate().change_single_quarter_to_ttm_quarter(total_asset)
    total_asset /= 4.0

    turnover = income_q.div(total_asset)
    turnover_qoq = turnover.T.diff().T
    turnover_qoq = StockFactorOperate().change_quarter_to_daily_with_report_date(turnover_qoq, beg_date, end_date)

    # code set & date set
    #################################################################################
    pass

    res = turnover_qoq.T.dropna(how='all').T

    # save data
    #############################################################################
    Stock().write_factor_h5(res, factor_name, "alpha_dfc")
    return res
    #############################################################################

if __name__ == '__main__':

    from datetime import datetime
    beg_date = '2004-01-01'
    end_date = datetime.today()
    data = TotalAssetTurnBias(beg_date, end_date)
    print(data)