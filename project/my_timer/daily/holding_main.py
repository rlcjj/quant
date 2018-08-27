from quant.project.my_timer.daily.holding.load_holding_data import load_mfc_holding_data
from quant.project.my_timer.daily.holding.load_other_data import load_other_data
from quant.project.my_timer.daily.holding.cal_reverse_5days import cal_reverse_5days
from quant.project.my_timer.daily.holding.cal_ipo_mkt_monitor import cal_ipo_mkt_monitor
from quant.project.my_timer.daily.holding.holding_for_clj import holding_data_clj, mail_for_clj
from quant.project.my_timer.daily.holding.holding_for_liuxin import holding_data_liuxin, mail_for_liuxin
from quant.project.my_timer.daily.holding.holding_for_yangchao import holding_data_yangchao, mail_for_yangchao
from quant.project.my_timer.daily.holding.holding_for_liuyang import holding_data_liuyang, mail_for_liuyang
from datetime import datetime
from quant.param.param import Parameter


def my_main():

    project_path = Parameter().get_read_file("Mfc_Fund")
    out_path = Parameter().get_read_file("Mfc_Daily")
    today = datetime.today().strftime("%Y%m%d")
    # today = datetime(2018, 7, 3).strftime("%Y%m%d")

    load_mfc_holding_data(today)

    load_other_data(today)
    cal_reverse_5days(today, project_path, out_path)
    cal_ipo_mkt_monitor(today, project_path, out_path)

    holding_data_clj(today, project_path, out_path)
    holding_data_liuxin(today, project_path, out_path)
    holding_data_yangchao(today, project_path, out_path)
    holding_data_liuyang(today, project_path, out_path)

    mail_for_clj()
    mail_for_liuxin()
    mail_for_yangchao()
    mail_for_liuyang()

if __name__ == '__main__':

    my_main()
