from quant.stock.stock_factor_file_mfc import StockFactorFileMfc
from quant.stock.stock_factor_file_dfc import StockFactorFileDfc
from quant.utility_fun.factor_operate import FactorOperate
from quant.data_source.hdf_mfc import HdfMfc
from quant.stock.stcok_pool import StockPool
from quant.stock.date import Date
import os
import pandas as pd
from datetime import datetime


class StockFactorReadWrite(StockFactorFileMfc, StockFactorFileDfc):

    """
    读取股票因子数据
    泰达因子数据 StockFactorMfc()
    我的因子数据 StockFactorDfc()

    get_factor_h5()
    get_factor_csv()
    write_factor_h5()
    """

    def __init__(self):

        StockFactorFileMfc.__init__(self)
        StockFactorFileDfc.__init__(self)

    def get_factor_h5(self, factor_name="Beta", dataset_name=None, type="alpha_mfc"):

        # 参数
        #############################################################################
        if dataset_name is None:
            dataset_name = factor_name

        # 文件位置
        #############################################################################
        if type == "alpha_mfc":
            file = self.get_alpha_factor_mfc_file(factor_name)
        elif type == "primary_mfc":
            file = self.get_primary_factor_mfc_file(factor_name)
        elif type == "alpha_dfc":
            file = self.get_alpha_factor_dfc_file(factor_name)
        elif type == "primary_dfc":
            file = self.get_primary_factor_dfc_file(factor_name)
        elif type == "barra_risk_dfc":
            file = self.get_barra_risk_factor_dfc_file(factor_name)
        else:
            file = ""
            print(" No Exist The Type ")

        # 读取数据
        print("Read Data From %s" % file)
        #############################################################################
        if os.path.exists(file):

            h = HdfMfc(file, factor_name)
            factor_data = h.read_hdf_factor(dataset_name)
            factor_data.columns = factor_data.columns.map(str)
            return factor_data

        else:
            print("%s is no exists" % factor_name)
            return None
            #############################################################################

    def write_factor_h5(self, data, factor_name=None, type="alpha_mfc", data_type='f'):

        # 文件位置
        #############################################################################
        if type == "alpha_mfc":
            file = self.get_alpha_factor_mfc_file(factor_name)
        elif type == "primary_mfc":
            file = self.get_primary_factor_mfc_file(factor_name)
        elif type == "alpha_dfc":
            file = self.get_alpha_factor_dfc_file(factor_name)
        elif type == "primary_dfc":
            file = self.get_primary_factor_dfc_file(factor_name)
        elif type == "barra_risk_dfc":
            file = self.get_barra_risk_factor_dfc_file(factor_name)
        else:
            file = ""
            print(" No Exist The Type ")

        print(file)
        # 检查数据结构
        #############################################################################
        # index --> code columns --> date
        data.index = data.index.map(str)
        data.columns = data.columns.map(str)
        if data.columns[0][0] not in ["1", "2"]:
            print(" Data Columns in not Date ")
        data = data.T.dropna(how='all').T

        # 写入H5数据
        #############################################################################

        if not os.path.exists(file):
            print(" The File %s Not Exist, Saving %s " % (file, factor_name))
            HdfMfc().write_hdf_factor(filename=file, dsname=factor_name, data=data, type=data_type)
        else:
            old_data = self.get_factor_h5(factor_name, None, type)
            old_data = old_data.T
            new_data = data.T
            save_data = FactorOperate().pandas_add_row(old_data=old_data, new_data=new_data)
            save_data = save_data.T
            save_data = save_data.T.dropna(how='all').T
            print(" The File %s Exist, Saving %s " % (file, factor_name))
            HdfMfc().write_hdf_factor(filename=file, dsname=factor_name, data=save_data, type=data_type)
        #############################################################################


if __name__ == '__main__':

    print(StockFactorReadWrite().get_factor_h5("Beta", None, "alpha_mfc"))
    print(StockFactorReadWrite().get_factor_h5())
    data = StockFactorReadWrite().get_factor_h5("PriceCloseAdjust", None, "alpha_dfc")
    print(data)
    StockFactorReadWrite().write_factor_h5(data, "PriceCloseAdjust", "alpha_dfc")

