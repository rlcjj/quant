import pandas as pd
import numpy as np
import os
from quant.data_source.my_ftp import MyFtp
from quant.utility_fun.code_format import stock_code_add_postfix, stock_code_drop_postfix
from quant.param.param import Parameter
from quant.utility_fun.zip_file import unzip_file
from quant.stock.date import Date
from quant.stock.stock import Stock
from WindPy import w
w.start()


class IndexWeight(object):

    """
    指数每日权重的下载和获取 ftp\wind

    load_weight_from_ftp_date()
    load_weight_from_wind_date()
    load_weight_china_index_date()
    load_weight_period()

    get_weight()
    """
    def __init__(self):

        self.weight_name = 'Index_Weight'

        self.load_out_path_weight = Parameter().get_load_out_file(self.weight_name)
        self.read_path_weight = Parameter().get_read_file(self.weight_name)

    def load_weight_from_ftp_date(self, index_code, date):

        """
        从中证公司的FTP上下载原始指数权重 解压缩 并改变原始文件的位置
        """

        myftp = MyFtp(ip="124.74.243.125",
                      port=21,
                      user_name="csitd",
                      user_password="26266119")

        myftp.connect()
        date = Date().change_to_str(date)
        code = stock_code_drop_postfix(index_code)

        file_name = code + "weightnextday" + date + ".zip"
        ftp_file = '/idxdata/data/asharedata/' + code + "/weight_for_next_trading_day/" + file_name

        raw_path = r'E:\3_Data\2_index_data\2_index_weight\weight_raw\weight_dfc'
        raw_sub_path = os.path.join(raw_path, code)

        print(' Loading Index Weight Form FTP ', code, ' At ', date)

        if not os.path.exists(raw_sub_path):
            os.makedirs(raw_sub_path)

        local_file = os.path.join(raw_sub_path, file_name)
        myftp.load_file(ftp_file, local_file)
        myftp.close()

        print(raw_sub_path, local_file)
        unzip_file(local_file, raw_sub_path)

        unzip_file_name = code + "weightnextday" + date + ".xls"
        unzip_file_name = os.path.join(raw_sub_path, unzip_file_name)
        data = pd.read_excel(unzip_file_name, encoding='gbk')
        data = data.iloc[:, [4, 16]]
        data.columns = ['CODE', 'WEIGHT']
        data.CODE = data.CODE.map(stock_code_add_postfix)
        data.WEIGHT = data.WEIGHT.astype(np.float) / 100.0

        out_sub_path = os.path.join(self.load_out_path_weight, code)

        print(' Changing Index Weight Position', code, ' At ', date)

        if not os.path.exists(out_sub_path):
            os.makedirs(out_sub_path)

        out_file = os.path.join(out_sub_path, date + '.csv')
        data.to_csv(out_file, index=None)

    def load_weight_from_wind_date(self, index_code, date):

        """
        从wind客户终端下载指数权重
        注意：未付费的指数只能获得月频的权重数据
        """

        code = stock_code_drop_postfix(index_code)
        out_sub_path = os.path.join(self.load_out_path_weight, code)

        if not os.path.exists(out_sub_path):
            os.makedirs(out_sub_path)

        date = Date().change_to_str(date)
        last_date = Date().get_trade_date_offset(date, -1)

        print(' Loading Index Weight Form Wind', code, ' At ', date)

        data = w.wset("indexconstituent","date=" + last_date +
                      ";windcode=" + index_code + ";field=wind_code,i_weight")
        data = pd.DataFrame(data.Data, index=['CODE', 'WEIGHT'], columns=data.Codes).T
        data.WEIGHT /= 100.0

        if len(data.dropna()) < len(data):
            print(' Index Weight Form Wind Has NAN', code, ' At ', date)
            print(' Nan Code has ', -(len(data.dropna()) - len(data)))
            data = data.dropna()

        if len(data) < 10:
            print(' Index Weight Form Wind is Small', code, ' At ', date)

        out_file = os.path.join(out_sub_path, date + '.csv')
        data.to_csv(out_file, index=None)

    def load_weight_china_index_date(self, date):

        """
        利用自由流通市值作为指数权重
        """

        date = Date().change_to_str(date)
        date_1y = Date().get_normal_date_offset(date, -180)
        data = Stock().get_free_market_value_date(date)
        ipo_data = Stock().get_ipo_date()
        data = pd.concat([data, ipo_data], axis=1)
        data = data[data['IPO_DATE'] <= date_1y]
        data = data[data['DELIST_DATE'] >= date]

        code = "China_Index_Benchmark"

        data = data.dropna()
        free_mv_sum = data['Free_Market_Value'].sum()
        weight = pd.DataFrame(data['Free_Market_Value'].values / free_mv_sum, index=data.index, columns=['WEIGHT'])
        weight.index.name = "CODE"

        out_sub_path = os.path.join(self.load_out_path_weight, code)
        if not os.path.exists(out_sub_path):
            os.makedirs(out_sub_path)
        out_file = os.path.join(out_sub_path, date + '.csv')
        weight.to_csv(out_file)

    def load_weight_period(self, index_code, beg_date, end_date):

        """
        下载一段时间内 每个交易日的指数权重
        """

        date_list = Date().get_trade_date_series(beg_date, end_date)

        if index_code in ['000300.SH', '000905.SH', '000940.SH']:
            for date in date_list:
                self.load_weight_from_ftp_date(index_code, date)
        elif index_code in ["China_Index_Benchmark"]:
            for date in date_list:
                self.load_weight_china_index_date(date)
        else:
            for date in date_list:
                self.load_weight_from_wind_date(index_code, date)

    def get_weight(self, index_code, date):

        """
        获取在某个交易日 某个指数的权重
        """

        date = Date().change_to_str(date)
        path = Parameter().get_read_file(self.weight_name)
        file = os.path.join(path, index_code.strip(".SHZWI"),  date + '.csv')

        if os.path.exists(file):
            data = pd.read_csv(file, index_col=[0], encoding='gbk')
            data = data[data['WEIGHT'] > 0.0]
        else:
            print(" File No Exist ", index_code, date)
            data = None
        return data


if __name__ == "__main__":

    index = IndexWeight()
    date = "20180719"
    from datetime import datetime
    date = datetime.today()

    # Index Weight
    #############################################################################
    # index.load_weight_from_ftp_date("000905.SH", date)
    # index.load_weight_from_wind_date("000016.SH", date)
    # index.load_weight_china_index_date(date)
    # index.load_weight_period("000905.SH", "20180701", date)
    # index.load_weight_from_wind_date("000016.SH", date)
    index.load_weight_from_wind_date("881001.WI", date)
    #############################################################################
    