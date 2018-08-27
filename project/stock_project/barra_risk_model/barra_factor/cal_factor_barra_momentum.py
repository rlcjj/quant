import numpy as np
import pandas as pd
from quant.stock.stock import Stock
from quant.utility_fun.factor_preprocess import FactorPreProcess
from quant.stock.date import Date
from quant.utility_fun.weight_fun import exponential_weight


def cal_factor_barra_momentum(beg_date=None, end_date=None):

    """
    因子说明：长期动量减去短期动量

    """
    # params
    ######################################################################################
    raw_factor_name = 'RAW_CNE5_MOMENTUM'
    factor_name = "NORMAL_CNE5_MOMENTUM"
    L = 21
    T = 504
    half_life = 126
    Min_T = 400

    # read data
    #################################################################################
    pct = Stock().get_factor_h5("Pct_chg", None, 'primary_mfc').T
    pct = np.log(pct / 100.0 + 1.0) * 100

    if beg_date is None:
        beg_date = pct.index[0]
    if end_date is None:
        end_date = pct.index[-1]

    # calculate data daily
    #################################################################################
    date_series = Date().get_trade_date_series(beg_date, end_date)
    res_data = pd.DataFrame([], index=date_series, columns=pct.columns)

    for i_index in range(len(date_series)):

        current_date = date_series[i_index]
        data_end = Date().get_trade_date_offset(current_date, -L+1)
        data_beg = Date().get_trade_date_offset(current_date, -L-T+2)
        pct_period = pct.ix[data_beg: data_end, :]
        pct_period = pct_period.dropna(how='all')

        if len(pct_period) > Min_T:
            print('Calculating Barra Risk factor %s at date %s' % (factor_name, current_date))
            weight = exponential_weight(len(pct_period), half_life)
            weight_mat = np.tile(np.row_stack(weight), (1, len(pct_period.columns)))
            weight_pd = pd.DataFrame(weight_mat, index=pct_period.index, columns=pct_period.columns)
            pct_weight = pct_period.mul(weight_pd)
            res_data.ix[current_date, :] = pct_weight.sum(skipna=False)
        else:
            print('Calculating Barra Risk factor %s at date %s is null' % (factor_name, current_date))

    res_data = res_data.dropna(how='all').T
    Stock().write_factor_h5(res_data, raw_factor_name, 'barra_risk_dfc')
    res_data = FactorPreProcess().remove_extreme_value_mad(res_data)
    res_data = FactorPreProcess().standardization_free_mv(res_data)
    Stock().write_factor_h5(res_data, factor_name, 'barra_risk_dfc')


if __name__ == '__main__':

    from datetime import datetime
    beg_date = "20180101"
    end_date = datetime.today().strftime("%Y%m%d")
    cal_factor_barra_momentum(beg_date, end_date)
