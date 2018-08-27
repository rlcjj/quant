import pandas as pd
from datetime import datetime
import os
from quant.param.param import Parameter
from quant.stock.date import Date
from quant.utility_fun.pandas_fun import pandas_add_row
from WindPy import w
w.start()


class IndexFactor(object):

    """
    指数的不同属性CLOSE\PE\PCT时间序列的下载和获取 默认为wind终端下载

    load_index_factor()
    load_index_factor_all()
    get_index_factor()
    """

    def __init__(self):

        self.name = "Index"
        self.beg_date = '19991231'
        self.load_out_path = Parameter().get_load_out_file(self.name)
        self.read_path = Parameter().get_read_file(self.name)

        self.index_code_primary = pd.DataFrame({'000300.SH': '沪深300',
                                                '000905.SH': '中证500',
                                                '881001.WI': '万德全A',
                                                '399005.SZ': '中小板指',
                                                '399006.SZ': '创业板指',
                                                "000985.CSI": "中证全指",
                                                "HSI.HI": "恒生指数",
                                                "IXIC.GI": "纳斯达克综合指数",
                                                "SPX.GI": "标普500指数"}, index=['Name']).T

        self.index_code_other = pd.DataFrame({'885012.WI': '股票型基金总指数',
                                              '885007.WI': '混合二级债基指数',
                                              '885003.WI': '偏债混合基金指数',
                                              'H11001.CSI': '中证全债指数',
                                              "000940.SH": '财富大盘指数',
                                              "930609.CSI": '中证纯债债基指数',
                                              "H00905.CSI": '中证500全收益'}, index=['Name']).T

    def load_index_factor(self, index_code="000300.SH", beg_date=None, end_date=None, source="wind_terminal"):


        # 参数
        ##############################################################################
        if beg_date is None:
            try:
                base_data = w.wsd(index_code, "basedate")
                beg_date = base_data.Data[0][0].strftime("%Y%m%d")
            except:
                beg_date = self.beg_date

        if end_date is None:
            end_date = datetime.today()

        beg_date = Date().change_to_str(beg_date)
        end_date = Date().change_to_str(end_date)

        # 下载数据
        ##############################################################################
        if source == 'wind_terminal':

            if index_code in list(self.index_code_primary.index):
                index_data = w.wsd(index_code, "close,pe_ttm,pb_lf", beg_date, end_date, "Fill=Previous")
            else:
                index_data = w.wsd(index_code, "close", beg_date, end_date, "Fill=Previous")

            new_data = pd.DataFrame(index_data.Data, index=index_data.Fields, columns=index_data.Times).T
            new_data.index = new_data.index.map(lambda x: x.strftime('%Y%m%d'))
            new_data['PCT'] = new_data['CLOSE'].pct_change()

            print(" Loading Index Attribute ", index_code)
            out_file = os.path.join(self.load_out_path, index_code + '.csv')

            if os.path.exists(out_file):
                data = pd.read_csv(out_file, encoding='gbk', index_col=[0])
                data.index = data.index.map(str)
                data = pandas_add_row(data, new_data)
            else:
                print(" File No Exist ", index_code)
                data = new_data
            data = data.dropna(how='all')
            data.to_csv(out_file)
        ##############################################################################

    def load_index_factor_all(self, beg_date=None, end_date=None, source="wind_terminal"):

        """
        下载所有指数 最近的Factor
        """

        for i in range(len(self.index_code_primary)):
            index_code = self.index_code_primary.index[i]
            self.load_index_factor(index_code, beg_date=beg_date, end_date=end_date, source=source)

        for i in range(len(self.index_code_other)):
            index_code = self.index_code_other.index[i]
            self.load_index_factor(index_code, beg_date=beg_date, end_date=end_date, source=source)

    def get_index_factor(self, index_code="000300.SH", beg_date=None, end_date=None, attr=None):

        if beg_date is None:
            beg_date = self.beg_date
        if end_date is None:
            end_date = datetime.today()
        if attr is None:
            attr = ['CLOSE', 'PCT']

        beg_date = Date().change_to_str(beg_date)
        end_date = Date().change_to_str(end_date)

        file = os.path.join(self.read_path, index_code + '.csv')

        if os.path.exists(file):
            data = pd.read_csv(file, index_col=[0], encoding='gbk', parse_dates=[0])
            data.index = data.index.map(lambda x: x.strftime('%Y%m%d'))
            data = data.ix[beg_date: end_date, attr]
        else:
            print(" File No Exist ", index_code)
            data = None
        return data

if __name__ == "__main__":

    # Index Factor
    #############################################################################
    index = IndexFactor()
    # index.load_index_factor("000300.SH", "20180531", datetime.today())
    # index.load_index_factor_all("20180701", datetime.today())
    # index.load_index_factor("000985.CSI")
    # index.load_index_factor("HSI.HI")
    #
    # index.load_index_factor("IXIC.GI")
    # index.load_index_factor("SPX.GI")
    # index.load_index_factor_all()
    date = datetime(2018, 7, 6)

    print(index.get_index_factor("000905.SH", "20180601", datetime.today()))
    print(index.get_index_factor("000300.SH", "20180601", date))
    #############################################################################