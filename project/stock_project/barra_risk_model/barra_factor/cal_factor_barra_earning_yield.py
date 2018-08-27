import os
from quant.param.param import Parameter
from quant.stock.stock import Stock
from quant.utility_fun.factor_preprocess import FactorPreProcess


def cal_predicted_earnings_to_price_ratio():

    """
    预期盈利 / 总市值
    """
    raw_factor_name = 'RAW_CNE5_EARNING_YIELD_PREDICTED_EARNINGS_TO_PRICE_RATIO'
    factor_name = 'NORMAL_CNE5_EARNING_YIELD_PREDICTED_EARNINGS_TO_PRICE_RATIO'


def cal_cash_earnings_to_price_ratio():

    """
    经营性现金流净额 / 总市值
    """
    raw_factor_name = 'RAW_CNE5_EARNING_YIELD_CASH_EARNINGS_TO_PRICE_RATIO'
    factor_name = 'NORMAL_CNE5_EARNING_YIELD_CASH_EARNINGS_TO_PRICE_RATIO'


def cal_trailing_earnings_to_price_ratio():

    """
    归母净利润TTM / 总市值
    """
    raw_factor_name = 'RAW_CNE5_EARNING_YIELD_TRAILING_EARNINGS_TO_PRICE_RATIO'
    factor_name = 'NORMAL_CNE5_EARNING_YIELD_TRAILING_EARNINGS_TO_PRICE_RATIO'



def cal_earning_yield():

    """
    0.68 * 预期盈利 / 总市值 +  0.21 * 经营性现金流净额 / 总市值 + 0.11 * 归母净利润TTM / 总市值
    """

    predicted_ep_name = 'NORMAL_CNE5_EARNING_YIELD_PREDICTED_EARNINGS_TO_PRICE_RATIO'
    predicted_ep = get_barra_standard_data(predicted_ep_name)

    cp_name = 'NORMAL_CNE5_EARNING_YIELD_CASH_EARNINGS_TO_PRICE_RATIO'
    cp = get_barra_standard_data(cp_name)

    ep_name = 'NORMAL_CNE5_EARNING_YIELD_TRAILING_EARNINGS_TO_PRICE_RATIO'
    ep = get_barra_standard_data(ep_name)

    # earning_yield = 0.68 * predicted_ep + 0.21 * cp + 0.11 * ep
    earning_yield = 0.50 * cp + 0.50 * ep



if __name__ == '__main__':

    cal_cash_earnings_to_price_ratio()
    cal_predicted_earnings_to_price_ratio()
    cal_trailing_earnings_to_price_ratio()
    cal_earning_yield()
