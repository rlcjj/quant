import zipfile
import os


def make_zip_folder(source_dir, output_filename):

    zipf = zipfile.ZipFile(output_filename, 'w')
    pre_len = len(os.path.dirname(source_dir))

    for parent, dirnames, filenames in os.walk(source_dir):
        for filename in filenames:
            pathfile = os.path.join(parent, filename)
            arcname = pathfile[pre_len:].strip(os.path.sep)  # 相对路径
            zipf.write(pathfile, arcname)
    zipf.close()


def make_zip_file(source_dir, output_filename, zip_file_list):

    zipf = zipfile.ZipFile(output_filename, 'w')

    for filename in zip_file_list:
        pathfile = os.path.join(source_dir, filename)
        arcname = filename
        zipf.write(pathfile, arcname)
    zipf.close()


def unzip_file(zip_file, upzip_folder):

    file_zip = zipfile.ZipFile(zip_file, 'r')
    for file in file_zip.namelist():
        file_zip.extract(file, upzip_folder)
    file_zip.close()
    # os.remove(zip_file)


if __name__ == '__main__':

    # source_dir = 'C:\\Users\\doufucheng\\OneDrive\\Desktop\\QFII\\'
    # output_filename = 'C:\\Users\\doufucheng\\OneDrive\\Desktop\\' + "qfii2.rar"
    # zip_file_list = ['机构持仓（一）：A股投资者结构变迁.pdf', '机构持仓（二）：机构行为与跟踪策略.pdf']
    # make_zip_file(source_dir, output_filename, zip_file_list)

    path = r'E:\3_数据\2_index_data\2_index_weight\raw_file\000300'
    zip_file = os.path.join(path, "000300closeweight20180625.zip")
    unzip_file(zip_file, path)