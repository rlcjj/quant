from quant.stock.index_exposure import IndexBarraExposure
from quant.stock.index_factor import IndexFactor
from quant.stock.index_weight import IndexWeight
from datetime import datetime


class Index(IndexFactor, IndexWeight, IndexBarraExposure):

    def __init__(self):
        IndexFactor.__init__(self)
        IndexWeight.__init__(self)
        IndexBarraExposure.__init__(self)


if __name__ == "__main__":

    # Index Factor
    #############################################################################
    index = Index()
    # index.load_index_factor("000300.SH", "20171231", datetime.today())
    # index.load_index_factor_all("20180701", datetime.today())
    # index.load_index_factor("000985.CSI")
    # index.load_index_factor("HSI.HI")

    # index.load_index_factor("IXIC.GI")
    # index.load_index_factor("SPX.GI")
    # index.load_index_factor_all()
    date = datetime(2018, 7, 6)
    #
    print(index.get_index_factor("000905.SH", "20180601", date, ["CLOSE", "PE_TTM"]))
    # print(index.get_index_factor("000300.SH", "20180601", date))
    #
    # # Index Weight
    # #############################################################################
    # index.load_weight_from_ftp_date("000905.SH", date)
    index.load_weight_from_wind_date("000016.SH", date)
    # index.load_weight_china_index_date(date)
    # index.load_weight_period("000905.SH", "20180701", date)
    # index.load_weight_from_wind_date("000016.SH", date)
    #############################################################################
    # Index Exposure
    # index.cal_index_exposure_period("000300.SH", beg_date="20041229", end_date="20171229")
    # index.cal_index_exposure_period("000905.SH", beg_date="20041229", end_date="20171229")
    # index.cal_index_exposure_period("881001.WI", beg_date="20041229", end_date="20171229")
    # index.cal_index_exposure_period("000016.SH", beg_date="20041229", end_date="20171229")
    print(index.get_index_exposure_date("000300.SH", "20171231"))