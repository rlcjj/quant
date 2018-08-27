import pandas as pd
import numpy as np
from quant.stock.stock import Stock
from quant.stock.date import Date
from quant.stock.stock_factor_operate import StockFactorOperate


def AverageHolder(beg_date, end_date):

    """
    因子说明：户均持股比例
    就是持股户数的倒数
    去掉新股和未上市企业
    按照统一的季报日期
    在wind查证 户均持股比例应该是不定期公布的 并不一定是季度公布的数据 603978.SH

    """

    # param
    #################################################################################
    factor_name = 'AverageHolder'
    ipo_num = 90

    # read data
    #################################################################################
    holder = Stock().get_factor_h5("HolderAvgPct", None, "primary_mfc")
    holder = StockFactorOperate().change_quarter_to_daily_with_report_date(holder, beg_date, end_date)
    # ipo = Stock().get_factor_h5("ipo_normal_days", None, "primary_dfc")

    # data precessing
    #################################################################################
    # [holder, ipo] = Stock().make_same_index_columns([holder, ipo])
    # holder[~(ipo > ipo_num)] = np.nan
    # holder[holder > 1.0] = np.nan

    res = holder.T.dropna(how='all').T

    # save data
    #############################################################################
    Stock().write_factor_h5(res, factor_name, "alpha_dfc")
    return res
    #############################################################################


if __name__ == '__main__':

    from datetime import datetime

    beg_date = '2004-01-01'
    end_date = datetime.today()
    data = AverageHolder(beg_date, end_date)
    print(data)

