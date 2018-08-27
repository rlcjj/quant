from quant.mfc.mfc_data import MfcData
from quant.stock.date import Date
from quant.utility_fun.code_format import stock_code_add_postfix, stock_code_drop_postfix
import pandas as pd
from datetime import datetime
import os


def GenerateUserPortfolio(date, name, portfolio_name, path):

    """
    生成 Barra Aegis Portfolio Analyst 所需要的股票组合文件
    资产当中只有股票和现金资产
    """

    # date = "20171228"
    # name = '泰达中证500指数分级'
    # portfolio_name = 'TD_ZZ500'
    # path = 'E:\\3_Data\\8_barra_contribution_data\\Aegis Performance Analysis\\TD_User_Portfolio\\'

    try:
        # read data and change type
        #################################################################################################
        security = MfcData().get_fund_security(date)
        asset = MfcData().get_fund_asset(date)
        print(' Fund %s At Date %s ' % (name, date))

        # 1 stock
        ################################################
        type = '股票'
        security = security[security['基金名称'] == name]
        security = security[security['证券类别'] == type]

        res = pd.DataFrame(security['持仓'].values, index=security['证券代码'].values, columns=['Holdings'])
        res.index = res.index.map(stock_code_add_postfix)
        res.index = res.index.map(stock_code_drop_postfix)
        res['Holdings'] = res['Holdings'].map(int)
        res['Type'] = 'A'

        # 2 cash
        ################################################
        data = asset[asset['基金名称'] == name]

        res.ix['CHNCURR', 'Holdings'] = int(data['当前现金余额'].values[0])
        res.ix['CHNCURR', 'Type'] = 'G'

        # save data path
        #################################################################################################
        sub_path = os.path.join(path, portfolio_name)

        if not os.path.exists(sub_path):
            os.makedirs(sub_path)
        file = portfolio_name + '.' + date
        f1 = open(os.path.join(sub_path, file), 'w')

        # write data
        #################################################################################################'
        f1.write('!MODEL:CQ\n')
        f1.write('!WEIGHT:SHRE\n')

        for i in range(len(res)):
            code = str(res.index[i])
            f1.write(code)
            f1.write('\t')
            f1.write(str(res.ix[code, 'Type']))
            f1.write('\t')
            f1.write(str(res.ix[code, 'Holdings']))
            f1.write('\n')
        f1.close()
        #################################################################################################'

    except:
        print(' Fund %s At Date %s is Null ' % (name, date))


if __name__ == '__main__':

    param_path = 'D:\\Program Files (x86)\\anaconda\\Lib\\site-packages\\quant\\project\\mfc_holding_project\\attribute_barra\\'
    data_path = 'E:\\3_Data\\8_barra_contribution_data\\Aegis Performance Analysis\\TD_User_Portfolio\\'
    param_file = os.path.join(param_path, 'generate_user_portfolio_param.xlsx')
    param = pd.read_excel(param_file)

    for i_fund in range(len(param)):

        beg_date = param.ix[i_fund, 'beg_date']
        end_date = datetime.today()
        name = param.ix[i_fund, 'fund_name_ch']
        portfolio_name = param.ix[i_fund, 'fund_name_en']

        date_series = Date().get_trade_date_series(beg_date, end_date)
        for date in date_series:
            GenerateUserPortfolio(date, name, portfolio_name, data_path)
