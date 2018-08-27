from quant.utility_fun.factor_preprocess import FactorPreProcess
from quant.stock.stock import Stock
from quant.stock.stock_factor_operate import StockFactorOperate


def cal_factor_barra_book_to_price(beg_date, end_date):

    """
    因子说明: 净资产/总市值, 根据最新财报更新数据
    披露日期 为 最近财报
    """

    # param
    #################################################################################
    raw_factor_name = 'RAW_CNE5_BOOK_TO_PRICE'
    factor_name = "NORMAL_CNE5_BOOK_TO_PRICE"

    # read data
    #################################################################################
    holder = Stock().get_factor_h5("TotalShareHoldeRequity", None, "primary_mfc")
    total_mv = Stock().get_factor_h5("TotalMarketValue", None, "alpha_dfc")

    # data precessing
    #################################################################################
    report_data = Stock().get_factor_h5("OperatingIncome" + "Daily", "ReportDate", 'primary_mfc')
    holder = StockFactorOperate().change_quarter_to_daily_with_disclosure_date(holder, report_data, beg_date, end_date)

    [holder, total_mv] = Stock().make_same_index_columns([holder, total_mv])
    holder_price = holder.div(total_mv)

    pb_data = holder_price.T.dropna(how='all').T

    # save data
    #############################################################################
    Stock().write_factor_h5(pb_data, raw_factor_name, 'barra_risk_dfc')
    pb_data = FactorPreProcess().remove_extreme_value_mad(pb_data)
    pb_data = FactorPreProcess().standardization_free_mv(pb_data)
    Stock().write_factor_h5(pb_data, factor_name, 'barra_risk_dfc')

    return pb_data
    #############################################################################


if __name__ == '__main__':

    from datetime import datetime

    beg_date = '2004-01-01'
    end_date = datetime.today()
    data = cal_factor_barra_book_to_price(beg_date, end_date)
    print(data)


