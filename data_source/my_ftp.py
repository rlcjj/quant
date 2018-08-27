from ftplib import FTP
import os
from datetime import datetime
from quant.stock.date import Date
from quant.param.param import Parameter


class MyFtp(object):

    """
    连接FTP服务器 用来下载上传数据文件
    默认为公司FTP服务器 也可以调整为其他FTP(如中证指数ftp)
    connect()
    close()
    load_file()
    load_file_folder_change_name()
    upload_file()
    """

    def __init__(self,
                 ip="10.253.0.70",
                 port=21,
                 user_name='doufucheng',
                 user_password="Mfcteda2018!!"):

        self.ip = str(ip)
        self.port = int(port)
        self.user_name = user_name
        self.user_password = user_password
        self.ftp = None

    def connect(self):

        self.ftp = FTP()
        self.ftp.encoding = 'utf-8'
        self.ftp.connect(self.ip, self.port)
        self.ftp.login(self.user_name, self.user_password)

    def close(self):
        self.ftp.close()

    def load_file(self, ftp_file, local_file):

        print('Begin Loading ', ftp_file, ' ......')
        ftp_path = os.path.dirname(ftp_file)
        file_name = os.path.basename(ftp_file)
        self.ftp.cwd(ftp_path)
        file_list = self.ftp.nlst()

        if file_name in file_list:
            bufsize = 1024
            fp = open(local_file, 'wb')
            self.ftp.retrbinary('RETR ' + ftp_file, fp.write, bufsize)
        else:
            print(" No Exist File in FTP ")
            pass

    def load_file_folder_change_name(self, ftp_path, local_path, ftp_file_list, local_file_list):

        for i_file in range(len(ftp_file_list)):
            ftp_file = ftp_file_list[i_file]
            local_file = local_file_list[i_file]
            ftp_file = os.path.join(ftp_path, ftp_file)
            local_file = os.path.join(local_path, local_file)
            self.load_file(ftp_file, local_file)

    def upload_file(self, ftp_file, local_file):

        print('Begin UpLoading ', ftp_file, ' ......')
        ftp_path = os.path.dirname(ftp_file)
        file_name = os.path.basename(ftp_file)
        try:
            self.ftp.cwd(ftp_path)
        except:
            self.ftp.mkd(ftp_path)
            self.ftp.cwd(ftp_path)
        bufsize = 1024
        fp = open(local_file, 'rb')
        self.ftp.storbinary('STOR ' + file_name, fp, bufsize)


if __name__ == '__main__':

    date = datetime.today()
    date_int = Date().change_to_str(date)

    ftp_path = Parameter().get_load_in_file("Mfc_Data")
    local_path = Parameter().get_load_out_file("Mfc_Data")

    local_sub_path = os.path.join(local_path, date_int)
    ftp_sub_path = os.path.join(ftp_path, date_int)

    if not os.path.exists(local_sub_path):
        os.mkdir(local_sub_path)

    ftp = MyFtp()
    ftp.connect()