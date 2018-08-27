import pandas as pd
from quant.stock.date import Date
from quant.utility_fun.code_format import stock_code_add_postfix
from datetime import datetime
from jqdatasdk import *
auth('18810515636', 'dfc19921208')


def change_code_format_from_jq(code):

    code = code.replace("XSHE", "SZ")
    code = code.replace("XSHG", "SH")
    return code


def change_code_format_to_jq(code):

    code = code.replace("SZ", "XSHE")
    code = code.replace("SH", "XSHG")
    return code


def get_all_stock_code():

    data = get_all_securities(types=['stock'], date=datetime.today())
    return data


def get_price():

    code
    data = get_price(security, start_date=None, end_date=None, frequency='daily', fields=None, skip_paused=False, fq='pre',
              count=None)



