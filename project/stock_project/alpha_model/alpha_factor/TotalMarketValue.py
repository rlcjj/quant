from quant.stock.stock import Stock
from quant.stock.date import Date
from quant.utility_fun.factor_preprocess import FactorPreProcess


def TotalMarketValue(beg_date, end_date):

    """
    计算股票的总市值 = 总股本 * 未复权股价
    """

    # param
    #################################################################################
    factor_name = "TotalMarketValue"
    beg_date = Date().change_to_str(beg_date)
    end_date = Date().change_to_str(end_date)

    # read data
    #################################################################################
    price_unadjust = Stock().get_factor_h5("Price_Unadjust", None, "primary_mfc")
    free_share = Stock().get_factor_h5("TotalShare", None, "primary_mfc")
    price_unadjust = price_unadjust.ix[:, beg_date:end_date]
    free_share = free_share.ix[:, beg_date:end_date]

    # calculate data
    #################################################################################
    [price_unadjust, free_share] = FactorPreProcess().make_same_index_columns([price_unadjust, free_share])
    free_market_value = price_unadjust.mul(free_share)
    # free_market_value /= 100000000.0

    # save data
    ################################################################################
    Stock().write_factor_h5(free_market_value, factor_name, "alpha_dfc")
    return free_market_value
    ################################################################################


if __name__ == "__main__":

    from datetime import datetime

    beg_date = '2004-01-01'
    end_date = datetime.today()
    TotalMarketValue(beg_date, end_date)
