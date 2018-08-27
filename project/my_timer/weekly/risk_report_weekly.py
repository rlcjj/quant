from quant.utility_fun.send_email import send_mail_mfcteda


def risk_report_weekly():

    sender_mail_name = 'fucheng.dou@mfcteda.com'  # 发送邮箱
    receivers_mail_name = ['yaoxin.liu@mfcteda.com', 'fucheng.dou@mfcteda.com']  # 接收邮箱 list
    acc_mail_name = ['jie.dai@mfcteda.com', 'jing.yuan@mfcteda.com']  # 抄送邮箱 list
    subject_header = "金融工程风险周报(2018年8月20日-8月24日)"  # 邮件标题
    body_text = '瑶歆：\n你好! 上周金融工程无风险， 供知晓， 谢谢!\n祝好\n\n窦福成\n泰达宏利基金管理有限公司\n金融工程部'
    file_path = ""
    file_name = ''
    send_mail_mfcteda(sender_mail_name, receivers_mail_name, acc_mail_name,
                      subject_header, body_text, file_path, file_name)


if __name__ == '__main__':

    risk_report_weekly()

