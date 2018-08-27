import numpy as np
import pandas as pd
from quant.stock.stock import Stock
from quant.stock.date import Date
from quant.utility_fun.factor_preprocess import FactorPreProcess
import statsmodels.api as sm


def cal_factor_liquidity_stom(beg_date, end_date):

    """
    LIQUIDITY_STOM 最近21个交易日的换手率总和的对数值
    """

    # params
    ##################################################################################
    raw_factor_name = "RAW_CNE5_LIQUIDITY_STOM"
    factor_name = "NORMAL_CNE5_LIQUIDITY_STOM"
    M = 21

    # read data
    ##################################################################################
    turnover_daily = Stock().get_factor_h5("TurnOver_Daily", None, 'primary_mfc').T
    data_beg_date = Date().get_trade_date_offset(beg_date, -M)
    end_date = Date().change_to_str(end_date)
    turnover_daily = turnover_daily.ix[data_beg_date:end_date, :]
    turnover_month = turnover_daily.rolling(window=M).sum().applymap(np.log)
    turnover_month = turnover_month.ix[beg_date:end_date, :]
    turnover_month = turnover_month.replace(-np.inf, np.nan)
    turnover_month = turnover_month.replace(np.inf, np.nan)
    turnover_month = turnover_month.dropna(how='all').T

    # save data
    ##################################################################################
    Stock().write_factor_h5(turnover_month, raw_factor_name, 'barra_risk_dfc')
    turnover_month = FactorPreProcess().remove_extreme_value_mad(turnover_month)
    turnover_month = FactorPreProcess().standardization_free_mv(turnover_month)
    Stock().write_factor_h5(turnover_month, factor_name, 'barra_risk_dfc')
    ##################################################################################
    return turnover_month


def cal_factor_liquidity_stoq(beg_date, end_date):

    """
    LIQUIDITY_STOQ 最近63个交易日的换手率总和的对数值
    """

    # params
    ##################################################################################
    raw_factor_name = "RAW_CNE5_LIQUIDITY_STOM"
    factor_name = "NORMAL_CNE5_LIQUIDITY_STOM"
    Q = 63

    # read data
    ##################################################################################
    turnover_daily = Stock().get_factor_h5("TurnOver_Daily", None, 'primary_mfc').T
    data_beg_date = Date().get_trade_date_offset(beg_date, -M)
    end_date = Date().change_to_str(end_date)
    turnover_daily = turnover_daily.ix[data_beg_date:end_date, :]
    turnover_month = turnover_daily.rolling(window=M).sum().applymap(np.log)
    turnover_month = turnover_month.ix[beg_date:end_date, :]
    turnover_month = turnover_month.replace(-np.inf, np.nan)
    turnover_month = turnover_month.replace(np.inf, np.nan)
    turnover_month = turnover_month.dropna(how='all').T

    # save data
    ##################################################################################
    Stock().write_factor_h5(turnover_month, raw_factor_name, 'barra_risk_dfc')
    turnover_month = FactorPreProcess().remove_extreme_value_mad(turnover_month)
    turnover_month = FactorPreProcess().standardization_free_mv(turnover_month)
    Stock().write_factor_h5(turnover_month, factor_name, 'barra_risk_dfc')
    ##################################################################################
    return turnover_month


def cal_factor_liquidity(beg_date, end_date):

    """
    因子说明：流动性因子 LIQUIDITY

    LIQUIDITY_STOM 最近21个交易日的换手率总和的对数值

    LIQUIDITY_STOA 最近252个交易日的换手率总和的对数值
    LIQUIDITY = 0.35 * LIQUIDITY_STOM + 0.35 * LIQUIDITY_STOQ + 0.3 * LIQUIDITY_STOA
    LIQUIDITY 在对 SIZE 因子做回归取残差

    """

    # params
    ##################################################################################
    factor_name = "NORMAL_CNE5_LIQUIDITY"



    A = 252

    beg_date = Date().change_to_str(beg_date)
    end_date = Date().change_to_str(end_date)
    beg_date =

    # params
    ##################################################################################
    turnover_daily = Stock().get_factor_h5("TurnOver_Daily", None, 'primary_mfc').T
    turnover_month = turnover_daily.rolling(window=M).sum().applymap(np.log)
    turnover_quarter = (turnover_daily.rolling(window=Q).sum() / 3.0).applymap(np.log)
    turnover_yearly = (turnover_daily.rolling(window=A).sum() / 12.0).applymap(np.log)


    turnover_quarter = turnover_quarter.dropna(how='all').T
    turnover_yearly = turnover_yearly.dropna(how='all').T


    Stock().write_factor_h5(turnover_quarter, "RAW_CNE5_LIQUIDITY_STOQ", 'barra_risk_dfc')
    Stock().write_factor_h5(turnover_yearly, "RAW_CNE5_LIQUIDITY_STOA", 'barra_risk_dfc')


    turnover_quarter = FactorPreProcess().remove_extreme_value_mad(turnover_quarter)
    turnover_quarter = FactorPreProcess().standardization_free_mv(turnover_quarter)
    turnover_yearly = FactorPreProcess().remove_extreme_value_mad(turnover_yearly)
    turnover_yearly = FactorPreProcess().standardization_free_mv(turnover_yearly)

    Stock().write_factor_h5(turnover_quarter, "NORMAL_CNE5_LIQUIDITY_STOQ", 'barra_risk_dfc')
    Stock().write_factor_h5(turnover_yearly, "NORMAL_CNE5_LIQUIDITY_STOA", 'barra_risk_dfc')

    turnover = 0.35 * turnover_month + 0.35 * turnover_quarter + 0.3 * turnover_yearly
    turnover = turnover.T.dropna(how='all').T

    size_data = Stock().get_factor_h5("NORMAL_CNE5_SIZE", None, 'barra_risk_dfc')
    [size_data, turnover] = FactorPreProcess().make_same_index_columns([size_data, turnover])

    turnover_res = pd.DataFrame([], index=turnover.index, columns=turnover.columns)

    for i_index in range(len(turnover.columns)):

        date = turnover.columns[i_index]
        print('Calculating Barra Risk factor %s at date %s' % (factor_name, date))
        regression_data = pd.concat([size_data[date], turnover[date]], axis=1)
        regression_data.columns = ['x', 'y']
        regression_data = regression_data.dropna()
        y = regression_data['y'].values
        x = regression_data['x'].values
        x_add = sm.add_constant(x)
        model = sm.OLS(y, x_add).fit()
        regression_data['res'] = regression_data['y'] - model.fittedvalues
        turnover_res[date] = regression_data['res']

    turnover_res = FactorPreProcess().remove_extreme_value_mad(turnover_res)
    turnover_res = FactorPreProcess().standardization_free_mv(turnover_res)
    Stock().write_factor_h5(turnover_res, factor_name, 'barra_risk_dfc')


if __name__ == '__main__':

    cal_factor_liquidity()
