import pandas as pd
import statsmodels.api as sm
from quant.stock.stock import Stock
from quant.stock.date import Date
from quant.utility_fun.factor_preprocess import FactorPreProcess


def cal_factor_ROE(beg_date=None, end_date=None):

    """
    因子说明

    """

    # params
    ##########################################################################
    factor_name = "NORMAL_CNE5_NON_LINEAR_SIZE"

    size_data = Stock().get_factor_h5("NORMAL_CNE5_SIZE", None, 'barra_risk_dfc').T
    square_size_data = - size_data ** 2

    if beg_date is None:
        beg_date = size_data.index[0]
    if end_date is None:
        end_date = size_data.index[-1]

    date_series = Date().get_trade_date_series(beg_date, end_date)
    res_data = pd.DataFrame([], index=date_series, columns=size_data.columns)

    # calculate everyday
    ##########################################################################
    for i_index in range(len(date_series)):

        current_date = date_series[i_index]

        if current_date in list(square_size_data.index):
            print('Calculating Barra Risk factor %s at date %s' % (factor_name, current_date))
            regression_data = pd.concat([size_data.ix[i_index, :], square_size_data.ix[i_index, :]], axis=1)
            regression_data.columns = ['x', 'y']
            regression_data = regression_data.dropna()
            y = regression_data['y'].values
            x = regression_data['x'].values
            x_add = sm.add_constant(x)
            model = sm.OLS(y, x_add).fit()
            regression_data['res'] = regression_data['y'] - model.fittedvalues
            res_data.ix[i_index, :] = regression_data['res']
        else:
            print('Calculating Barra Risk factor %s at date %s is null' % (factor_name, current_date))

    res_data = res_data.T.dropna(how='all')
    res_data = FactorPreProcess().remove_extreme_value_mad(res_data)
    res_data = FactorPreProcess().standardization_free_mv(res_data)
    Stock().write_factor_h5(res_data, factor_name, 'barra_risk_dfc')


if __name__ == '__main__':

    from datetime import datetime
    beg_date = "20170101"
    end_date = datetime.today().strftime("%Y%m%d")
    cal_factor_ROE(beg_date, end_date)
