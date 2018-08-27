def cal_factor_Long_Term_ROE():

    name = '净资产收益率'
    roe_data = get_cal_data(name)
    roe_data = roe_data.dropna(how='all')

    long_term_roe_data = roe_data.rolling(window=5*252, ).mean() - roe_data.rolling(window=5*252).std()
    out_path = 'E:\\4_代码\\pycharmprojects\\2_风险模型BARRA\\data\\barra_data\\raw_data\\'
    long_term_roe_data = long_term_roe_data.dropna(how='all')
    long_term_roe_data.to_csv(out_path + 'RAW_Long_Term_ROE.csv')

    long_term_roe_data = remove_extreme_value_mad_pandas(long_term_roe_data)
    long_term_roe_data = normal_pandas(long_term_roe_data)
    out_path = 'E:\\4_代码\\pycharmprojects\\2_风险模型BARRA\\data\\barra_data\\standardization_data\\'
    long_term_roe_data.to_csv(out_path + 'NORMAL_Long_Term_ROE.csv')


if __name__ == '__main__':

    cal_factor_Long_Term_ROE()


