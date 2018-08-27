import pandas as pd


# 去重行和列
def drop_duplicated(data):
    
    ind_noduplicated = data.index[~data.index.duplicated(keep='first')]
    col_notduplicated = data.columns[~data.columns.duplicated(keep='first')]
    data = data.ix[ind_noduplicated, col_notduplicated]
    return data


# 增加新的 pandas 行，若有则覆盖 若没有则增加
def pandas_add_row(old_data, new_data):
    
    old_data = drop_duplicated(old_data)
    new_data = drop_duplicated(new_data)

    old_columns = set(old_data.columns)
    new_columns = set(new_data.columns)
    old_index = set(old_data.index)
    new_index = set(new_data.index)

    add_index = list(new_index - old_index)
    and_index = list(old_index & new_index)

    add_columns = list(new_columns - old_columns)
    and_columns = list(old_columns & new_columns)

    and_index.sort()
    add_index.sort()

    print(' ReWrite Index At ', list(and_index))
    print(' Add New Index At ', list(add_index))

    # 重复的覆盖 新的数据合并
    old_data.loc[and_index, and_columns] = new_data.loc[and_index, and_columns]
    res = pd.concat([old_data, new_data.ix[add_index, :]], axis=0)

    res_index = list(res.index)
    res_index.sort()
    res = res.ix[res_index, :]
    
    return res

if __name__ == '__main__':

    data = pd.DataFrame([[1, 'hh'],
                         [3, 'kk'],
                         [4, 'll']], index=pd.date_range(start='20171229', periods=3), columns=['int', 'str'])

    data_add = pd.DataFrame([], index=pd.date_range(start='20171230', periods=4), columns=['int', 'str', 'nan'])
    data_add['int'] = 10
    data_add['str'] = 'str'
    data_add['nan'] = 'hhh'

    print(drop_duplicated(data))
    print(drop_duplicated(data_add))
    print(pandas_add_row(data, data_add))