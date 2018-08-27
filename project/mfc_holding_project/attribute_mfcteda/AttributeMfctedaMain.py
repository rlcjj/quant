import pandas as pd
from quant.project.mfc_holding_project.attribute_mfcteda.AttributeMfctedaFund import AttributeMfctedaFund


def ArributeMfctedaMain():

    """
    归因所有 基金 主程序
    """

    # 参数文件读取参数
    ####################################################################################################################
    param_path = 'E:\\3_Data\\6_mfcteda_fund_data\\2_Mfc_Fund\\'
    param_file = param_path + 'Fund_Info.xlsx'
    param = pd.read_excel(param_file, index_col=[0])
    data_path = 'C:\\Users\\doufucheng\\OneDrive\\Desktop\\data\\'

    # 所需要计算的基金 和 开始结束日期
    ####################################################################################################################
    number_list = range(0, len(param))
    date_list = [["20160101", '20161231'],
                 ["20170101", '20171231'],
                 ["20180101", '20180731']]

    # 开始循环计算
    ####################################################################################################################
    for i_date in range(len(date_list)):

        beg_date = date_list[i_date][0]
        end_date = date_list[i_date][1]

        for i_fund in number_list:

            fund_name = param.index[i_fund]
            index_code_ratio = param.loc[fund_name, "Index_Ratio"]
            fund_code = param.loc[fund_name, "Code"]
            index_code = param.loc[fund_name, "Index"]
            fund_id = param.loc[fund_name, "Id"]
            type = param.loc[fund_name, "Type"]
            mg_fee_ratio = param.loc[fund_name, "MgFeeRatio"] + param.loc[fund_name, "TrusteeShipFeeRatio"]

            # 若基准不是NAN 就开始计算归因
            if len(str(index_code)) > 6:
                print(" ########## BEGIN ATTRIBUTE Fund %s Date From %s To %s" % (fund_name, beg_date, end_date))
                AttributeMfctedaFund(index_code_ratio, fund_code, index_code,
                                        fund_name, beg_date, end_date, fund_id, data_path, type, mg_fee_ratio)

    ####################################################################################################################

if __name__ == '__main__':

    ArributeMfctedaMain()
