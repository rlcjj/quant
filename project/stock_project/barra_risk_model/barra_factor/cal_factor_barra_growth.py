

def cal_factor_barra_growth_income_yoy():

    name = 'income_yoy_daily'
    income_yoy = get_h5_data(name)

    out_path = 'E:\\4_代码\\pycharmprojects\\2_风险模型BARRA\\data\\barra_data\\raw_data\\'
    income_yoy.to_csv(out_path + 'RAW_CNE5_GROWTH_INCOME_YOY.csv')

    income_yoy = remove_extreme_value_mad_pandas(income_yoy)
    income_yoy = normal_pandas(income_yoy)
    out_path = 'E:\\4_代码\\pycharmprojects\\2_风险模型BARRA\\data\\barra_data\\standardization_data\\'
    income_yoy.to_csv(out_path + 'NORMAL_CNE5_GROWTH_INCOME_YOY.csv')


def cal_factor_barra_growth_grossprofit_yoy():

    name = 'grossprofit_yoy_daily'
    grossprofit_yoy = get_h5_data(name)

    out_path = 'E:\\4_代码\\pycharmprojects\\2_风险模型BARRA\\data\\barra_data\\raw_data\\'
    grossprofit_yoy.to_csv(out_path + 'RAW_CNE5_GROWTH_GROSSPROFIT_YOY.csv')

    grossprofit_yoy = remove_extreme_value_mad_pandas(grossprofit_yoy)
    grossprofit_yoy = normal_pandas(grossprofit_yoy)
    out_path = 'E:\\4_代码\\pycharmprojects\\2_风险模型BARRA\\data\\barra_data\\standardization_data\\'
    grossprofit_yoy.to_csv(out_path + 'NORMAL_CNE5_GROWTH_GROSSPROFIT_YOY.csv')


def cal_factor_barra_growth_netprofit_yoy():

    name = 'netprofit_yoy_daily'
    netprofit_yoy = get_h5_data(name)

    out_path = 'E:\\4_代码\\pycharmprojects\\2_风险模型BARRA\\data\\barra_data\\raw_data\\'
    netprofit_yoy.to_csv(out_path + 'RAW_CNE5_GROWTH_NETPROFIT_YOY.csv')

    netprofit_yoy = remove_extreme_value_mad_pandas(netprofit_yoy)
    netprofit_yoy = normal_pandas(netprofit_yoy)
    out_path = 'E:\\4_代码\\pycharmprojects\\2_风险模型BARRA\\data\\barra_data\\standardization_data\\'
    netprofit_yoy.to_csv(out_path + 'NORMAL_CNE5_GROWTH_NETPROFIT_YOY.csv')


def cal_factor_barra_growth():

    name = 'NORMAL_CNE5_GROWTH_INCOME_YOY'
    income_yoy = get_barra_standard_data(name)

    name = 'NORMAL_CNE5_GROWTH_NETPROFIT_YOY'
    netprofit_yoy = get_barra_standard_data(name)

    name = 'NORMAL_CNE5_GROWTH_GROSSPROFIT_YOY'
    grossprofit_yoy = get_barra_standard_data(name)

    growth = 0.35 * income_yoy + 0.35 * grossprofit_yoy + 0.30 * netprofit_yoy

    out_path = 'E:\\4_代码\\pycharmprojects\\2_风险模型BARRA\\data\\barra_data\\raw_data\\'
    growth.to_csv(out_path + 'RAW_CNE5_GROWTH.csv')

    growth = remove_extreme_value_mad_pandas(growth)
    growth = normal_pandas(growth)
    print(growth.index[len(growth) - 1])
    out_path = 'E:\\4_代码\\pycharmprojects\\2_风险模型BARRA\\data\\barra_data\\standardization_data\\'
    growth.to_csv(out_path + 'NORMAL_CNE5_GROWTH.csv')


if __name__ == '__main__':

    cal_factor_barra_growth_grossprofit_yoy()
    cal_factor_barra_growth_income_yoy()
    cal_factor_barra_growth_netprofit_yoy()
    cal_factor_barra_growth()
