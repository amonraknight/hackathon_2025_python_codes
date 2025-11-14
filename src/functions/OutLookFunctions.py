import win32com.client
import os
import random

def read_outlook_mail(output_path: str):
    '''
    读取所有的outlook邮件，获取正文、发件人、主题，下载附件。
    :param output_path:
    :return:
    '''
    outlook = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")
    inbox = outlook.GetDefaultFolder(6)  # 6代表收件箱
    messages = inbox.Items
    messages.Sort("[ReceivedTime]", True)  # 按收件时间排序
    emails = []

    for message in messages:
        # 生成一个随机的10位数字编号。
        random_key = random.randint(1000000000, 9999999999)
        each_email = {"Sender": message.Sender.Address, "Subject": message.Subject, "Body": message.Body, "Random_Key": str(random_key)}
        attachments = message.Attachments
        if len(attachments) > 0 and not os.path.exists(os.path.join(output_path, str(random_key))):
            os.makedirs(os.path.join(output_path, str(random_key)))

        for attachment in attachments:
            attachment.SaveAsFile(os.path.join(output_path, str(random_key), attachment.FileName))
        emails.append(each_email)

    return emails
