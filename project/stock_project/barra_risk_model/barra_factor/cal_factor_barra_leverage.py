def cal_factor_barra_leverage_market_leverage():

    name = 'TotalLiabilityDaily'
    total_debt = get_h5_data(name)

    name = 'TotalAssetDaily'
    total_asset = get_h5_data(name)

    debt_to_asset = total_debt.div(total_asset)
    debt_to_asset = debt_to_asset.dropna(how='all')

    out_path = 'E:\\4_代码\\pycharmprojects\\2_风险模型BARRA\\data\\barra_data\\raw_data\\'
    debt_to_asset.to_csv(out_path + 'RAW_CNE5_LEVERAGE_MARKET_LEVERAGE.csv')

    debt_to_asset = remove_extreme_value_mad_pandas(debt_to_asset)
    debt_to_asset = normal_pandas(debt_to_asset)
    out_path = 'E:\\4_代码\\pycharmprojects\\2_风险模型BARRA\\data\\barra_data\\standardization_data\\'
    debt_to_asset.to_csv(out_path + 'NORMAL_CNE5_LEVERAGE_MARKET_LEVERAGE.csv')


def cal_factor_barra_leverage():

    name = 'NORMAL_CNE5_LEVERAGE_MARKET_LEVERAGE'
    leverage = get_barra_standard_data(name)
    leverage = leverage.dropna(how='all')

    out_path = 'E:\\4_代码\\pycharmprojects\\2_风险模型BARRA\\data\\barra_data\\raw_data\\'
    leverage.to_csv(out_path + 'RAW_CNE5_LEVERAGE.csv')

    leverage = remove_extreme_value_mad_pandas(leverage)
    leverage = normal_pandas(leverage)
    out_path = 'E:\\4_代码\\pycharmprojects\\2_风险模型BARRA\\data\\barra_data\\standardization_data\\'
    leverage.to_csv(out_path + 'NORMAL_CNE5_LEVERAGE.csv')


if __name__ == '__main__':

    cal_factor_barra_leverage_market_leverage()
    cal_factor_barra_leverage()
