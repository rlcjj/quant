import numpy as np
import pandas as pd
import statsmodels.api as sm


def rolling_ewm_mean(x, halflife, adjust):

    x_pd = pd.DataFrame(x, columns=['x'])
    x_pd['rolling'] = x_pd['x'].ewm(halflife=halflife, adjust=adjust).std() * np.sqrt(252)
    val = x_pd.ix[len(x_pd) - 1, 'rolling']
    return val


def cal_factor_barra_dastd():

    name = '涨跌幅'
    pct = get_format_data(name)
    pct /= 100.0

    data = pct.ewm(halflife=42, min_periods=252, adjust=False).std() * np.sqrt(252) * 100
    data = data.dropna(how='all')
    out_path = 'E:\\4_代码\\pycharmprojects\\2_风险模型BARRA\\data\\barra_data\\raw_data\\'
    data.to_csv(out_path + 'RAW_CNE5_RESIDUAL_VOLATILITY_DASTD.csv')

    data = remove_extreme_value_mad_pandas(data)
    data = normal_pandas(data)
    out_path = 'E:\\4_代码\\pycharmprojects\\2_风险模型BARRA\\data\\barra_data\\standardization_data\\'
    data.to_csv(out_path + 'NORMAL_CNE5_RESIDUAL_VOLATILITY_DASTD.csv')


def cal_factor_barra_hsigma():

    name = '涨跌幅'
    pct = get_format_data(name)
    index_pct = get_index_pct("881001.WI") * 100

    name = 'RAW_CNE5_BETA'
    beta = get_barra_raw_data(name)

    res_vol = pd.DataFrame([], index=pct.index, columns=pct.columns)

    for i_code in range(len(pct.columns)):

        code = pct.columns[i_code]
        print(code)
        pct_code = pct.ix[:, code]
        beta_code = beta.ix[:, code]
        concat_data = pd.concat([index_pct, pct_code, beta_code], axis=1)
        concat_data = concat_data.dropna()
        concat_data.columns = ['mfc', 'code', 'beta']
        concat_data['res'] = concat_data['code'] - concat_data['beta'] * concat_data['mfc']
        res_vol.ix[:, code] = concat_data['res'].ewm(halflife=63, min_periods=252, adjust=False).std() * np.sqrt(252)

    res_vol = res_vol.dropna(how='all')
    out_path = 'E:\\4_代码\\pycharmprojects\\2_风险模型BARRA\\data\\barra_data\\raw_data\\'
    res_vol.to_csv(out_path + 'RAW_CNE5_RESIDUAL_VOLATILITY_HSIGMA.csv')

    res_vol = remove_extreme_value_mad_pandas(res_vol)
    res_vol = normal_pandas(res_vol)
    out_path = 'E:\\4_代码\\pycharmprojects\\2_风险模型BARRA\\data\\barra_data\\standardization_data\\'
    res_vol.to_csv(out_path + 'NORMAL_CNE5_RESIDUAL_VOLATILITY_HSIGMA.csv')


def cal_factor_barra_residual_volatility():

    name = 'NORMAL_CNE5_RESIDUAL_VOLATILITY_DASTD'
    dastd = get_barra_standard_data(name)

    name = 'NORMAL_CNE5_RESIDUAL_VOLATILITY_HSIGMA'
    hsigma = get_barra_standard_data(name)

    residual_volatility = dastd * 0.74 + hsigma + 0.10 * hsigma
    residual_volatility = residual_volatility.dropna(how='all')

    name = 'NORMAL_CNE5_SIZE'
    size_data = get_barra_standard_data(name)

    name = 'NORMAL_CNE5_BETA'
    beta_data = get_barra_standard_data(name)

    date_series = list(set(list(size_data.index)) & set(list(residual_volatility.index))
                       & set(list(beta_data.index)))
    date_series.sort()

    residual_volatility_res = pd.DataFrame([], index=date_series, columns=residual_volatility.columns)

    for i_index in range(len(date_series)):

        date = date_series[i_index]
        print(date)
        regression_data = pd.concat([size_data.ix[date, :], beta_data.ix[date, :],
                                     residual_volatility.ix[date, :]], axis=1)
        regression_data.columns = ['size', 'beta', 'y']
        regression_data = regression_data.dropna()
        y = regression_data['y'].values
        x = regression_data[['size', 'beta']].values
        x_add = sm.add_constant(x)
        model = sm.OLS(y, x_add).fit()
        regression_data['res'] = regression_data['y'] - model.fittedvalues
        residual_volatility_res.ix[date, :] = regression_data['res']

    residual_volatility_res = remove_extreme_value_mad_pandas(residual_volatility_res)
    residual_volatility_res = normal_pandas(residual_volatility_res)
    out_path = 'E:\\4_代码\\pycharmprojects\\2_风险模型BARRA\\data\\barra_data\\standardization_data\\'
    residual_volatility_res.to_csv(out_path + 'NORMAL_CNE5_RESIDUAL_VOLATILITY.csv')


if __name__ == '__main__':

    cal_factor_barra_dastd()
    cal_factor_barra_hsigma()
    cal_factor_barra_residual_volatility()
