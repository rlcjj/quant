import pandas as pd
import numpy as np
from quant.stock.stock import Stock
from quant.stock.date import Date


def VolumeIR(beg_date, end_date):

    """
    因子说明：-1* 过去40天成交额标准差 / 过去40天成交额均值
    """
    # param
    #################################################################################
    LongTerm = 40
    HalfTerm = int(LongTerm/2)
    factor_name = "VolumeIR"
    ipo_num = 90

    # read data
    #################################################################################
    trade_amount = Stock().get_factor_h5("TradeAmount", None, "primary_mfc").T

    # code set & date set
    #################################################################################
    trade_amount = trade_amount.fillna(0.0)

    # calculate data daily
    #################################################################################
    date_series = Date().get_trade_date_series(beg_date, end_date)
    date_series = list(set(trade_amount.index) & set(date_series))
    date_series.sort()

    for i in range(0, len(date_series)):

        current_date = date_series[i]
        data_beg_date = Date().get_trade_date_offset(current_date, -(LongTerm-1))
        amount_before = trade_amount.ix[data_beg_date:current_date, :]

        if len(amount_before) >= int(0.8*LongTerm):

            print('Calculating factor %s at date %s' % (factor_name, current_date))
            zero_number = amount_before.applymap(lambda x: 1.0 if x == 0.0 else 0.0).sum()
            code_filter_list = (zero_number[zero_number < HalfTerm]).index

            trade_amount_pre = trade_amount.ix[data_beg_date:current_date, code_filter_list]
            trade_amount_pre_std = trade_amount_pre.std()
            trade_amount_pre_mean = trade_amount_pre.mean()
            trade_amount_pre_cv = - trade_amount_pre_std / trade_amount_pre_mean
            trade_amount_pre_cv = pd.DataFrame(trade_amount_pre_cv.values,
                                               columns=[current_date], index=trade_amount_pre.columns)
        else:
            print('Calculating factor %s at date %s is null' % (factor_name, current_date))
            trade_amount_pre_cv = pd.DataFrame([], columns=[current_date], index=trade_amount.columns)

        if i == 0:
            res = trade_amount_pre_cv
        else:
            res_add = trade_amount_pre_cv
            res = pd.concat([res, res_add], axis=1)

    res = res.T.dropna(how='all').T
    # save data
    #############################################################################
    Stock().write_factor_h5(res, factor_name, "alpha_dfc")
    return res
    #############################################################################


if __name__ == '__main__':

    from datetime import datetime
    beg_date = '2018-01-01'
    end_date = datetime.today()
    data = VolumeIR(beg_date, end_date)
    print(data)
