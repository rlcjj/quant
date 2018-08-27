from quant.mfc.mfc_data import MfcData
from quant.stock.date import Date
from quant.param.param import Parameter
from datetime import datetime
import pandas as pd
import os
import shutil
from quant.stock.index import Index
from quant.utility_fun.zip_file import make_zip_file, make_zip_folder
from quant.utility_fun.send_email import send_mail_mfcteda


def holding_data_liuxin(today, project_path, out_path):

    # 输入参数
    ##################################################################################
    # project_path = 'E:\\4_代码\\pycharmprojects\\timer\\input_data\\'
    # out_path = 'E:\\3_数据\\7_other_data\\0_mail_holding_all\\'
    person_name = 'liuxin'
    # today = datetime(2018, 6, 27).strftime("%Y%m%d")
    before_trade_data = Date().get_trade_date_offset(today, -1)
    today = Date().change_to_str(today)

    # 基金列表
    ##################################################################################
    fund = pd.read_excel(project_path + 'Manage_Fund_Name.xlsx', encoding='gbk')
    fund_val = fund.ix[:, person_name]
    fund_val = fund_val.dropna()
    fund_list = list(fund_val.values)
    # fund_list.append("泰达宏利品质生活")

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
            os.makedirs(out_sub_path)
        out_file = os.path.join(out_sub_path, fund_name + '持仓.xlsx')
        fund_asset_fund.to_excel(out_file, index=None)

    # 股票库
    ##################################################################################
    pool_path = Parameter().get_load_out_file("Mfc_Data")
    pool_list = ["改革动力股票库.xls", "改革动力禁止库.xls", "改革动力限制库.xls",
                 "公司超五库.xls", "公司股票库.xls", "公司关联库.xls", "公司禁止库.xls", "公司限制库.xls",
                 "逆向股票库.xls", "逆向禁止库.xls", "逆向限制库.xls", "同顺禁止库.xls",
                 "量化限制库.xls"]

    out_sub_path = os.path.join(out_path, person_name, today, "holding_data")
    if not os.path.exists(out_sub_path):
        os.makedirs(out_sub_path)

    for i_file in range(len(pool_list)):

        file = pool_list[i_file]
        src_file = os.path.join(pool_path, 'raw_file', today, file)
        out_file = os.path.join(out_sub_path, file)
        try:
            shutil.copyfile(src_file, out_file)
        except:
            pd.DataFrame([]).to_excel(out_file)


    # 指数权重 Axioma
    ##################################################################################
    index_code_list = ["000300.SH", "000905.SH", "000016.SH", "881001.WI", 'China_Index_Benchmark']
    out_sub_path = os.path.join(out_path, person_name, today, "index_weight")
    if not os.path.exists(out_sub_path):
        os.makedirs(out_sub_path)

    for index_code in index_code_list:
        data = Index().get_weight(index_code, before_trade_data)
        out_file = os.path.join(out_sub_path, index_code + '.csv')
        data.index = data.index.map(lambda x: x[0:6] + '-CN')
        data.to_csv(out_file, header=None)


def mail_for_liuxin():

    today = datetime.today().strftime("%Y%m%d")
    out_path = Parameter().get_read_file("Mfc_Daily")
    person_name = 'liuxin'

    print(" Mailing For ", person_name)
    sender_mail_name = 'fucheng.dou@mfcteda.com'

    receivers_mail_name = ['xin.liu@mfcteda.com', 'fucheng.dou@mfcteda.com']
    # receivers_mail_name = ['fucheng.dou@mfcteda.com', 'yang.liu@mfcteda.com']
    out_sub_path = os.path.join(out_path, person_name, today)
    zip_filename = "holding_data_" + today + ".rar"
    make_zip_folder(out_sub_path, os.path.join(out_sub_path, zip_filename))

    acc_mail_name = []
    subject_header = "持仓相关文件_部门内部自动发送_刘欣"
    body_text = ""
    send_mail_mfcteda(sender_mail_name, receivers_mail_name, acc_mail_name,
                      subject_header, body_text, out_sub_path, zip_filename)
    os.remove(os.path.join(out_sub_path, zip_filename))

if __name__ == "__main__":

    project_path = Parameter().get_read_file("Mfc_Fund")
    out_path = Parameter().get_read_file("Mfc_Daily")
    today = datetime.today().strftime("%Y%m%d")
    # today = datetime(2018, 7, 6).strftime("%Y%m%d")
    holding_data_liuxin(today, project_path, out_path)
    # mail_for_liuxin()
