import pandas as pd
import cx_Oracle
from quant.param.param import Parameter


class FinDb(object):

    """
    财汇数据库下载数据
    connect()
    close()
    load_raw_data()
    load_raw_data_filter()
    load_raw_data_filter_period()
    """

    def __init__(self):

        self.ip = '10.1.0.34'
        self.port = '1526'
        self.db_name = 'FINDDATA'
        self.usr_name = 'findb'
        self.usr_password = 'findb2017!!'
        self.tns_name = None
        self.conn = None
        self.cursor = None

    def connect(self):
        self.tns_name = cx_Oracle.makedsn(self.ip, self.port, self.db_name)
        self.conn = cx_Oracle.connect(self.usr_name, self.usr_password, self.tns_name)
        self.cursor = self.conn.cursor()

    def close(self):
        self.cursor.close()
        self.conn.close()

    def load_raw_data(self, factor_name):

        table_name, field_en, filter_field, field_ch = Parameter().get_load_findb_param(factor_name)
        field_en_str = ','.join(field_en)
        self.connect()
        self.cursor.execute('SELECT ' + field_en_str + ' FROM ' + table_name)

        rows = self.cursor.fetchall()
        data_df = pd.DataFrame(rows, columns=field_ch)
        self.close()

        return data_df

    def load_raw_data_filter(self, factor_name, filter_val):

        table_name, field_en, filter_field, field_ch = Parameter().get_load_findb_param(factor_name)
        self.connect()

        field_en_str = ','.join(field_en)
        self.cursor.execute('SELECT ' + field_en_str + ' FROM ' + table_name +
                            ' WHERE ' + filter_field + '=' + str(filter_val))

        rows = self.cursor.fetchall()
        data_df = pd.DataFrame(rows, columns=field_ch)
        self.close()
        return data_df

    def load_raw_data_filter_period(self, factor_name, beg_val, end_val):

        table_name, field_en, filter_field, field_ch = Parameter().get_load_findb_param(factor_name)
        self.connect()

        field_en_str = ','.join(field_en)
        print(table_name, field_en, filter_field, field_ch)
        self.cursor.execute('SELECT ' + field_en_str + ' FROM ' + table_name +
                            ' WHERE ' + filter_field + '<' + end_val + " AND " + filter_field + '>' + beg_val)

        rows = self.cursor.fetchall()
        data_df = pd.DataFrame(rows, columns=field_ch)
        self.close()
        return data_df

if __name__ == '__main__':

    print(FinDb().load_raw_data("Fund_Basic_Info"))
    print(FinDb().load_raw_data_filter("Sec_Basic_Info", 101))
