from quant.mfc.mfc_data import MfcData
from quant.stock.date import Date
import pandas as pd
from datetime import datetime
import os
from WindPy import w
w.start()


def GenerateFundReturnAndCost(fund_code, beg_date, end_date, name, data_path):

    """
    生成 Barra Aegis Portfolio Analyst 所需要的真实组合收益和成本文件
    """
    beg_date = Date().change_to_str(beg_date)
    end_date = Date().change_to_str(end_date)
    cost_ratio = 0.26

    data = w.wsd(fund_code, "NAV_adj_return1", beg_date, end_date, "")
    fund_pct = pd.DataFrame(data.Data, columns=data.Times, index=['Fund_' + name]).T
    fund_pct = fund_pct.dropna(how='all')
    fund_pct.index = fund_pct.index.map(Date().change_to_str)

    index = ['!ID', '!TYPE']
    index.extend(list(fund_pct.index))
    res = pd.DataFrame([], index=index, columns=['Fund_' + name, "Cost_" + name])
    res.ix['!ID', 'Fund_' + name] = 'Fund_' + name
    res.ix['!TYPE', 'Fund_' + name] = 'R'

    res.ix['!ID', 'Cost_' + name] = 'Cost_' + name
    res.ix['!TYPE', 'Cost_' + name] = 'TCP'

    res.loc[fund_pct.index, 'Fund_' + name] = fund_pct['Fund_' + name]
    res.loc[fund_pct.index, 'Cost_' + name] = cost_ratio

    res.to_csv(data_path + 'FundReturn_Cost_' + name + '.csv', header=None)


def GenerateFundReturnAndCostAll():

    """
    生成 Barra Aegis Portfolio Analyst 所需要的真实组合收益和成本文件
    每个组合生成一个文件
    """

    param_path = 'D:\\Program Files (x86)\\anaconda\\Lib\\site-packages\\quant\\project\\mfc_holding_project\\attribute_barra\\'
    data_path = 'E:\\3_Data\\8_barra_contribution_data\\Aegis Performance Analysis\\TD_FundReturn_Cost\\'
    param_file = os.path.join(param_path, 'generate_user_portfolio_param.xlsx')
    param = pd.read_excel(param_file)

    for i_fund in range(len(param)):

        name = param.ix[i_fund, 'fund_name_en']
        beg_date = param.ix[i_fund, 'beg_date']
        end_date = datetime.today().strftime('%Y%m%d')
        fund_code = param.ix[i_fund, 'fund_code']
        GenerateFundReturnAndCost(fund_code, beg_date, end_date, name, data_path)

if __name__ == '__main__':

    GenerateFundReturnAndCostAll()
