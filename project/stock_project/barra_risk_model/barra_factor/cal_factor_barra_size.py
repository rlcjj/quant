
import numpy as np
from quant.stock.stock import Stock
from quant.stock.date import Date
from quant.utility_fun.factor_preprocess import FactorPreProcess


def cal_factor_barra_size(beg_date, end_date):

    """
    因子说明 计算总市值的对数值
    """

    # param
    #################################################################################
    raw_factor_name = 'RAW_CNE5_SIZE'
    factor_name = 'NORMAL_CNE5_SIZE'
    beg_date = Date().change_to_str(beg_date)
    end_date = Date().change_to_str(end_date)

    # read data
    #################################################################################
    price_unadjust = Stock().get_factor_h5("Price_Unadjust", None, "primary_mfc")
    free_share = Stock().get_factor_h5("TotalShare", None, "primary_mfc")
    price_unadjust = price_unadjust.ix[:, beg_date:end_date]
    total_share = free_share.ix[:, beg_date:end_date]

    # calculate data
    #################################################################################
    [price_unadjust, total_share] = FactorPreProcess().make_same_index_columns([price_unadjust, total_share])
    total_market_value = price_unadjust.mul(free_share)
    log_size_data = np.log(total_market_value)

    # save data
    #################################################################################
    Stock().write_factor_h5(log_size_data, raw_factor_name, 'barra_risk_dfc')

    log_size_data = FactorPreProcess().remove_extreme_value_mad(log_size_data)
    log_size_data = FactorPreProcess().standardization_free_mv(log_size_data)
    Stock().write_factor_h5(log_size_data, factor_name, 'barra_risk_dfc')
    return log_size_data
    #################################################################################


if __name__ == "__main__":

    from datetime import datetime

    beg_date = '20040101'
    end_date = datetime.today()
    cal_factor_barra_size(beg_date, end_date)


