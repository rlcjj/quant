from quant.param.param import Parameter
import pandas as pd
import numpy as np
import os
from quant.stock.date import Date
from datetime import datetime


class Barra(object):

    """
    从曹龙洁网盘地址下载 Barra Retrun / Exposure / Stock Residual Return

    """

    def __init__(self):

        self.barra_name = "Barra_Name"
        self.factor_return_name = "Barra_Factor_Return"
        self.factor_exposure_name = "Barra_Factor_Exposure"
        self.stock_residual_name = "Barra_Stock_Residual"

    def load_factor_return(self):

        print('loading barra factor return......')
        in_file = Parameter().get_load_in_file(self.factor_return_name)
        data = pd.read_csv(in_file, index_col=[0], parse_dates=[0], encoding='gbk')
        output_file = Parameter().get_load_out_file(self.factor_return_name)
        data.to_csv(output_file)

    def load_factor_exposure(self):

        in_path = Parameter().get_load_in_file(self.factor_exposure_name)
        dirpath = os.listdir(in_path)
        output_path = Parameter().get_load_out_file(self.factor_exposure_name)
        output_dirpath = os.listdir(output_path)
        mydirpath = list(set(dirpath) - set(output_dirpath))

        for i_file in range(len(mydirpath)):

            file = mydirpath[i_file]
            print('loading barra factor exposure ' + file + '......')
            data = pd.read_csv(in_path + file, index_col=[0], encoding='gbk')
            data.to_csv(output_path + file)

    def load_stock_residual(self):

        in_path = Parameter().get_load_in_file(self.stock_residual_name)
        dirpath = os.listdir(in_path)
        output_path = Parameter().get_load_out_file(self.stock_residual_name)
        output_dirpath = os.listdir(output_path)
        mydirpath = list(set(dirpath) - set(output_dirpath))

        for i_file in range(len(mydirpath)):

            file = mydirpath[i_file]
            print('loading barra stock residual ' + file + '......')
            data = pd.read_csv(in_path + file, index_col=[0], encoding='gbk')
            data.to_csv(output_path + file)

    def load_barra(self):

        self.load_factor_return()
        self.load_factor_exposure()
        self.load_stock_residual()

    def get_factor_name(self, type_list=None):

        if type_list is None:
            type_list = ["STYLE"]

        filename = Parameter().get_read_file(self.barra_name)
        data = pd.read_excel(filename, encoding='gbk')
        data = data[data['TYPE'].map(lambda x: x in type_list)]
        return data

    def get_factor_return(self, beg_date=None, end_date=None, type_list=None):

        if beg_date is None:
            beg_date = "20000101"
        if end_date is None:
            end_date = datetime.today().strftime("%Y%m%d")
        if type_list is None:
            type_list = ["STYLE"]

        filename = Parameter().get_read_file(self.factor_return_name)
        barra_factor_return = pd.read_csv(filename, index_col=[0], parse_dates=[0], encoding='gbk')
        barra_factor_return.index = barra_factor_return.index.map(Date().change_to_str)

        name = self.get_factor_name(type_list=type_list)
        barra_factor_name = name['NAME_EN'].values

        barra_factor_return = barra_factor_return[barra_factor_name]
        barra_factor_return = barra_factor_return[~barra_factor_return.index.duplicated()]
        beg_date = Date().change_to_str(beg_date)
        end_date = Date().change_to_str(end_date)
        barra_factor_return = barra_factor_return.ix[beg_date:end_date, :]

        return barra_factor_return

    def get_factor_exposure_date(self, date, type_list=None):

        if type_list is None:
            type_list = ["STYLE"]

        path = Parameter().get_read_file(self.factor_exposure_name)
        date = Date().change_to_str(date)
        filename = path + 'CQU_CQA_' + date + '.csv'

        name = self.get_factor_name(type_list=type_list)
        barra_factor_name = name['NAME_EN'].values

        if os.path.exists(filename):
            barra_factor_exposure = pd.read_csv(filename, index_col=[0], encoding='gbk')
            barra_factor_exposure['CTY'] = 1.0
            barra_factor_exposure = barra_factor_exposure[barra_factor_name]
        else:
            print('barra factor exposure at ', str(date), ' not exist ')
            return None

        return barra_factor_exposure

    def get_factor_exposure_average(self, beg_date, end_date, type_list=None):

        date_series = Date().get_trade_date_series(beg_date, end_date)

        for i_date in range(len(date_series)):

            date = date_series[i_date]
            exposure_add = self.get_factor_exposure_date(date, type_list=type_list)
            if i_date == 0:
                exposure = exposure_add
            else:
                exposure = exposure_add + exposure

        exposure /= len(date_series)

        return exposure

    def cal_stock_riskfactor_return_daily(self, beg_date, end_date):

        """
        计算股票每一日 在行业 风格 上的收益 = 当日在风格、行业上的暴露 * 当日风格、行业的因子收益率
        """

        factor_return = self.get_factor_return(beg_date, end_date, type_list=['COUNTRY', 'STYLE', 'INDUSTRY'])
        path = Parameter().get_read_file("Barra_Stock_Factor_Return")

        for i_date in range(len(factor_return)):

            date = factor_return.index[i_date]
            exposure = self.get_factor_exposure_date(date, type_list=['COUNTRY', 'STYLE', 'INDUSTRY'])

            if exposure is not None:
                factor_return_date = factor_return.ix[date, :]
                factor_return_mat = np.tile(factor_return_date.values, (len(exposure), 1))
                factor_return_mat = pd.DataFrame(factor_return_mat, index=exposure.index, columns=factor_return.columns)
                stock_factor_return = factor_return_mat.mul(exposure)

                print("Cal Stock Riskfactor Return Daily is %s" % date)
                file = os.path.join(path, "Barra_Stock_Factor_Return_" + date + '.csv')
                stock_factor_return.to_csv(file)

    def get_stock_riskfactor_return_date(self, date):

        date = Date().change_to_str(date)
        path = Parameter().get_read_file("Barra_Stock_Factor_Return")
        file = os.path.join(path, "Barra_Stock_Factor_Return_" + date + '.csv')
        if os.path.exists(file):
            stock_factor_return = pd.read_csv(file, index_col=[0], encoding='gbk')
        else:
            stock_factor_return = None
        return stock_factor_return

    def get_stock_residual_return_date(self, date):

        """

        :return:
        """
        date = Date().change_to_str(date)
        path = Parameter().get_read_file(self.stock_residual_name)
        file = os.path.join(path, 'SRETURN_' + date + '.csv')
        if os.path.exists(file):
            stock_residual_return = pd.read_csv(file, index_col=[0], encoding='gbk')
            stock_residual_return = stock_residual_return[~stock_residual_return.index.duplicated()]
            stock_residual_return *= 100
        else:
            stock_residual_return = None

        return stock_residual_return

    def get_stock_return(self):

        from quant.stock.stock import Stock
        pct = Stock().get_factor_h5("Pct_chg", None, "primary_mfc")
        return pct

if __name__ == '__main__':

    # Barra().load_barra()
    # print(Barra().factor_exposure_name)
    # print(Barra().get_factor_exposure_date(20171229))
    # print(Barra().get_factor_return(20171203, 20180709))
    # data = Barra().get_factor_return("20040101", "20180615")
    # data = data.cumsum()
    # data.to_csv('C:\\Users\\doufucheng\\OneDrive\\Desktop\\QFII\\Barra_Cum_Return.csv')

    # Barra().cal_stock_riskfactor_return_daily("20020101", datetime.today())

    date = "20180807"
    stock_riskfactor_return = Barra().get_stock_riskfactor_return_date(date)
    stock_riskfactor_return_sum = stock_riskfactor_return.sum(axis=1)
    stock_residual_return = Barra().get_stock_residual_return_date(date)

    stock_return = Barra().get_stock_return()
    stock_return = stock_return[date]

    data = pd.concat([stock_residual_return, stock_riskfactor_return_sum, stock_return], axis=1)
    data.columns = ['Residual', 'RiskReturn', 'Return']
    data['Return_Sum'] = data['Residual'] + data['RiskReturn']
    data['Diff'] = data['Return'] - data['Return_Sum']

    """
    两个的差为无风险利率
    """
    print(data)
    print(data['Diff'].mean())
