import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header


def send_mail_qq(email, password, send_subject, send_message, receiver):

    sender = email
    receiver = receiver
    subject = send_subject
    smtpsever = 'smtp.qq.com'
    username = email

    # 中文需参数‘utf-8'，单字节字符不需要

    msg = MIMEText(send_message, 'plain', 'utf-8')
    msg['Subject'] = Header(subject, 'utf-8')

    server = smtplib.SMTP_SSL(smtpsever)

    try:
        # server.connect() # ssl无需这条
        server.login(username, password)  # 登陆
        server.sendmail(sender, receiver, msg.as_string())  # 发送
        print('邮件发送成功')

    except:
        print('邮件发送失败')

    server.quit()


def send_mail_mfcteda(sender_mail_name, receivers_mail_name, acc_mail_name,
                      subject_header, body_text, file_path="", file_name=""):

    # sender_mail_name = 'fucheng.dou@mfcteda.com'  # 发送邮箱
    # receivers_mail_name = ['fucheng.dou@mfcteda.com', 'doufucheng123@foxmail.com']  # 接收邮箱 list
    # acc_mail_name = ['doufucheng123@foxmail.com', 'fuchengdou@126.com']  # 抄送邮箱 list
    # subject_header = "Python 测试标题"  # 邮件标题
    # body_text = 'Python 测试内容 具体见附件.\n\n窦福成\n金融工程部\n'
    # file_path = 'C:\\Users\\doufucheng\\OneDrive\\Desktop\\'
    # file_name = 'Desktop.rar'

    mail_server_host = "10.1.0.163"  # 邮件服务器地址
    mail_server_user = "doufucheng"  # 服务器登录名
    mail_server_pass = "mfcteda2018!!"  # 服务器登陆密码

    message = MIMEMultipart('related')

    message['Subject'] = Header(subject_header, 'utf-8') # 写好 邮件标题
    message['From'] = Header(sender_mail_name, 'utf-8')  # 写好 发送者
    message['To'] = Header(';'.join(receivers_mail_name), 'utf-8')  # 写好 接收者
    message['Cc'] = Header(';'.join(acc_mail_name), 'utf-8')  # 写好 接收者

    # MIMEText有三个参数，第一个对应文本内容，第二个对应文本的格式，第三个对应文本编码

    # 文件正文
    thebody = MIMEText(body_text, 'plain', 'utf-8')
    message.attach(thebody)

    if file_name == "" or file_path == "":
        pass
    else:
        filename = os.path.join(file_path, file_name)
        att = MIMEText(open(filename, 'rb').read(), 'base64', 'utf-8')
        # att["Content-Type"] = 'application/octet-stream'
        att['Content-Disposition'] = 'attachment; filename="%s"' % file_name
        message.attach(att)

    try:
        smtpObj = smtplib.SMTP()
        smtpObj.connect(mail_server_host, 25)  # 25 为 SMTP 端口号
        smtpObj.login(mail_server_user, mail_server_pass)

        smtpObj.sendmail(sender_mail_name, receivers_mail_name, message.as_string())
        print("邮件发送成功")
    except smtplib.SMTPException:
        print("Error: 无法发送邮件")


def send_mail_126():

    email = 'fuchengdou@126.com'
    receivers = [email]
    sender = email

    # 第三方 SMTP 服务
    mail_host = "smtp.126.com"  # 设置服务器
    mail_user = email  # 用户名
    mail_pass = "dfc19921208"  # 口令

    message = MIMEText('Python 邮件发送测试...', 'plain', 'utf-8')
    message['From'] = Header("菜鸟教程", 'utf-8')  # 发送者
    message['To'] = Header("测试", 'utf-8')  # 接收者

    subject = 'Python SMTP 邮件测试'
    message['Subject'] = Header(subject, 'utf-8')

    try:
        smtpObj = smtplib.SMTP()
        smtpObj.connect(mail_host, 25)  # 25 为 SMTP 端口号
        smtpObj.login(mail_user, mail_pass)

        smtpObj.sendmail(sender, receivers, message.as_string())
        print("邮件发送成功")
    except smtplib.SMTPException:
        print("Error: 无法发送邮件")

if __name__ == '__main__':

    # qq邮箱的密码是邮箱授权码
    # 一个16位字符串 bxfiljzifsaggdea
    # send_mail_qq('1119332482@qq.com', 'bxfiljzifsaggdea', 'index_pct', 'good', '1119332482@qq.com')

    sender_mail_name = 'fucheng.dou@mfcteda.com'  # 发送邮箱
    receivers_mail_name = ['fucheng.dou@mfcteda.com', 'doufucheng123@foxmail.com']  # 接收邮箱 list
    acc_mail_name = ['doufucheng123@foxmail.com', 'fuchengdou@126.com']  # 抄送邮箱 list
    subject_header = "Python 测试标题"  # 邮件标题
    body_text = 'Python 测试内容 具体见附件.\n\n窦福成\n金融工程部\n'
    file_path = 'C:\\Users\\doufucheng\\OneDrive\\Desktop\\'
    file_name = 'Desktop.rar'
    send_mail_mfcteda(sender_mail_name, receivers_mail_name, acc_mail_name,
                      subject_header, body_text, file_path, file_name)

    # send_mail_126()