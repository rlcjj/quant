import os
from datetime import datetime
import pandas as pd
from quant.data_source.my_ftp import MyFtp
from quant.utility_fun.code_format import stock_code_add_postfix
from quant.stock.date import Date
from quant.param.param import Parameter


class MfcData(object):

    """
    1、下载FTP上的持仓文件和股票库文件
    load_holding_date()
    change_holding_date()
    load_stock_pool_date()

    2、读取本地持仓数据
    get_fund_asset()
    get_fund_security()
    get_group_security()
    get_trade_statement()
    get_fund_nav()

    3、计算和获取Barra因子暴露
    cal_barra_exposure()
    get_barra_exposure()
    """

    def __init__(self):

        self.name = 'Mfc_Data'

    def load_holding_date(self, date):

        load_file_list = ['01AfterTA.ok', '01BeforeTA.ok',
                          '01HIS成交回报.xls', '01HIS委托流水.xls', '01TODAY单元资产.xls',
                          '01TODAY基金证券.xls', '01TODAY基金资产.xls', '01TODAY组合证券.xls']

        ftp_path = Parameter().get_load_in_file(self.name)
        local_path = Parameter().get_load_out_file(self.name)
        local_path = os.path.join(local_path, 'raw_file')

        date_int = Date().change_to_str(date)
        local_sub_path = os.path.join(local_path, date_int)
        ftp_sub_path = os.path.join(ftp_path, date_int)

        if not os.path.exists(local_sub_path):
            os.mkdir(local_sub_path)

        ftp = MyFtp()
        ftp.connect()

        print("######################################### Loading Ftp File #########################################")

        ftp.load_file_folder_change_name(ftp_sub_path, local_sub_path, load_file_list, load_file_list)
        ftp.close()

    def load_stock_pool_date(self, date):

        pool_file = os.path.join(Parameter().get_read_file("Mfc_Fund"), "Stock_Pool_Ftp.xlsx")
        pool_data = pd.read_excel(pool_file, encoding='gbk')
        pool_data = pool_data.dropna(subset=['Pool_Ch', 'Pool_Ftp'])
        pool_ch = list(pool_data['Pool_Ch'].values)
        pool_ftp = list(pool_data['Pool_Ftp'].values)

        ftp_path = Parameter().get_load_in_file(self.name)
        local_path = Parameter().get_load_out_file(self.name)
        local_path = os.path.join(local_path, 'raw_file')

        date_int = Date().change_to_str(date)
        local_sub_path = os.path.join(local_path, date_int)
        ftp_sub_path = os.path.join(ftp_path, date_int)

        if not os.path.exists(local_sub_path):
            os.mkdir(local_sub_path)

        ftp = MyFtp()
        ftp.connect()

        print("######################################### Loading Ftp File #########################################")

        ftp.load_file_folder_change_name(ftp_sub_path, local_sub_path, pool_ftp, pool_ch)
        ftp.close()

    def change_holding_date(self, date):

        date_before = Date().get_trade_date_offset(date, -1)

        local_path = Parameter().get_load_out_file(self.name)
        local_path = os.path.join(local_path, 'raw_file')

        date_int = Date().change_to_str(date)
        date_before = Date().change_to_str(date_before)
        before_path = os.path.join(local_path, date_int)
        after_path = Parameter().get_read_file(self.name)

        change_file_dick = {'01HIS成交回报.xls': "3_成交回报\\成交回报_",
                            '01TODAY单元资产.xls': "4_单元资产\\单元资产_",
                            '01TODAY基金证券.xls': "5_基金证券\\基金证券_",
                            '01TODAY基金资产.xls': "2_基金资产\\基金资产_",
                            '01TODAY组合证券.xls': "6_组合证券\\组合证券_"}

        print("######################################### Change Ftp File #########################################")

        for b_file, a_file in change_file_dick.items():

            before_file = os.path.join(before_path, b_file)

            if os.path.exists(before_file):

                data = pd.read_excel(before_file, index_col=[0], encoding='gbk')
                after_file = after_path + a_file + date_before + '.csv'
                print("Change File into ", after_file)
                data.to_csv(after_file)
            else:
                print("Tne File At ", date_int, " is No Exist. ")

    def get_fund_asset(self, date):

        date_int = Date().change_to_str(date)
        path = Parameter().get_read_file(self.name)
        file = os.path.join(path, '2_基金资产', '基金资产_' + str(date_int) + '.csv')
        data = pd.read_csv(file, encoding='gbk', thousands=',')
        return data

    def get_fund_security(self, date):

        date_int = Date().change_to_str(date)
        path = Parameter().get_read_file(self.name)
        file = os.path.join(path, '5_基金证券', '基金证券_' + str(date_int) + '.csv')
        data = pd.read_csv(file, encoding='gbk', thousands=',')
        return data

    def get_group_security(self, date):

        date_int = Date().change_to_str(date)
        path = Parameter().get_read_file(self.name)
        file = os.path.join(path, '6_组合证券', '组合证券_' + str(date_int) + '.csv')
        data = pd.read_csv(file, encoding='gbk', thousands=',')
        return data

    def get_trade_statement(self, date):

        date_int = Date().change_to_str(date)
        path = Parameter().get_read_file(self.name)
        file = os.path.join(path, '3_成交回报', '成交回报_' + str(date_int) + '.csv')
        data = pd.read_csv(file, encoding='gbk', thousands=',')
        return data

    @staticmethod
    def get_file_tradedate(sub_path, begin_date_int, end_date_int):

        dir_list = os.listdir(sub_path)
        date_list = list(map(lambda x: str(x)[5:13], dir_list))
        date_list_pd = pd.DataFrame(date_list, index=date_list, columns=['trade_date'])
        date_period = list(date_list_pd.ix[begin_date_int:end_date_int, 'trade_date'].values)
        return date_period

    def get_fund_nav(self, fund_name, begin_date_int, end_date_int):

        path = Parameter().get_read_file(self.name)
        sub_path = os.path.join(path, '2_基金资产')

        date_list = self.get_file_tradedate(sub_path, begin_date_int, end_date_int)
        trade_date_list = Date().get_trade_date_series(begin_date_int, end_date_int)
        date_list = list(set(date_list) & set(trade_date_list))
        date_list.sort()
        cum_nav_period = pd.DataFrame([], index=date_list, columns=['单位净值', '基金份额', '净值'])

        for i in range(len(date_list)):

            date_int = date_list[i]
            asset = self.get_fund_asset(date_int)
            asset.index = asset['基金名称']
            cum_nav_period.ix[date_int, '基金份额'] = asset.ix[fund_name, '基金份额']
            cum_nav_period.ix[date_int, '净值'] = asset.ix[fund_name, '净值']
            cum_nav_period['单位净值'] = cum_nav_period['净值'] / cum_nav_period['基金份额']
            cum_nav_period = pd.DataFrame(cum_nav_period['单位净值'].values, index=cum_nav_period.index, columns=['单位净值'])

        return cum_nav_period

    def get_fund_nav_adjust(self, fund_name, begin_date_int, end_date_int):

        file = '\\\\10.1.9.208\\fe\\fe_public\\业绩归因\\input\\dividend.csv'
        did_file = pd.read_csv(file, index_col=[0], encoding='gbk')
        did_file['DATETIME'] = did_file['DATETIME'].map(str)
        did_data = did_file[did_file.index == fund_name]

        path = Parameter().get_read_file(self.name)
        sub_path = os.path.join(path, '2_基金资产')

        date_list = self.get_file_tradedate(sub_path, begin_date_int, end_date_int)
        trade_date_list = Date().get_trade_date_series(begin_date_int, end_date_int)
        date_list = list(set(date_list) & set(trade_date_list))
        date_list.sort()
        cum_nav_period = pd.DataFrame([], index=date_list, columns=['单位净值', '基金份额', '净值'])

        for i in range(len(date_list)):

            date_int = date_list[i]
            asset = self.get_fund_asset(date_int)
            asset.index = asset['基金名称']
            cum_nav_period.ix[date_int, '基金份额'] = asset.ix[fund_name, '基金份额']
            cum_nav_period.ix[date_int, '净值'] = asset.ix[fund_name, '净值']
            cum_nav_period['单位净值'] = cum_nav_period['净值'] / cum_nav_period['基金份额']

        did_date = pd.DataFrame(did_data['DIVD_ASSET'].values, index=did_data['DATETIME'], columns=['分红资产'])
        all_data = pd.concat([cum_nav_period, did_date], axis=1)
        all_data['分红资产'] = all_data['分红资产'].fillna(0.0)

        all_data['分红净值'] = all_data['分红资产'] / all_data['基金份额']
        all_data['累计分红净值'] = all_data['分红净值'].cumsum()
        all_data['累计净值'] = all_data['累计分红净值'] + all_data['单位净值']
        all_data['累计净值涨跌幅'] = all_data['累计净值'].pct_change()
        all_data['累计复权分红净值'] = (all_data['累计分红净值'] * all_data['累计净值涨跌幅']).cumsum()
        all_data['累计复权净值'] = all_data['累计净值'] + all_data['累计复权分红净值']
        result = pd.DataFrame(all_data['累计复权净值'].values, index=all_data.index, columns=['累计复权净值'])

        return result

    def get_mfc_name(self, fund_code):

        path = Parameter().get_read_file("Mfc_Fund")
        file = os.path.join(path, "Fund_Info.xlsx")
        data = pd.read_excel(file)
        name = data[data['Code'] == fund_code].values[0][0]
        return name

    def get_mfc_code(self, fund_name):

        path = Parameter().get_read_file("Mfc_Fund")
        file = os.path.join(path, "Fund_Info.xlsx")
        data = pd.read_excel(file)
        name = data[data['Name'] == fund_name].values[0][0]
        return name

    def cal_barra_exposure(self, fund_code, date):

        date = Date().get_trade_date_offset(date, 0)
        fund_name = self.get_mfc_name(fund_code)
        holding_data = self.get_fund_security(date)
        holding_data = holding_data[["基金名称", "证券代码", "市值比净值(%)"]]
        holding_data = holding_data[holding_data["基金名称"] == fund_name]
        holding_data.columns = ["FundName", "StockCode", "Weight"]
        holding_data.StockCode = holding_data.StockCode.map(stock_code_add_postfix)
        holding_data.index = holding_data.StockCode
        holding_data.Weight /= 100.0

    def get_mfcteda_public_fund_nav_wind(self, fund_code, beg_date, end_date):

        path = 'E:\\3_Data\\6_mfcteda_fund_data\\3_Fund_Nav\public_fund\\'
        beg_date = Date().change_to_str(beg_date)
        end_date = Date().change_to_str(end_date)
        file = os.path.join(path, fund_code + '.csv')
        if os.path.exists(file):
            data = pd.read_csv(file, index_col=[0], encoding='gbk')
            data.index = data.index.map(Date().change_to_str)
            data = data.loc[beg_date:end_date, :]
        else:
            data = None
            print(" Fund %s No Exist! " % fund_code)
        return data

    def get_mfcteda_public_fund_pct_wind(self, fund_code, beg_date, end_date):

        beg_date_before = Date().get_trade_date_offset(beg_date, -1)
        data = self.get_mfcteda_public_fund_nav_wind(fund_code, beg_date_before, end_date)
        data = data.dropna()
        data = data.pct_change()
        data = data.loc[beg_date:end_date, :]

        return data

    def get_fund_asset_period(self, fund_id, beg_date, end_date, columns=None):

        # fund_id = 38
        date_series = Date().get_trade_date_series(beg_date, end_date)
        if columns is None:
            columns = ['基金编号', '基金名称', '净值', '基金份额', '单位净值',
                       '股票资产', '债券资产', '当前现金余额', '回购资产', '基金资产',
                       '股票当日浮动盈亏', '债券当日浮动盈亏', '基金当日浮动盈亏',
                       '当日股票总盈亏金额', '当日债券总盈亏金额',
                       '当日买金额', '当日卖金额']

        result = pd.DataFrame([], index=date_series, columns=columns)

        for i in range(len(date_series)):
            date = date_series[i]
            try:
                asset = self.get_fund_asset(date)
                asset = asset[asset['基金编号'] == fund_id]
                asset.index = [date]
                result.loc[date, columns] = asset.loc[date, columns]
            except:
                pass
        result = result.dropna(how='all')
        return result

    def load_his_data(self):

        file_ftp = ["新综合信息查询_基金证券201501.xls",
                    "新综合信息查询_基金证券201502.xls",
                    "新综合信息查询_基金证券201503.xls",
                    "新综合信息查询_基金证券201504.xls",
                    "新综合信息查询_基金证券201505.xls",
                    "新综合信息查询_基金证券201506.xls",
                    "新综合信息查询_基金证券201507.xls",
                    "新综合信息查询_基金证券201508.xls",
                    "新综合信息查询_基金证券201509.xls",
                    "新综合信息查询_基金证券201510.xls",
                    "新综合信息查询_基金证券201511.xls",
                    "新综合信息查询_基金证券201512.xls",
                    "新综合信息查询_基金证券201601.xls",
                    "新综合信息查询_基金证券201602.xls",
                    "新综合信息查询_基金证券201603.xls",
                    "新综合信息查询_基金证券201604.xls",
                    "新综合信息查询_基金证券201605.xls",
                    "新综合信息查询_基金证券201606.xls",
                    "新综合信息查询_基金证券201607.xls",
                    "新综合信息查询_基金证券201608_1.xls",
                    "新综合信息查询_基金证券201608_2.xls",
                    "新综合信息查询_基金证券201609_1.xls",
                    "新综合信息查询_基金证券201609_2.xls",
                    "新综合信息查询_基金证券201610_1.xls",
                    "新综合信息查询_基金证券201610_2.xls",
                    "新综合信息查询_基金证券201611_1.xls",
                    "新综合信息查询_基金证券201611_2.xls",
                    "新综合信息查询_基金证券201612_1.xls",
                    "新综合信息查询_基金证券201612_2.xls",
                    "新综合信息查询_基金证券201701_1.xls",
                    "新综合信息查询_基金证券201701_2.xls",
                    "新综合信息查询_基金证券201702_1.xls",
                    "新综合信息查询_基金证券201702_2.xls",
                    "新综合信息查询_基金证券201703_1.xls",
                    "新综合信息查询_基金证券201703_2.xls",
                    "新综合信息查询_基金证券201703_3.xls",
                    "新综合信息查询_基金证券201704_1.xls",
                    "新综合信息查询_基金证券201704_2.xls",
                    "新综合信息查询_基金证券201704_3.xls",
                    "新综合信息查询_基金证券201705_1.xls",
                    "新综合信息查询_基金证券201705_2.xls",
                    "新综合信息查询_基金证券201705_3.xls",
                    "新综合信息查询_基金证券201706_1.xls",
                    "新综合信息查询_基金证券201706_2.xls",
                    "新综合信息查询_基金证券201706_3.xls",
                    "新综合信息查询_基金证券201707_1.xls",
                    "新综合信息查询_基金证券201707_2.xls",
                    "新综合信息查询_基金证券201707_3.xls",
                    "新综合信息查询_基金证券201708_1.xls",
                    "新综合信息查询_基金证券201708_2.xls",
                    "新综合信息查询_基金证券201708_3.xls",
                    "新综合信息查询_基金证券201708_4.xls",
                    "新综合信息查询_基金证券201709_1.xls",
                    "新综合信息查询_基金证券201709_2.xls",
                    "新综合信息查询_基金证券201709_3.xls",
                    "新综合信息查询_基金证券201710_1.xls",
                    "新综合信息查询_基金证券201710_2.xls",
                    "新综合信息查询_基金证券201710_3.xls",
                    "新综合信息查询_基金证券201711_1.xls",
                    "新综合信息查询_基金证券201711_2.xls",
                    "新综合信息查询_基金证券201711_3.xls",
                    "新综合信息查询_基金证券201712_1.xls",
                    "新综合信息查询_基金证券201712_2.xls",
                    "新综合信息查询_基金证券201712_3.xls",
                    "新综合信息查询_基金证券201801_1.xls",
                    "新综合信息查询_基金证券201801_2.xls",
                    "新综合信息查询_基金证券201801_3.xls",
                    "新综合信息查询_基金证券201802_1.xls",
                    "新综合信息查询_基金证券201802_2.xls",
                    "新综合信息查询_基金证券201802_3.xls",
                    "新综合信息查询_基金证券201803_1.xls",
                    "新综合信息查询_基金证券201803_2.xls",
                    "新综合信息查询_基金证券201803_3.xls",
                    "新综合信息查询_基金证券201803_4.xls",
                    "新综合信息查询_基金证券201804_1.xls",
                    "新综合信息查询_基金证券201804_2.xls",
                    "新综合信息查询_基金证券201804_3.xls",
                    "新综合信息查询_基金证券201804_4.xls",
                    "新综合信息查询_基金证券201805_1.xls",
                    "新综合信息查询_基金证券201805_2.xls",
                    "新综合信息查询_基金证券201805_3.xls",
                    "新综合信息查询_基金证券201805_4.xls",
                    "新综合信息查询_基金证券201806_1.xls",
                    "新综合信息查询_基金证券201806_2.xls",
                    "新综合信息查询_基金证券201806_3.xls",
                    "新综合信息查询_基金资产2015.xls",
                    "新综合信息查询_基金资产2016.xls",
                    "新综合信息查询_基金资产2017.xls",
                    "新综合信息查询_基金资产2018.xls",
                    ]
        file_local = file_ftp

        ftp_path = '\\hisData\\'
        local_path = "E:\\3_Data\\6_mfcteda_fund_data\\0_原始持仓文件\\2_窦福成_201806_now\\his_raw_file\\"

        ftp = MyFtp()
        ftp.connect()

        print("######################################### Loading Ftp File #########################################")

        ftp.load_file_folder_change_name(ftp_path, local_path, file_ftp, file_local)
        ftp.close()

    def change_his_data_file(self):

        in_path = "E:\\3_Data\\6_mfcteda_fund_data\\0_原始持仓文件\\2_窦福成_201806_now\\his_raw_file\\"
        out_path = 'E:\\3_Data\\6_mfcteda_fund_data\\1_整理持仓文件\\'
        dirlist = os.listdir(in_path)
        dirlist_security = list(filter(lambda x: "基金证券" in x, dirlist))
        dirlist_security.sort()
        dirlist_asset = list(filter(lambda x: "基金资产" in x, dirlist))
        dirlist_asset.sort()

        for i in range(len(dirlist_security)):

            file = dirlist_security[i]
            in_file = os.path.join(in_path, file)
            data = pd.read_excel(in_file, index_col=[0])
            data = data.dropna(subset=['持仓日期'])
            date_list = list(set(data['持仓日期'].values))
            date_list.sort()

            for i_date in range(len(date_list)):
                date = date_list[i_date]
                data_date = data[data['持仓日期'] == date]
                data_date = data_date.reset_index(drop=True)
                date_format = Date().change_to_str(date)
                out_file = os.path.join(out_path, '5_基金证券', '基金证券_' + date_format + '.csv')
                data_date.to_csv(out_file)
                print("基金证券", date_format)

        for i in range(len(dirlist_asset)):

            file = dirlist_asset[i]
            in_file = os.path.join(in_path, file)
            data = pd.read_excel(in_file, index_col=[0])
            data = data.dropna(subset=['统计日期'])
            date_list = list(set(data['统计日期'].values))
            date_list.sort()

            for i_date in range(len(date_list)):
                date = date_list[i_date]
                data_date = data[data['统计日期'] == date]
                data_date = data_date.reset_index(drop=True)
                date_format = Date().change_to_str(date)
                out_file = os.path.join(out_path, '2_基金资产', '基金资产_' + date_format + '.csv')
                data_date.to_csv(out_file)
                print("基金资产", date_format)


if __name__ == '__main__':

    lmd = MfcData()
    # date = datetime.today()
    # date = datetime(2018, 7, 6)
    # lmd.load_holding_date(date)
    # lmd.load_stock_pool_date(date)
    # lmd.change_holding_date(date)
    #
    # print(lmd.get_fund_asset(20171229))
    # print(lmd.get_fund_nav('泰达中证500指数分级', '20171229', '20180606'))
    #
    # print(MfcData().get_mfcteda_public_fund_nav_wind("229002.OF", '20171231', '20180304'))
    # print(MfcData().get_mfcteda_public_fund_pct_wind("229002.OF", '20171231', '20180304'))
    lmd.load_his_data()
    lmd.change_his_data_file()
    # print(MfcData().get_fund_asset_period(38, '20171231', '20180304'))



