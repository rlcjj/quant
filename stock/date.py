import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import calendar
import inspect
from quant.param.param import Parameter
from WindPy import w
w.start()


class Date(object):

    """
    1、交易日数据（日、周、月、季、半年、年）的下载，获取
    load_trade_date_series
    load_trade_date_series_all
    get_trade_date_series
    get_trade_date_offset
    get_trade_date_month_end_day
    get_trade_date_last_month_end_day

    2、普通日数据（日、周、月、季、半年、年）的获取
    get_normal_date_series
    get_normal_date_offset
    get_normal_date_month_end_day
    get_normal_date_last_month_end_day
    get_normal_date_month_first_day

    3、交易日的格式转化（str, date, int）
    change_to_str
    change_to_str_hyphen
    change_to_datetime
    """

    def __init__(self):

        self.name = "Date"
        self.beg_date = "1989-12-31"
        self.file_dict = {"D": 'trade_date_daily.csv',
                          "W": 'trade_date_weekly.csv',
                          "M": 'trade_date_monthly.csv',
                          "Q": 'trade_date_quarterly.csv',
                          "S": 'trade_date_semiannually.csv',
                          "Y": 'trade_date_yearly.csv'}

        self.load_path = Parameter().get_load_out_file(self.name)
        self.read_path = Parameter().get_read_file(self.name)

    def load_trade_date_series(self, period="D"):

        today = datetime.today().strftime('%Y-%m-%d')
        data = w.tdays(self.beg_date, today, "Period=" + str(period))
        data_pd = pd.DataFrame(data.Data, index=['Trade_Date'], columns=data.Times).T
        data_pd['Trade_Date'] = data_pd['Trade_Date'].map(lambda x: x.strftime('%Y%m%d'))
        data_pd.index = data_pd.index.map(lambda x: x.strftime('%Y%m%d'))

        out_file = os.path.join(self.load_path, self.file_dict[period])
        data_pd.to_csv(out_file)
        print(" Loading Date " + out_file)

    def load_trade_date_series_all(self):

        self.load_trade_date_series(period="D")
        self.load_trade_date_series(period="W")
        self.load_trade_date_series(period="M")
        self.load_trade_date_series(period="Q")
        self.load_trade_date_series(period="S")
        self.load_trade_date_series(period="Y")

    def get_trade_date_series(self, beg_date=None, end_date=None, period='D'):

        if beg_date is None:
            beg_date = self.beg_date
        if end_date is None:
            end_date = datetime.today()

        beg_date = self.change_to_str(beg_date)
        end_date = self.change_to_str(end_date)

        file = os.path.join(self.read_path, self.file_dict[period])
        date_data = pd.read_csv(file, index_col=[0], encoding='gbk')
        date_data['Trade_Date'] = date_data['Trade_Date'].map(str)
        date_data.index = date_data.index.map(str)
        date_series = list(date_data.ix[beg_date:end_date, "Trade_Date"].values)
        date_series.sort()
        if period in ['M', 'Q', 'S', 'Y']:
            date_series = date_series[0:-1]
        else:
            pass
        return date_series

    def get_trade_date_offset(self, end_date=None, offset_num=0):

        if end_date is None:
            end_date = datetime.today()

        all_date = self.get_trade_date_series(None, None, 'D')
        all_date = pd.DataFrame(all_date, index=all_date)
        end_date = self.change_to_str(end_date)
        data_end_date = all_date.index[-1]
        if data_end_date < end_date:
            print(" The Input Date is Bigger Than Current Date ." + inspect.stack()[1][1])
            return data_end_date

        data = all_date.ix[:end_date, :]
        last_trade_date = data.index[-1]
        last_trade_date_index = list(data.index).index(last_trade_date)
        offset_trade_date_index = last_trade_date_index + offset_num

        if offset_trade_date_index < 0:
            print(" The Offset Trade Date Index Smaller Than Zero ." + inspect.stack()[1][1])
            offset_trade_date = all_date.index[0]
        elif offset_trade_date_index >= len(all_date):
            print(" The Offset Trade Date Index Bigger Than Current Date ." + inspect.stack()[1][1])
            offset_trade_date = all_date.index[-1]
        else:
            offset_trade_date = all_date.index[offset_trade_date_index]
        return offset_trade_date

    def get_trade_date_month_end_day(self, date):

        date = self.get_normal_date_month_end_day(date)
        date_series = self.get_trade_date_series()
        date_series = pd.DataFrame(date_series, index=date_series)
        date_series = date_series.ix[:date, :]
        last_date = date_series.index[-1]
        return last_date

    def get_trade_date_last_month_end_day(self, date):

        date = self.get_normal_date_last_month_end_day(date)
        date_series = self.get_trade_date_series()
        date_series = pd.DataFrame(date_series, index=date_series)
        date_series = date_series.ix[:date, :]
        last_date = date_series.index[-1]
        return last_date

    def get_normal_date_series(self, beg_date=None, end_date=None, period='D'):

        if beg_date is None:
            beg_date = self.beg_date
        if end_date is None:
            end_date = datetime.today()

        beg_date = self.change_to_str(beg_date)
        end_date = self.change_to_str(end_date)

        if period in ['D']:
            date_series = pd.date_range(start=beg_date, end=end_date)
            date_series = list(date_series.map(lambda x: x.strftime('%Y%m%d')))
        elif period in ['M', 'Q', 'S', 'Y']:
            date_series_trade = self.get_trade_date_series(beg_date, end_date, period=period)
            date_series = list(map(self.get_normal_date_month_end_day, date_series_trade))
        else:
            date_series = None

        return date_series

    def get_normal_date_offset(self, end_date=None, offset_num=0):

        if end_date is None:
            end_date = datetime.today()
        end_date = self.change_to_datetime(end_date)
        end_date = end_date + timedelta(offset_num)
        date_str = self.change_to_str(end_date)
        return date_str

    def get_normal_date_month_first_day(self, date):

        date = self.change_to_datetime(date)
        date_str = self.change_to_str(datetime(date.year, date.month, 1))
        return date_str

    def get_normal_date_last_month_end_day(self, date):

        date = datetime.strptime(self.get_normal_date_month_first_day(date), '%Y%m%d') - timedelta(days=1)
        date_str = self.change_to_str(date)
        return date_str

    def get_normal_date_month_end_day(self, date):

        date = self.change_to_datetime(date)
        days = calendar.monthrange(date.year, date.month)[1]
        date_str = self.change_to_str(datetime(date.year, date.month, days))
        return date_str

    """
    获取离当前日期最近可得的一个基金季报日期
    基金季报是15个工作日 基金半年报是60个工作日 基金年报是90个工作日
    """

    def get_last_fund_quarter_date(self, date):

        date_series = self.get_normal_date_series(beg_date=None, end_date=datetime.today(), period="Q")
        quarter_date = self.get_trade_date_offset(date, -15)
        date_series = pd.DataFrame(date_series, index=date_series)

        date_series = date_series[date_series <= quarter_date]
        date_series = date_series.dropna()

        result_date = date_series.index[-1]
        return result_date

    def get_last_fund_halfyear_date(self, date):

        date_series = Date().get_normal_date_series(beg_date=None, end_date=datetime.today(), period="S")
        month = self.change_to_datetime(date).month

        if month in [1, 2, 3, 4, 5, 6]:
            quarter_date = self.get_trade_date_offset(date, -90)
        else:
            quarter_date = self.get_trade_date_offset(date, -60)

        date_series = pd.DataFrame(date_series, index=date_series)
        date_series = date_series[date_series <= quarter_date]
        date_series = date_series.dropna()

        result_date = date_series.index[-1]
        return result_date

    def get_factor_date_dict(self, cur_date):

        # 返回日期结果字典
        res = {}

        cur_date = self.change_to_datetime(cur_date)
        year = cur_date.year
        month = cur_date.month
        day = cur_date.day

        # 当前交易日
        res['trade_date'] = datetime(year, month, day).strftime("%Y%m%d")

        # 去年同期交易日
        res['trade_date_last_year'] = (datetime(year, month, day) - timedelta(days=365)).strftime("%Y%m%d")

        if month in [1, 2, 3, 4]:

            # 最近季报
            res['quarter_report_1'] = datetime(year - 1, 9, 30).strftime("%Y%m%d")
            # 最近季报 的去年同期季报
            res['quarter_report_1_last_year'] = datetime(year - 2, 9, 30).strftime("%Y%m%d")

            # 最近季报 的上期季报
            res['quarter_report_2'] = datetime(year - 1, 6, 30).strftime("%Y%m%d")
            # 最近季报 的上期季报 的去年同期季报
            res['quarter_report_2_last_year'] = datetime(year - 2, 6, 30).strftime("%Y%m%d")

            # 最近季报 的上上期季报
            res['quarter_report_3'] = datetime(year - 1, 3, 31).strftime("%Y%m%d")
            # 最近季报 的上上上期季报
            res['quarter_report_4'] = datetime(year - 2, 12, 31).strftime("%Y%m%d")

            # 去年年报
            res['annual_report_date_last_year'] = datetime(year - 2, 12, 31).strftime("%Y%m%d")

        elif month in [5, 6, 7, 8]:

            # 最近季报
            res['quarter_report_1'] = datetime(year, 3, 31).strftime("%Y%m%d")
            # 最近季报 的去年同期季报
            res['quarter_report_1_last_year'] = datetime(year - 1, 3, 31).strftime("%Y%m%d")

            # 最近季报 的上期季报
            res['quarter_report_2'] = datetime(year - 1, 12, 31).strftime("%Y%m%d")
            # 最近季报 的上期季报 的去年同期季报
            res['quarter_report_2_last_year'] = datetime(year - 2, 12, 31).strftime("%Y%m%d")

            # 最近季报 的上上期季报
            res['quarter_report_3'] = datetime(year - 1, 9, 30).strftime("%Y%m%d")
            # 最近季报 的上上上期季报
            res['quarter_report_4'] = datetime(year - 1, 6, 30).strftime("%Y%m%d")

            # 去年年报
            res['annual_report_date_last_year'] = datetime(year - 1, 12, 31).strftime("%Y%m%d")

        elif month in [9, 10]:

            # 最近季报
            res['quarter_report_1'] = datetime(year, 6, 30).strftime("%Y%m%d")
            # 最近季报 的去年同期季报
            res['quarter_report_1_last_year'] = datetime(year - 1, 6, 30).strftime("%Y%m%d")

            # 最近季报 的上期季报
            res['quarter_report_2'] = datetime(year, 3, 31).strftime("%Y%m%d")
            # 最近季报 的上期季报 的去年同期季报
            res['quarter_report_2_last_year'] = datetime(year - 1, 3, 31).strftime("%Y%m%d")

            # 最近季报 的上上期季报
            res['quarter_report_3'] = datetime(year - 1, 12, 31).strftime("%Y%m%d")
            # 最近季报 的上上上期季报
            res['quarter_report_4'] = datetime(year - 1, 9, 30).strftime("%Y%m%d")

            # 去年年报
            res['annual_report_date_last_year'] = datetime(year - 1, 12, 31).strftime("%Y%m%d")

        elif month in [11, 12]:

            # 最近季报
            res['quarter_report_1'] = datetime(year, 9, 30).strftime("%Y%m%d")
            # 最近季报 的去年同期季报
            res['quarter_report_1_last_year'] = datetime(year - 1, 9, 30).strftime("%Y%m%d")

            # 最近季报 的上期季报
            res['quarter_report_2'] = datetime(year, 6, 30).strftime("%Y%m%d")
            # 最近季报 的上期季报 的去年同期季报
            res['quarter_report_2_last_year'] = datetime(year - 1, 6, 30).strftime("%Y%m%d")

            # 最近季报 的上上期季报
            res['quarter_report_3'] = datetime(year, 3, 31).strftime("%Y%m%d")
            # 最近季报 的上上上期季报
            res['quarter_report_4'] = datetime(year - 1, 12, 31).strftime("%Y%m%d")

            # 去年年报
            res['annual_report_date_last_year'] = datetime(year - 1, 12, 31).strftime("%Y%m%d")

        else:
            print('month number is error')

        return res

    def get_last_stock_quarter_date(self, date):

        cur_date = self.change_to_datetime(date)
        year = cur_date.year
        month = cur_date.month

        if month in [1, 2, 3, 4]:
            return datetime(year - 1, 9, 30).strftime("%Y%m%d")
        elif month in [5, 6, 7, 8]:
            return datetime(year, 3, 31).strftime("%Y%m%d")
        elif month in [9, 10]:
            return datetime(year, 6, 30).strftime("%Y%m%d")
        elif month in [11, 12]:
            return datetime(year, 9, 30).strftime("%Y%m%d")
        else:
            print('month number is error')
            return None

    @staticmethod
    def change_to_str(date):

        if type(date) in [np.int, np.float]:
            date_int = str(int(date))
            return date_int

        try:
            date_int = datetime.strftime(date, '%Y%m%d')
            return date_int
        except:
            pass

        try:
            date_int = datetime.strptime(str(date), '%Y-%m-%d').strftime('%Y%m%d')
            return date_int
        except:
            pass

        try:
            date_int = datetime.strptime(str(date), '%Y/%m/%d').strftime('%Y%m%d')
            return date_int
        except:
            pass

        return str(date)

    def get_trade_date_diff(self, beg_date, end_date):

        beg_date = self.get_trade_date_offset(beg_date, 0)
        end_date = self.get_trade_date_offset(end_date, 0)

        date_series = self.get_trade_date_series(beg_date, end_date)
        diff_number = date_series.index(end_date) - date_series.index(beg_date)
        return diff_number

    def change_to_str_hyphen(self, date):

        date = self.change_to_str(date)
        date = datetime.strptime(str(date), '%Y%m%d').strftime('%Y-%m-%d')
        return date

    def change_to_datetime(self, date):
        date = self.change_to_str(date)
        date = datetime.strptime(str(date), '%Y%m%d')
        return date

if __name__ == '__main__':

    print("################################################################################")
    date = Date()
    # date.load_trade_date_series_all()
    #
    # print("################################################################################")
    # print(date.get_trade_date_series('2007-12-31', datetime(2018, 12, 31), 'S'))
    # print(date.get_trade_date_offset(20180707, -20))
    # print(date.get_trade_date_last_month_end_day(20180707))
    # print(date.get_trade_date_month_end_day(20180707))
    #
    # print(date.get_normal_date_series('2010/3/3', 20100306))
    # print(date.get_normal_date_last_month_end_day('2010/1/3'))
    # print(date.get_normal_date_month_end_day('2010/1/3'))
    # print(date.get_normal_date_month_first_day('2010/3/3'))
    #
    # print("################################################################################")
    # print(date.change_to_str('2017-08-08'))
    # print(date.change_to_str('2017/8/8'))
    # print(date.change_to_str(20170808))
    # print(date.change_to_str('20170808'))
    # print(date.change_to_str(datetime(2017, 8, 8)))
    # print(date.get_last_fund_quarter_date("20180702"))
    #
    # print("################################################################################")
    # print(date.get_factor_date_dict(datetime.today()))

    print(Date().get_trade_date_offset(end_date="20040116", offset_num=10))

