import os
from datetime import datetime
import pandas as pd
from quant.fund.fund import Fund
from quant.param.param import Parameter
from quant.stock.date import Date


def fund_pool_update(date):

    fund_pool_wind_dict = {"普通股票型基金": 2001010101000000,
                           "偏股混合型基金": 2001010201000000,
                           "港股通基金": 1000024255000000,
                           "量化基金": 1000023322000000}

    for name, pool_number in fund_pool_wind_dict.items():

        print(name, pool_number)
        Fund().load_fund_pool(date, name, pool_number)

    ptgp = Fund().get_fund_pool_all(date, "普通股票型基金")
    pghh = Fund().get_fund_pool_all(date, "偏股混合型基金")
    ggt = Fund().get_fund_pool_all(date, "港股通基金")
    lh = Fund().get_fund_pool_all(date, "量化基金")

    fund_pool = set(ptgp['wind_code'].values) | set(pghh['wind_code'].values)
    fund_pool = set(fund_pool) - set(ggt['wind_code'].values) - set(lh['wind_code'].values)

    data = pd.concat([ptgp, pghh], axis=0)
    data = data.reset_index(drop=True)

    data_final = data[data['wind_code'].map(lambda x:x in fund_pool)]
    data_final['if_A'] = data_final['sec_name'].map(Fund.if_a_fund)
    data_final = data_final[data_final['if_A'] == 'A类基金']
    data = data_final.reset_index(drop=True)

    name = "基金持仓基准基金池"
    out_path = Parameter().get_load_out_file("Fund_Pool")
    out_sub_path = os.path.join(out_path, name)
    if not os.path.exists(out_sub_path):
        os.makedirs(out_sub_path)
    file = name + '_' + date + '.csv'
    out_file = os.path.join(out_sub_path, file)
    data.to_csv(out_file)


def fund_pool_update_all():

    date_series = Date().get_normal_date_series("20040101", datetime.today(), 'Q')
    for i_date in range(56, len(date_series)-1):
        report_date = date_series[i_date]
        fund_pool_update(report_date)
        print(report_date)


if __name__ == '__main__':

    # date = '20180331'
    # fund_pool_update(date)
    fund_pool_update_all()
