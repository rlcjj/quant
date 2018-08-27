from quant.stock.stock_factor import StockFactor
from quant.stock.stock_static import StockStatic
from quant.stock.stcok_pool import StockPool
from datetime import datetime


class Stock(StockPool, StockStatic, StockFactor):

    def __init__(self):

        StockPool.__init__(self)
        StockStatic.__init__(self)
        StockFactor.__init__(self)


if __name__ == '__main__':

    # StockPool
    ################################################################################
    # Stock().load_all_stock_code_now()
    print(Stock().get_all_stock_code_now())

    # StockStatic
    ################################################################################
    date = datetime(2018, 7, 6)
    Stock().load_trade_status_today()
    print(Stock().get_trade_status_date(date))

    Stock().load_free_market_value_date(date)
    print(Stock().get_free_market_value_date(date))

    Stock().load_ipo_date()
    print(Stock().get_ipo_date())
    ################################################################################

    # StockFactor
    print(Stock().get_factor_h5())

