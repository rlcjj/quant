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


def holding_data_clj(today, project_path, out_path):

    # 输入参数
    ##################################################################################
    # project_path = 'E:\\4_代码\\pycharmprojects\\timer\\input_data\\'
    # out_path = 'E:\\3_数据\\7_other_data\\0_mail_holding_all\\'
    person_name = 'caolongjie'
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

    fund_asset = MfcData().get_fund_security(before_trade_data)
    fund_asset = fund_asset[['持仓日期', '序号', '基金名称', '证券代码', '证券名称', '证券类别',
                             '市值', '市值比净值(%)', '持仓', '净买量', '净买金额', '费用合计',
                             '当日涨跌幅(%)', '持仓多空标志', '估值价格', '最新价']]

    for i_fund in range(len(fund_list)):

        fund_name = fund_list[i_fund]
        fund_asset_fund = fund_asset[fund_asset['基金名称'] == fund_name]
        out_sub_path = os.path.join(out_path, person_name, today, "holding_data")
        if not os.path.exists(out_sub_path):
            os.mkdir(out_sub_path)
        out_file = os.path.join(out_sub_path, fund_name + '持仓.xlsx')
        fund_asset_fund.to_excel(out_file, index=None)

    # 基金资产
    ##################################################################################
    fund_asset = MfcData().get_fund_asset(before_trade_data)
    fund_asset = fund_asset[['序号', '统计日期', '基金编号', '基金名称', '股票资产', '净值', '基金份额',
                             '单位净值', '单位净值涨跌幅(%)', '累计单位净值', '昨日单位净值', '当日股票收益率(%)',
                             '当日股票净买入金额', '股票资产/净值(%)', '当前现金余额', '累计应收金额', '累计应付金额',
                             '期货保证金账户余额', '期货保证金', '可用期货保证金', '保证金']]

    fund_asset_fund = fund_asset[fund_asset['基金名称'].map(lambda x: x in fund_list)]
    out_sub_path = os.path.join(out_path, person_name, today, "holding_data")
    if not os.path.exists(out_sub_path):
        os.mkdir(out_sub_path)
    out_file = os.path.join(out_sub_path, '基金资产.xlsx')
    fund_asset_fund.to_excel(out_file, index=None)

    # 股票库
    ##################################################################################
    pool_path = Parameter().get_load_out_file("Mfc_Data")
    pool_list = ["公司超五库.xls", "公司股票库.xls", "公司关联库.xls", "公司禁止库.xls", "公司限制库.xls",
                 "专户禁止库.xls", "量化11号禁止库.xls", "人寿固收限制库.xls", "人寿固收禁止库(委托人发送).xls",
                 "量化限制库.xls"]

    out_sub_path = os.path.join(out_path, person_name, today, "holding_data")

    for i_file in range(len(pool_list)):

        file = pool_list[i_file]
        src_file = os.path.join(pool_path, 'raw_file', today, file)
        out_file = os.path.join(out_sub_path, file)
        try:
            shutil.copyfile(src_file, out_file)
        except:
            pd.DataFrame([]).to_excel(out_file)

    # 股票库 英文
    ##################################################################################
    pool_path = Parameter().get_load_out_file("Mfc_Data")
    pool_list = {"公司禁止库.xls": "Company Forbidden Pool.csv",
                 "公司关联库.xls": "Company Related Pool.csv",
                 "公司限制库.xls": "Company Limited Pool.csv"}
    out_sub_path = os.path.join(out_path, person_name, today, "holding_data")

    for scr_file, out_file in pool_list.items():

        src_file = os.path.join(pool_path, 'raw_file', before_trade_data, scr_file)
        out_file = os.path.join(out_sub_path, out_file)
        data = pd.read_excel(src_file, index_col=[0])
        data.index = data['证券代码'].map(stock_code_add_postfix)
        data.index = data.index.map(lambda x: x[0:6] + '-CN')
        data['Status'] = 1.0
        data.to_csv(out_file, header=None, columns=['Status'])

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

    # CSI500 Benchmark.csv 5.5 现金
    ##################################################################################
    data = Index().get_weight("000905.SH", before_trade_data)
    data.index = data.index.map(lambda x: x[0:6] + '-CN')
    data['WEIGHT'] *= 94.5
    result = pd.DataFrame([5.5], index=["CSH_CNY"], columns=['WEIGHT'])
    result = pd.concat([result, data], axis=0)

    filename = 'CSI500 Benchmark.csv'
    out_sub_path = os.path.join(out_path, person_name, today, "holding_data")
    print('loading ', filename, ' ......')
    result.to_csv(os.path.join(out_sub_path, filename), header=None, columns=['WEIGHT'])

    # 指数权重 Axioma
    ##################################################################################
    index_code_list = ["000300.SH", "000905.SH", "000016.SH", "881001.WI"]
    out_sub_path = os.path.join(out_path, person_name, today, "index_weight")
    if not os.path.exists(out_sub_path):
        os.makedirs(out_sub_path)

    for index_code in index_code_list:
        data = Index().get_weight(index_code, before_trade_data)
        out_file = os.path.join(out_sub_path, index_code + '.csv')
        data.index = data.index.map(lambda x: x[0:6] + '-CN')
        data.to_csv(out_file, header=None)

    # 英文持仓情况
    ##################################################################################

    en_holding_dict = {"建行中国人寿中证500管理计划": "China Life Insurance Portfolio.csv"}
    out_sub_path = os.path.join(out_path, person_name, today, "holding_data")

    fund_sec = MfcData().get_fund_security(before_trade_data)

    for name, out_file in en_holding_dict.items():

        fund_sec_one = fund_sec[fund_sec['基金名称'] == name]
        fund_sec_one = fund_sec_one[fund_sec_one['证券类别'] == '股票']
        fund_sec_one = fund_sec_one[['证券代码', '持仓']]
        fund_sec_one.index = fund_sec_one['证券代码'].map(stock_code_add_postfix)
        fund_sec_one.index = fund_sec_one.index.map(lambda x: x[0:6] + '-CN')
        out_file = os.path.join(out_sub_path, out_file)
        fund_sec_one.to_csv(out_file, header=None, columns=['持仓'])


def mail_for_clj():

    today = datetime.today().strftime("%Y%m%d")
    out_path = Parameter().get_read_file("Mfc_Daily")
    person_name = 'caolongjie'

    print(" Mailing For ", person_name)
    sender_mail_name = 'fucheng.dou@mfcteda.com'

    receivers_mail_name = ['longjie.cao@mfcteda.com', 'fucheng.dou@mfcteda.com']
    # receivers_mail_name = ['fucheng.dou@mfcteda.com']
    out_sub_path = os.path.join(out_path, person_name, today)
    zip_filename = "holding_data_" + today + ".rar"
    make_zip_folder(out_sub_path, os.path.join(out_sub_path, zip_filename))

    acc_mail_name = []
    subject_header = "持仓相关文件_部门内部自动发送_曹龙洁"
    body_text = ""
    send_mail_mfcteda(sender_mail_name, receivers_mail_name, acc_mail_name,
                      subject_header, body_text, out_sub_path, zip_filename)
    os.remove(os.path.join(out_sub_path, zip_filename))


if __name__ == "__main__":

    project_path = Parameter().get_read_file("Mfc_Fund")
    out_path = Parameter().get_read_file("Mfc_Daily")
    today = datetime.today().strftime("%Y%m%d")
    today = datetime(2018, 7, 6).strftime("%Y%m%d")
    holding_data_clj(today, project_path, out_path)
    # mail_for_clj()