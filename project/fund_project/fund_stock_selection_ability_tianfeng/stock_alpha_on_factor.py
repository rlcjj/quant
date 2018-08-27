import pandas as pd
import numpy as np
from quant.stock.date import Date
from quant.stock.stock import Stock
from quant.fund.fund import Fund
import os


def GetStockAlphaAtFactor(factor, price, code, report_date):

    """
    计算某只股票在某个因子上的alpha
    假设股票A的市值为1000亿，选取1000亿市值附近的2M只股票
    计算在年报和半年报前后2T个交易日的收益率
    这2M只股票等权涨跌幅和股票A涨跌幅的差，就是股票A在市值因子上的Alpha收益
    """

    # params
    ###################################################################
    M = 50
    T = 20

    # get data
    ###################################################################
    beg_date = Date().get_trade_date_offset(end_date=report_date, offset_num=-T)
    end_date = Date().get_trade_date_offset(end_date=report_date, offset_num=T)
    print(beg_date, end_date)

    if (end_date in price.columns) and (beg_date in price.columns):

        # get pct and factor value
        ###################################################################
        price_end = price[end_date]
        price_beg = price[beg_date]

        pct_period = price_end / price_beg - 1.0
        factor_mean = factor.ix[:, beg_date:end_date].mean(axis=1)

        # concat_data
        ###################################################################
        concat_data = pd.concat([factor_mean, pct_period], axis=1)
        concat_data.columns = ["factor_mean", 'pct_period']
        concat_data = concat_data.dropna(how='all')
        concat_data = concat_data.sort_values(by=['factor_mean'])

        if code in concat_data.index:

            # get position
            ###################################################################
            position = list(concat_data.index).index(code)
            position_beg = max(0, position - M)
            position_end = min(len(concat_data), position + M + 1)

            # get alpha
            ###################################################################
            select_data = concat_data.iloc[position_beg:position_end, :]
            pct_mean = select_data['pct_period'].median()
            pct_code = select_data.ix[code, 'pct_period']
            alpha = pct_code - pct_mean
            print(pct_code, pct_mean)

        else:
            alpha = np.nan
    else:
        alpha = np.nan

    return alpha


def GetStockAlphaAtIndustry(industry, price, code, report_date):

    """
    计算某只股票A在行业上的alpha
    同行业股票等权涨跌幅和股票A涨跌幅的差，就是股票A在行业上的Alpha收益
    """

    # params
    ###################################################################
    T = 20

    # get data
    ###################################################################
    beg_date = Date().get_trade_date_offset(end_date=report_date, offset_num=-T)
    end_date = Date().get_trade_date_offset(end_date=report_date, offset_num=T)

    if (end_date in price.columns) and (beg_date in price.columns):

        # get pct and factor value
        ###################################################################
        price_end = price[end_date]
        price_beg = price[beg_date]
        pct_period = price_end / price_beg - 1.0

        # get alpha
        ###################################################################
        if code in industry.index:

            industry_code = industry.ix[code, end_date]
            industry_date = industry[end_date]
            industry_code_list = list(industry_date[industry_date == industry_code].index)

            # get industry stock
            ###################################################################
            concat_data = pd.DataFrame(pct_period[industry_code_list].values,
                                       index=pct_period[industry_code_list].index)
            concat_data.columns = ['pct_period']
            print(concat_data)
            pct_mean = concat_data['pct_period'].median()
            pct_code = pct_period[code]
            print(pct_code, pct_mean)

            alpha = pct_code - pct_mean

        else:
            alpha = np.nan
    else:
        alpha = np.nan

    return alpha

if __name__ == "__main__":

    ######################################################################################################
    code = '601318.SH'
    report_date = "20171231"

    #######################################################################################################
    factor_name_list = ["TotalMarketValue", "BP", "IncomeYOYDaily", "ROETTMDaily"]
    price = Stock().get_factor_h5("PriceCloseAdjust", None, 'alpha_dfc')

    #######################################################################################################
    for i in range(len(factor_name_list)):
        factor_name = factor_name_list[i]
        factor = Stock().get_factor_h5(factor_name, None, "alpha_dfc")
        alpha = GetStockAlphaAtFactor(factor, price, code, report_date)
        print(" Alpha Stock %s At Date %s On Factor %s is %s" % (code, report_date, factor_name, str(alpha)))

    #######################################################################################################
    industry = Stock().get_factor_h5("industry_citic1", None, "primary_mfc")
    price = Stock().get_factor_h5("PriceCloseAdjust", None, 'alpha_dfc')
    alpha = GetStockAlphaAtIndustry(industry, price, code, report_date)
    print(" Alpha Stock %s At Date %s On Factor %s is %s" % (code, report_date, "Industry", str(alpha)))
    ########################################################################################################




