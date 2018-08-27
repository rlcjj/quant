import numpy as np


def fund_code_add_postfix(code):

    if type(code) in [np.float]:
        code = int(code)

    code_str = str(code)
    if len(code_str) < 6:
        code_str = (6 - len(code_str)) * "0" + code_str + ".OF"
    else:
        code_str += ".OF"
    return code_str


def stock_code_add_postfix(code):

    if type(code) in [np.float]:
        code = int(code)

    code_str = str(code)
    if len(code_str) < 6:
        code_str = (6 - len(code_str)) * "0" + code_str
    if code_str[0] in ['6', "T"]:
        code_str += '.SH'
    else:
        code_str += '.SZ'
    return code_str


def stock_code_drop_postfix(code):

    code_str = stock_code_add_postfix(code)
    code_str = code_str[0:6]
    return code_str


def fund_code_drop_postfix(code):
    code_str = fund_code_add_postfix(code)
    code_str = code_str[0:6]
    return code_str


def get_stcok_market(code):
    code = stock_code_add_postfix(code)
    market = code[7:9]
    return market

if __name__ == "__main__":

    print(fund_code_add_postfix("000002"))
    print(fund_code_add_postfix(2))
    print(fund_code_add_postfix("002"))

    print(stock_code_add_postfix("T00002"))
    print(stock_code_add_postfix(300223))
    print(stock_code_add_postfix("600002"))
    print(stock_code_add_postfix(23))

    print(get_stcok_market(2))
    print(stock_code_add_postfix(2.0))


