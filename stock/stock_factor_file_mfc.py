import pandas as pd
import os
from quant.param.param import Parameter


class StockFactorFileMfc(object):

    """
    读取 matlab 下载好的股票因子数据

    get_primary_factor_mfc()
    get_alpha_factor_mfc()

    """

    def __init__(self):
        pass

    def get_primary_factor_mfc_file(self, factor_name="Pct_chg"):

        # 读取 primary data 路径
        #############################################################################
        param_path = Parameter().get_read_file("Primary_Factor_Mfc")
        param_file_list = ['FinancialStatementsDataPar.csv', 'industry.csv',
                           'DailyMarketDataPar.csv', 'PredictDataPar.csv', 'external.csv']

        for i_params in range(len(param_file_list)):

            param_file = param_file_list[i_params]
            param_file = os.path.join(param_path, param_file)
            data_add = pd.read_csv(param_file, encoding='gbk')

            if i_params == 0:
                data = data_add
            else:
                data = pd.concat([data, data_add], axis=0)

        try:
            data = data[['FACTOR', 'PATH']]
            data.index = data.FACTOR
            primary_path = data.ix[factor_name, "PATH"]
        except:
            primary_path = "InputData\WindData\DailyReportData"

        param_path = Parameter().get_read_file("Factor_Mfc")
        primary_factor_file = os.path.join(param_path, primary_path, factor_name + '.h5')

        return primary_factor_file

    def get_alpha_factor_mfc_file(self, factor_name="Beta"):

        # 读取 alpha data 路径
        #############################################################################
        param_path = Parameter().get_read_file("Alpha_Factor_Mfc")
        alpha_factor_file = os.path.join(param_path, factor_name + '.h5')
        return alpha_factor_file


if __name__ == '__main__':

    print(StockFactorFileMfc().get_primary_factor_mfc_file())
    print(StockFactorFileMfc().get_alpha_factor_mfc_file())
    print(StockFactorFileMfc().get_primary_factor_mfc_file("OperatingIncomeTotalDaily"))


