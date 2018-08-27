import h5py
import pandas as pd
import os
import numpy as np


class HdfMfc(object):

    """
    泰达 格式的 hdf 文件的读取和写入
    """

    def __init__(self, filename='', dsname=''):

        self.filename = filename
        self.dsname = dsname
        self.codestr = 'CodeStr'
        self.datestr = 'DateStr'

    def read_hdf_code(self):

        f = h5py.File(self.filename, 'a')
        codestr = f['CodeStr'][...][0]
        f.close()
        codestr_utf = list(map(lambda x: x.decode(encoding="utf-8"), list(codestr)))
        if '.SZ' in codestr_utf[0]:
            codestr_format = codestr_utf
        else:
            codestr_format = list(
                map(lambda x: str(x) + '.SH' if str(x)[0] in ['6', 'T'] else str(x) + '.SZ', codestr_utf))
        return codestr_format

    def read_hdf_date(self):

        f = h5py.File(self.filename, 'a')
        datestr = f['DateStr'][...][0]
        f.close()
        datestr_utf = list(map(lambda x: x.decode(encoding="utf-8"), list(datestr)))
        return datestr_utf

    def read_hdf_data(self, dsname, type='f'):

        f = h5py.File(self.filename, 'a')
        data = f[dsname][...]
        f.close()
        data_pd = pd.DataFrame(data)
        if type == 's':
            data = data_pd.applymap(lambda x: x.decode(encoding="utf-8")).values
        else:
            data = data_pd.values
        return data

    def read_hdf_factor(self, dsname, type='f'):

        index = self.read_hdf_code()
        columns = self.read_hdf_date()
        data = self.read_hdf_data(dsname, type=type)
        data_pd = pd.DataFrame(data, index=index, columns=columns)
        return data_pd

    def write_hdf_data(self, filename, dsname, data, type='f', clevel=9, cmethod="gzip"):

        f = h5py.File(filename)

        if type == 'f':
            dt = np.float64
        elif type == 's':
            dt = h5py.special_dtype(vlen=bytes)
        else:
            print('the type of data is illegal')

        if dsname in ['CodeStr', 'DateStr']:
            f.create_dataset(dsname, shape=(1, len(data)), data=data,
                             compression=cmethod, compression_opts=clevel, dtype=dt)
        else:
            f.create_dataset(dsname, shape=data.shape, data=data,
                             compression=cmethod, compression_opts=clevel, dtype=dt)
        f.close()
        return True

    def write_hdf_factor(self, filename, dsname, data, type='f'):

        if os.path.exists(filename):
            os.remove(filename)

        if ('.SZ' in data.index[0]) or ('.SH' in data.index[0]):
            pass
        else:
            data.index = data.index.map(lambda x: str(x) + '.SH' if str(x)[0] in ['6', 'T'] else str(x) + '.SZ')

        data.index = data.index.map(str)
        data.columns = data.columns.map(str)

        code_str = data.index.values
        # code_str = list(map(lambda x: bytes(x, encoding="utf8"), list(code_str)))
        date_str = data.columns.values
        # date_str = list(map(lambda x: bytes(x, encoding="utf8"), list(date_str)))

        # filename = filename.encode('mbcs')
        # print(filename)
        """
        只能是英文路径
        """

        factor = data.astype(np.float64).values

        self.write_hdf_data(filename, 'CodeStr', code_str, type='s')
        self.write_hdf_data(filename, 'DateStr', date_str, type='s')
        self.write_hdf_data(filename, dsname, factor, type=type)

        return True


if __name__ == '__main__':

    from quant.stock.stock import Stock
    filename = Stock().get_primary_factor_mfc_file(factor_name="Pct_chg")
    dsname = 'Pct_chg'
    h = HdfMfc(filename, dsname)
    data = h.read_hdf_factor(dsname)
    print(data)

    # filename = 'C:\\Users\\doufucheng\\OneDrive\\Desktop\\Pct_chg.h5'
    # h.write_hdf_factor(filename, dsname, data, type='f')
    # h = HdfMfc(filename, dsname)
    # data = h.read_hdf_factor(dsname)
    # print(data)

    data = pd.DataFrame([], index=['000001.SZ', '000002.SZ'], columns=['20171229', '20180101'])
    filename = 'C:\\Users\\doufucheng\\OneDrive\\Desktop\\Pct_chg.h5'
    h.write_hdf_factor(filename, dsname, data, type='f')