import pandas as pd
from quant.param.param import Parameter
from datetime import datetime
from WindPy import w
w.start()


class StockPool(object):

    """
    下载和得到当前所有的股票池
    load_all_stock_code_now
    get_all_stock_code_now
    """

    def __init__(self):

        self.name = "All_Stock_Code"
        self.load_out_file = Parameter().get_load_out_file(self.name)
        self.read_file = Parameter().get_read_file(self.name)

    def load_all_stock_code_now(self, source="wind_terminal"):

        if source == "wind_terminal":

            today = datetime.today().strftime('%Y-%m-%d')
            data = w.wset("sectorconstituent", "date=" + today + ";sectorid=a001010100000000")
            data = pd.DataFrame(data.Data, index=data.Fields, columns=data.Codes).T
            now_wind_list = list(data['wind_code'].values)

            data = w.wset("sectorconstituent", "date=" + today + ";sectorid=a001010m00000000")
            data = pd.DataFrame(data.Data, index=data.Fields, columns=data.Codes).T
            delist_list = list(data['wind_code'].values)

            now_list = self.get_all_stock_code_now()

            update_list = list(set(now_list) | set(now_wind_list) | set(delist_list))
            update_list.sort()
            update_code = pd.DataFrame(update_list, columns=['code'])
            update_code.to_csv(self.load_out_file)
            print("################# Loading All Stock Code ############################################")

    def get_all_stock_code_now(self, source="wind_terminal"):

        if source == "wind_terminal":
            code = pd.read_csv(self.read_file, encoding='gbk', index_col=[0])
            now_list = list(code['code'].values)
        else:
            now_list = []
        return now_list

if __name__ == '__main__':

    # StockPool
    ################################################################################
    StockPool().load_all_stock_code_now()
    print(StockPool().get_all_stock_code_now())
    ################################################################################
