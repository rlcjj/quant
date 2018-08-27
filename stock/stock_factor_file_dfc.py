import pandas as pd
import os
from quant.param.param import Parameter
from WindPy import w
w.start()


class StockFactorFileDfc(object):
    
    """
    读取自己的股票因子数据

    get_barra_risk_factor_dfc()

    """

    def __init__(self):
        pass

    def get_alpha_factor_dfc_file(self, factor_name):

        param_path = Parameter().get_read_file("Alpha_Factor_Dfc")
        alpha_factor_file = os.path.join(param_path, factor_name + '.h5')
        return alpha_factor_file

    def get_primary_factor_dfc_file(self, factor_name):

        param_path = Parameter().get_read_file("Primary_Factor_Dfc")
        factor_file = os.path.join(param_path, factor_name + '.h5')
        return factor_file

    def get_barra_risk_factor_dfc_file(self, name="NORMAL_CNE5_SIZE"):
        
        """
        "RAW_CNE5_BOOK_TO_PRICE" "NORMAL_CNE5_SIZE" "RAW_CNE5_BETA"
        """
        # sub 路径
        ########################################################
        if "RAW_" in name:
            sub_factor = "raw_data"
        elif "NORMAL_" in name:
            sub_factor = "standardization_data"
        else:
            sub_factor = ""
            print(" Can Not Find Sub Risk Factor ")

        # 主路径
        ########################################################
        main_path = Parameter().get_read_file("Barra_Risk_Factor_Dfc")

        # 读取数据
        ########################################################
        file = os.path.join(main_path, sub_factor, name + '.h5')
        return file


if __name__ == "__main__":

    print(StockFactorFileDfc().get_barra_risk_factor_dfc_file())
    
    

