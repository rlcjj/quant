from quant.stock.stock import Stock
from datetime import datetime
from quant.stock.date import Date
from quant.fund.fund import Fund
import pandas as pd
from quant.param.param import Parameter

"""
持仓比较集中、换手不高
业绩长期优秀稳定
"""

def lasso_fund_pool():

    fund_holder = Fund().get_fund_holding_all()
    position_all = Fund().get_fund_factor("Stock_Ratio", date_list=["20180331"], fund_pool=None)
    code_list = list(code_list['wind_code'].values)
    date_list = Date().get_normal_date_series(beg_date="20041231", end_date=datetime.today(), period="Q")

    code_list.sort()
    date_list.sort()

    result = pd.DataFrame([], index=code_list, columns=date_list)

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
                result.ix[fund_code, date] = holder.Weight.sum()
                print("计算 %s 在 %s 的前10大重仓股票为 %s" % (fund_code, date, holder.Weight.sum()))

    result.to_csv(path + '')

if __name__
