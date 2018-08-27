import os
import pandas as pd
import inspect


class Parameter(object):

    def __init__(self, path=r'D:\Program Files (x86)\anaconda\Lib\site-packages\quant\param\file'):

        self.path = path
        self.load_findb_name = 'load_findb_param.xlsx'
        self.read_name = 'read_param.xlsx'
        self.load_name = 'load_param.xlsx'

    def get_read_file(self, name):

        file_name = os.path.join(self.path, self.read_name)
        data = pd.read_excel(file_name, encoding='gbk')
        data = data.fillna("")

        if len(data[data.NAME == name].index) != 0:
            index = data[data.NAME == name].index.tolist()[0]
            path_or_file = os.path.join(data.ix[index, 'PATH'], data.ix[index, 'SUB_PATH'],
                                        data.ix[index, "FILE_NAME"])
        else:
            path_or_file = ""
            print(" The Input Name is no exist, Please Confirm Your Name. " + inspect.stack()[1][1])
        return path_or_file

    def get_load_findb_out_file(self, name):

        file_name = os.path.join(self.path, self.load_findb_name)
        data = pd.read_excel(file_name, encoding='gbk')
        data = data.fillna("")

        if len(data[data.NAME == name].index) != 0:
            index = data[data.NAME == name].index.tolist()[0]
            path_or_file = os.path.join(data.ix[index, 'OUTPUT_PATH'], data.ix[index, 'OUTPUT_SUB_PATH'],
                                        data.ix[index, "OUTPUT_FILE"])
        else:
            path_or_file = ""
            print(" The Input Name is no exist, Please Confirm Your Name. " + inspect.stack()[1][1])
        return path_or_file

    @staticmethod
    def change_str_to_list(in_str):

        in_str = in_str.replace('[', '')
        in_str = in_str.replace(']', '')
        in_str = in_str.replace(' ', '')
        in_str = in_str.replace('\'', '')
        in_str = in_str.replace("\"", "")
        in_str = in_str.replace("\n", "")
        str_list = in_str.split(',')
        return str_list

    def get_load_findb_param(self, name):

        file_name = os.path.join(self.path, self.load_findb_name)
        data = pd.read_excel(file_name, encoding='gbk')
        data = data.fillna("")
        if len(data[data.NAME == name].index) != 0:
            index = data[data.NAME == name].index.tolist()[0]
            table = data.ix[index, 'LOAD_TABLE']
            fileds_list_en = self.change_str_to_list(data.ix[index, 'LOAD_FIELD_EN'])
            fileds_list_ch = self.change_str_to_list(data.ix[index, 'LOAD_FIELD_CH'])
            filter_field = data.ix[index, "FILTER_FIELD"]
        else:
            table, fileds_list_en, filter_field, fileds_list_ch = "", "", "", ""
            print(" The Input Name is no exist, Please Confirm Your Name. " + inspect.stack()[1][1])
        return table, fileds_list_en, filter_field, fileds_list_ch

    def get_load_findb_val_name(self, name):

        file_name = os.path.join(self.path, self.load_findb_name)
        data = pd.read_excel(file_name, encoding='gbk')
        data = data.fillna("")
        if len(data[data.NAME == name].index) != 0:
            index = data[data.NAME == name].index.tolist()[0]
            val_name = data.ix[index, 'VAL_NAME']
            val_name = self.change_str_to_list(val_name)[0]
        else:
            val_name = None
            print(" The Input Name is no exist, Please Confirm Your Name. " + inspect.stack()[1][1])
        return val_name

    def get_load_out_file(self, name):

        file_name = os.path.join(self.path, self.load_name)
        data = pd.read_excel(file_name, encoding='gbk')
        data = data.fillna("")

        if len(data[data.NAME == name].index) != 0:
            index = data[data.NAME == name].index.tolist()[0]
            path_or_file = os.path.join(data.ix[index, 'OUTPUT_PATH'], data.ix[index, 'OUTPUT_SUB_PATH'],
                                        data.ix[index, "OUTPUT_FILE"])
        else:
            path_or_file = ""
            print(" The Input Name is no exist, Please Confirm Your Name. " + inspect.stack()[1][1])
        return path_or_file

    def get_load_in_file(self, name):

        file_name = os.path.join(self.path, self.load_name)
        data = pd.read_excel(file_name, encoding='gbk')
        data = data.fillna("")

        if len(data[data.NAME == name].index) != 0:
            index = data[data.NAME == name].index.tolist()[0]
            path_or_file = os.path.join(data.ix[index, 'INPUT_PATH'], data.ix[index, 'INPUT_SUB_PATH'],
                                        data.ix[index, "INPUT_FILE"])
        else:
            path_or_file = ""
            print(" The Input Name is no exist, Please Confirm Your Name. " + inspect.stack()[1][1])
        return path_or_file


if __name__ == '__main__':

    print(Parameter().get_read_file("Barra_Factor_Return"))
    print(Parameter().get_read_file("Trade_Date"))
    print(Parameter().get_load_findb_out_file("Unit_Nav"))
    print(Parameter().get_load_findb_param("Unit_Nav"))
    print(Parameter().get_load_findb_param("Sec_Basic_Info"))
    print(Parameter().get_load_in_file("Barra_Factor_Return"))
    print(Parameter().get_load_out_file("Barra_Factor_Return"))
    print(Parameter().get_load_findb_val_name("Unit_Nav"))


