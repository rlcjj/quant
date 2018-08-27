import pandas as pd
import numpy as np
from quant.stock.stock import Stock
from quant.stock.date import Date


def ReturnIntradayLn(beg_date, end_date):

    """
    因子说明：日内收益率 的对数 今天收盘 / 今天开盘价
    权重为线性加权
    """

    # param
    #################################################################################
    factor_name = 'ReturnIntradayLn'
    ipo_num = 90

    # read data
    #################################################################################
    close = Stock().get_factor_h5("PriceCloseAdjust", None, "alpha_dfc")
    open = Stock().get_factor_h5("PriceOpenAdjust", None, "alpha_dfc")

    # data precessing
    #################################################################################
    [close, open] = Stock().make_same_index_columns([close, open])

    # calculate data daily
    #################################################################################
    date_series = Date().get_trade_date_series(beg_date, end_date)
    date_series = list(set(date_series) & set(close.columns))
    date_series.sort()

    res = pd.DataFrame([], columns=date_series, index=close.index)

    for i in range(0, len(date_series)):

        current_date = date_series[i]

        if current_date in close.columns:

            print('Calculating factor %s at date %s' % (factor_name, current_date))

            close_today = close[current_date]
            open_today = open[current_date]
            data_date = (close_today / open_today).map(np.log) * 100
            res[current_date] = data_date
        else:
            print('Calculating factor %s at date %s is null' % (factor_name, current_date))

    res = res.T.dropna(how='all').T

    # save data
    #############################################################################
    Stock().write_factor_h5(res, factor_name, "alpha_dfc")
    return res
    #############################################################################


if __name__ == '__main__':

    from datetime import datetime

    beg_date = '2004-01-01'
    end_date = datetime.today()
    data = ReturnIntradayLn(beg_date, end_date)
    print(data)

