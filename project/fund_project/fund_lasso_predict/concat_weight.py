from quant.fund.fund import Fund
from quant.stock.date import Date
from datetime import datetime
from quant.project.fund_project.fund_lasso_predict.cal_ols_stock_weight import get_ols_stock_weight_all_date
import pandas as pd


def concat_weight():

    beg_date = "20041231"
    end_date = datetime.today()
    out_path = "E:\\3_数据\\4_fund_data\\4_fund_holding_predict\\ols_stock_weight\\"

    quarter_date = '20180630'
    fund_pool = Fund().get_fund_pool_code(quarter_date, "东方红基金")

    for i_fund in range(len(fund_pool)):

        fund_code = fund_pool[i_fund]
        data = get_ols_stock_weight_all_date(fund_code)
        data = data.fillna(0.0)

        if i_fund == 0:
            res = data
        else:
            res = res.add(data, fill_value=0)

    res /= len(fund_pool)
    res.to_csv(out_path + '东方红预测持仓.csv')

if __name__ == '__main__':

    concat_weight()

