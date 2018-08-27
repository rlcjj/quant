from quant.utility_fun.factor_preprocess import FactorPreProcess
from quant.stock.stock_factor_read_write import StockFactorReadWrite


class StockFactor(StockFactorReadWrite,
                  FactorPreProcess):

    """
    读取写入 股票因子数据
    因子数据的预先处理

    StockFactorReadWrite()
    FactorPreProcess()

    """

    def __init__(self):

        StockFactorReadWrite.__init__(self)
        FactorPreProcess.__init__(self)

if __name__ == '__main__':

    # print(StockFactor().get_factor_h5("Beta", None, "alpha_mfc"))
    # print(StockFactor().get_factor_h5())
    data = StockFactor().get_factor_h5("PriceCloseAdjust", None, "alpha_dfc")
    print(data)
    StockFactor().write_factor_h5(data, "PriceCloseAdjust", None, "alpha_dfc")
