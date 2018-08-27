from quant.stock.stock import Stock
from datetime import datetime
from quant.stock.date import Date
from quant.fund.fund import Fund
import pandas as pd
from quant.param.param import Parameter
import os
from quant.utility_fun.pandas_fun import pandas_add_row

"""
计算股票型基金前十大重仓股的权重（其中包括一些灵活配置型的基金）
先用所有纰漏股票的权重大致筛一遍，然后再计算前十大重仓比例
"""


def stock_ratio_10(beg_date, end_date):

    factor_name = "Stock_Ratio_10"
    fund_holder = Fund().get_fund_holding_all()

    quarter_date = Date().get_last_fund_quarter_date(end_date)

    position_all = Fund().get_fund_factor("Stock_Ratio", date_list=[quarter_date], fund_pool=None).T
    position_all.columns = ['Stock_Weight']
    position_all = position_all[position_all['Stock_Weight'] > 65]

    code_list = list(position_all.index)
    date_list = Date().get_normal_date_series(beg_date=beg_date, end_date=end_date, period="Q")

    code_list.sort()
    date_list.sort()

    new_data = pd.DataFrame([], index=code_list, columns=date_list)

    for i_date in range(len(date_list)):

        for i_fund in range(len(code_list)):

            fund_code = code_list[i_fund]
            date = date_list[i_date]

            holder = fund_holder[fund_holder.FundCode == fund_code]
            holder = holder[holder.Date == date]
            holder = holder.sort_values(by=['Weight'], ascending=False)
            holder = holder.reset_index(drop=True)

            if len(holder) >= 10:
                holder = holder.ix[0:10, :]
                new_data.ix[fund_code, date] = holder.Weight.sum()
                print("计算 %s 在 %s 的前10大重仓股票为 %s" % (fund_code, date, holder.Weight.sum()))

    out_file = Parameter().get_read_file(factor_name)

    if os.path.exists(out_file):
        data = pd.read_csv(out_file, encoding='gbk', index_col=[0])
        data.index = data.index.map(str)
        data = pandas_add_row(data, new_data)
    else:
        print(" File No Exist ", factor_name)
        data = new_data

    data.to_csv(out_file)

if __name__ == "__main__":

    beg_date = "20041231"
    end_date = datetime.today()

    stock_ratio_10(beg_date, end_date)
