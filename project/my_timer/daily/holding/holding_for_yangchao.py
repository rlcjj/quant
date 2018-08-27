from quant.mfc.mfc_data import MfcData
from quant.stock.date import Date
from quant.stock.index import Index
from quant.stock.stock import Stock
from quant.param.param import Parameter
from datetime import datetime, timedelta
import pandas as pd
from quant.utility_fun.code_format import stock_code_add_postfix
import shutil
import os
from quant.utility_fun.zip_file import make_zip_file, make_zip_folder
from quant.utility_fun.send_email import send_mail_mfcteda


def holding_data_yangchao(today, project_path, out_path):

    # 输入参数
    ##################################################################################
    person_name = 'yangchao'
    before_trade_data = Date().get_trade_date_offset(today, -1)
    today = Date().change_to_str(today)

    # 基金列表
    ##################################################################################
    fund = pd.read_excel(project_path + 'Manage_Fund_Name.xlsx', encoding='gbk')
    fund_val = fund.ix[:, person_name]
    fund_val = fund_val.dropna()
    fund_list = list(fund_val.values)

    # 基金持仓证券
    ##################################################################################

    fund_asset = MfcData().get_group_security(before_trade_data)
    fund_asset = fund_asset[['日期', '组合名称', '基金名称', '证券代码', '证券名称', '持仓',
                             '市值比净值(%)', '盈亏率(%)', '证券类别', '当日买金额', '当日卖金额',
                             '资产单元名称', '持仓多空标志']]

    for i_fund in range(len(fund_list)):

        fund_name = fund_list[i_fund]
        fund_asset_fund = fund_asset[fund_asset['基金名称'] == fund_name]
        out_sub_path = os.path.join(out_path, person_name, today, "holding_data")
        if not os.path.exists(out_sub_path):
            os.mkdir(out_sub_path)
        out_file = os.path.join(out_sub_path, fund_name + '.csv')
        fund_asset_fund.to_csv(out_file, index=None)

    # 绝对收益组合资产
    ##################################################################################
    group_name = 'yangchao_group'
    fund_val = fund.ix[:, group_name]
    fund_val = fund_val.dropna()
    fund_list = list(fund_val.values)

    fund_asset = MfcData().get_group_security(before_trade_data)
    fund_asset = fund_asset[['日期', '组合名称', '基金名称', '证券代码', '证券名称', '持仓',
                             '市值比净值(%)', '盈亏率(%)', '证券类别',
                             '当日买金额', '当日卖金额', '资产单元名称', '持仓多空标志']]

    for i_fund in range(len(fund_list)):

        fund_name = fund_list[i_fund]
        one_fund = fund_asset[fund_asset['组合名称'] == fund_name]
        out_sub_path = os.path.join(out_path, person_name, today, "holding_data")
        if not os.path.exists(out_sub_path):
            os.mkdir(out_sub_path)
        if fund_name == '绝对收益期货组合':
            fund_name = "绝对收益股指期货组合"
        out_file = os.path.join(out_sub_path, fund_name + '.csv')
        one_fund.to_csv(out_file)

    # 股票库
    ##################################################################################
    pool_path = Parameter().get_load_out_file("Mfc_Data")
    pool_list = ["公司超五库.xls", "公司股票库.xls", "公司关联库.xls", "公司禁止库.xls", "公司限制库.xls",
                 "绝对收益禁止库.xls", "绝对收益投资库.xls",
                 "量化限制库.xls"]

    out_sub_path = os.path.join(out_path, person_name, today, "holding_data")

    for i_file in range(len(pool_list)):

        file = pool_list[i_file]
        src_file = os.path.join(pool_path, 'raw_file', today, file)
        out_file = os.path.join(out_sub_path, file)
        try:
            shutil.copyfile(src_file, out_file)
        except:
            pd.DataFrame().to_excel(out_file)

    # 股票库 英文
    ##################################################################################
    pool_path = Parameter().get_load_out_file("Mfc_Data")
    pool_list = {"公司禁止库.xls": "Company Forbidden Pool.csv",
                 "公司关联库.xls": "Company Related Pool.csv",
                 "公司限制库.xls": "Company Limited Pool.csv",
                 "公司股票库.xls": "Company Investment Pool.csv",
                 "绝对收益禁止库.xls": "ABS Fund Forbidden Pool.csv",
                 "绝对收益投资库.xls": "ABS Fund Investment Pool.csv",
                 "量化限制库.xls": "Quantitative Limited Pool.csv"}
    out_sub_path = os.path.join(out_path, person_name, today, "holding_data")

    for scr_file, out_file in pool_list.items():

        src_file = os.path.join(pool_path, 'raw_file', before_trade_data, scr_file)
        out_file = os.path.join(out_sub_path, out_file)
        data = pd.read_excel(src_file, index_col=[0])
        data.index = data['证券代码'].map(stock_code_add_postfix)
        data.index = data.index.map(lambda x: x[0:6] + '-CN')
        data['Status'] = 1.0
        data.to_csv(out_file, header=None, columns=['Status'])

    # 股票库 Company Investment Pool.csv 包括公司股票库和公司超5库
    ##################################################################################
    stock_pool_file = os.path.join(pool_path, 'raw_file', before_trade_data, "公司股票库.xls")
    stock_pool = pd.read_excel(stock_pool_file, index_col=[0])
    stock_pool.index = stock_pool['证券代码'].map(stock_code_add_postfix)
    stock_pool.index = stock_pool.index.map(lambda x: x[0:6] + '-CN')
    stock_pool['Status'] = 1.0

    stock_5_pool_file = os.path.join(pool_path, 'raw_file', before_trade_data, "公司超五库.xls")
    stock_5_pool = pd.read_excel(stock_5_pool_file, index_col=[0])
    stock_5_pool.index = stock_5_pool['证券代码'].map(stock_code_add_postfix)
    stock_5_pool.index = stock_5_pool.index.map(lambda x: x[0:6] + '-CN')
    stock_5_pool['Status'] = 1.0

    out_file = os.path.join(out_sub_path, "Company Investment Pool.csv")
    res = pd.concat([stock_5_pool['Status'], stock_pool['Status']], axis=0)
    res.to_csv(out_file, header=None)

    # Recent IPO Stock.csv
    ##################################################################################
    ipo_date_pd = Stock().get_ipo_date()
    beg_date = (datetime.strptime(today, '%Y%m%d') - timedelta(days=365)).strftime("%Y%m%d")
    ipo_date_pd = ipo_date_pd[ipo_date_pd['IPO_DATE'] > beg_date]
    ipo_date_pd.loc[:, 'IPO_DATE'] = 1.0
    ipo_date_pd.index = ipo_date_pd.index.map(lambda x: x[0:6] + '-CN')

    filename = 'Recent IPO Stock.csv'
    out_sub_path = os.path.join(out_path, person_name, today, "holding_data")
    print('loading ', filename, ' ......')
    ipo_date_pd.to_csv(os.path.join(out_sub_path, filename), header=None, columns=['IPO_DATE'])

    # Suspended List.csv
    ##################################################################################

    status_data = Stock().get_trade_status_date(today)
    ipo_date_pd = Stock().get_ipo_date()
    data = pd.concat([status_data, ipo_date_pd], axis=1)
    data = data.dropna()
    data = data[data['DELIST_DATE'] >= today]
    data['Trade_Status'] = 1.0
    data.index = data.index.map(lambda x: x[0:6] + '-CN')

    filename = 'Suspended List.csv'
    out_sub_path = os.path.join(out_path, person_name, today, "holding_data")
    print('loading ', filename, ' ......')
    data.to_csv(os.path.join(out_sub_path, filename), header=None, columns=['Trade_Status'])

    # Benchmark.csv 5.5 现金
    ##################################################################################
    benchmark_dict = {"000905.SH": "CSI500 Benchmark.csv",
                      "000300.SH": "CSI300 Benchmark.csv",
                      "000016.SH": "CSI50 Benchmark.csv"}

    for index_code, out_file in benchmark_dict.items():

        data = Index().get_weight(index_code, before_trade_data)
        data.index = data.index.map(lambda x: x[0:6] + '-CN')
        data['WEIGHT'] *= 94.5
        result = pd.DataFrame([5.5], index=["CSH_CNY"], columns=['WEIGHT'])
        result = pd.concat([result, data], axis=0)

        out_sub_path = os.path.join(out_path, person_name, today, "holding_data")
        result.to_csv(os.path.join(out_sub_path, out_file), header=None, columns=['WEIGHT'])

    # 英文持仓情况
    ##################################################################################

    en_holding_dict = {"泰达宏利量化增强": "Quantitative Enhencement portfolio.csv",
                       "泰达宏利业绩驱动量化": "Quantitative Earning Drive.csv",
                       "泰达新思路": "New Thinking Portfolio.csv",
                       "泰达宏利集利债券": "High Dividend Bond Equity.csv",
                       "泰达宏利沪深300": "CSI300 Portfolio.csv",
                       "泰达中证500指数分级": "CSI500 Portfolio.csv"
                       }
    out_sub_path = os.path.join(out_path, person_name, today, "holding_data")

    fund_sec = MfcData().get_fund_security(before_trade_data)

    for name, out_file in en_holding_dict.items():

        fund_sec_one = fund_sec[fund_sec['基金名称'] == name]
        fund_sec_one = fund_sec_one[fund_sec_one['证券类别'] == '股票']
        fund_sec_one = fund_sec_one[['证券代码', '持仓']]
        fund_sec_one.index = fund_sec_one['证券代码'].map(stock_code_add_postfix)
        fund_sec_one.index = fund_sec_one.index.map(lambda x: x[0:6] + '-CN')
        print(fund_sec_one)
        if out_file != "High Dividend Bond Equity.csv":
            asset = MfcData().get_fund_asset(before_trade_data)
            asset.index = asset['基金名称']
            asset = asset[~asset.index.duplicated()]
            fund_sec_one = fund_sec_one[~fund_sec_one.index.duplicated()]
            fund_sec_one.ix['CSH_CNY', "持仓"] = asset.ix[name, "当前现金余额"]
        out_file = os.path.join(out_sub_path, out_file)
        fund_sec_one['持仓'] = fund_sec_one['持仓'].round(0)
        fund_sec_one.to_csv(out_file, header=None, columns=['持仓'])

    # 英文绝对收益持仓情况
    ##################################################################################

    en_holding_dict = {"绝对收益50对冲股票组合": "Absolute Return Strategy CSI50 Portfolio.csv",
                       "绝对收益300对冲股票组合": "Absolute Return Strategy CSI300 Portfolio.csv",
                       "绝对收益500对冲股票组合": "Absolute Return Strategy CSI500 Portfolio.csv",
                       }
    out_sub_path = os.path.join(out_path, person_name, today, "holding_data")

    fund_sec = MfcData().get_group_security(before_trade_data)

    for name, out_file in en_holding_dict.items():

        fund_sec_one = fund_sec[fund_sec['组合名称'] == name]
        fund_sec_one = fund_sec_one[fund_sec_one['证券类别'] == '股票']
        fund_sec_one = fund_sec_one[['证券代码', '持仓']]
        fund_sec_one.index = fund_sec_one['证券代码'].map(stock_code_add_postfix)
        fund_sec_one.index = fund_sec_one.index.map(lambda x: x[0:6] + '-CN')
        out_file = os.path.join(out_sub_path, out_file)
        fund_sec_one.to_csv(out_file, header=None, columns=['持仓'])

    # China Market Index.csv
    ##################################################################################
    data = Index().get_weight("China_Index_Benchmark", before_trade_data)
    out_file = "China Market Index.csv"
    data.index = data.index.map(lambda x: x[0:6] + '-CN')
    out_sub_path = os.path.join(out_path, person_name, today, "holding_data")
    data.to_csv(os.path.join(out_sub_path, out_file), header=None, columns=['WEIGHT'])

    # Monitor 基金证券
    ##################################################################################
    en_holding_dict = {"泰达中证500指数分级": "CSI500 Monitor.csv"}
    out_sub_path = os.path.join(out_path, person_name, today, "holding_data")

    fund_sec = MfcData().get_fund_security(before_trade_data)

    for name, out_file in en_holding_dict.items():

        fund_sec_one = fund_sec[fund_sec['基金名称'] == name]
        fund_sec_one = fund_sec_one[fund_sec_one['证券类别'] == '股票']
        fund_sec_one = fund_sec_one[['证券代码', '持仓']]
        fund_sec_one.columns = ['STOCK_CODE', 'HOLDING']
        fund_sec_one.index = fund_sec_one['STOCK_CODE'].map(stock_code_add_postfix)
        out_file = os.path.join(out_sub_path, out_file)
        fund_sec_one.to_csv(out_file, columns=['HOLDING'])

    # Monitor 组合证券 绝对收益
    ##################################################################################
    out_sub_path = os.path.join(out_path, person_name, today, "holding_data")
    en_holding_dict = {"绝对收益50对冲股票组合": "Absolute Trading Monitor CSI50.csv",
                       "绝对收益300对冲股票组合": "Absolute Trading Monitor CSI300.csv",
                       "绝对收益500对冲股票组合": "Absolute Trading Monitor CSI500.csv",
                       "绝对收益期货组合": "Absolute Monitor Option.csv",
                       }
    fund_sec = MfcData().get_group_security(before_trade_data)

    for name, out_file in en_holding_dict.items():

        fund_sec_one = fund_sec[fund_sec['组合名称'] == name]
        # fund_sec_one = fund_sec_one[fund_sec_one['资产类别'] == '股票资产']
        fund_sec_one = fund_sec_one[['证券代码', '持仓']]
        fund_sec_one.columns = ['STOCK_CODE', 'HOLDING']
        if name != "绝对收益期货组合":
            fund_sec_one.index = fund_sec_one['STOCK_CODE'].map(stock_code_add_postfix)
        else:
            fund_sec_one.index = fund_sec_one['STOCK_CODE']
        out_file = os.path.join(out_sub_path, out_file)
        fund_sec_one.to_csv(out_file, columns=['HOLDING'])


def mail_for_yangchao():

    today = datetime.today().strftime("%Y%m%d")
    out_path = Parameter().get_read_file("Mfc_Daily")
    person_name = 'yangchao'

    print(" Mailing For ", person_name)
    sender_mail_name = 'fucheng.dou@mfcteda.com'

    receivers_mail_name = ['chao.yang@mfcteda.com', 'fucheng.dou@mfcteda.com']
    out_sub_path = os.path.join(out_path, person_name, today)
    zip_filename = "holding_data_" + today + ".rar"
    make_zip_folder(out_sub_path, os.path.join(out_sub_path, zip_filename))

    acc_mail_name = []
    subject_header = "持仓相关文件_部门内部自动发送_杨超"
    body_text = ""
    send_mail_mfcteda(sender_mail_name, receivers_mail_name, acc_mail_name,
                      subject_header, body_text, out_sub_path, zip_filename)
    os.remove(os.path.join(out_sub_path, zip_filename))

if __name__ == "__main__":

    project_path = Parameter().get_read_file("Mfc_Fund")
    out_path = Parameter().get_read_file("Mfc_Daily")
    today = datetime.today().strftime("%Y%m%d")
    # today = datetime(2018, 7, 10).strftime("%Y%m%d")
    holding_data_yangchao(today, project_path, out_path)
    mail_for_yangchao()