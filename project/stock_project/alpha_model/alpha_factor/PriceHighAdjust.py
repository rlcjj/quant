from quant.stock.stock import Stock
from quant.stock.date import Date
from quant.utility_fun.factor_preprocess import FactorPreProcess


def PriceHighAdjust(beg_date, end_date):

    """
    因子说明 ：复权最高价格
    """

    # param
    #################################################################################
    factor_name = "PriceHighAdjust"
    beg_date = Date().change_to_str(beg_date)
    end_date = Date().change_to_str(end_date)

    # read data
    #################################################################################
    price_unadjust = Stock().get_factor_h5("PriceHighUnadjust", None, "primary_mfc")
    price_facor = Stock().get_factor_h5("AdjustFactor", None, "primary_mfc")
    price_unadjust = price_unadjust.ix[:, beg_date:end_date]
    price_facor = price_facor.ix[:, beg_date:end_date]

    # calculate data
    #################################################################################
    [price_unadjust, price_facor] = FactorPreProcess().make_same_index_columns([price_unadjust, price_facor])
    price_adjust = price_unadjust.mul(price_facor)

    # save data
    #############################################################################
    Stock().write_factor_h5(price_adjust, factor_name, "alpha_dfc")
    return price_adjust


if __name__ == "__main__":

    from datetime import datetime
    beg_date = '2002-01-01'
    end_date = datetime.today()
    data = PriceHighAdjust(beg_date, end_date)
    print(data)

