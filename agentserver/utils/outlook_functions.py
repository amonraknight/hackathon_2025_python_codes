import win32com.client
import os
import pythoncom



def read_outlook_mail(output_path: str):
    '''
    读取所有的outlook邮件，获取正文、发件人、主题，下载附件。
    :param output_path:
    :return:
    '''
    pythoncom.CoInitialize()
    outlook = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")
    inbox = outlook.GetDefaultFolder(6)  # 6代表收件箱
    messages = inbox.Items
    messages.Sort("[ReceivedTime]", True)  # 按收件时间排序
    emails = []

    for message in messages:
        each_email = {"Entry_ID": message.EntryID, "Subject": message.Subject, "Sender": message.Sender.Address,
                      "Body": message.Body}
        attachments = message.Attachments
        if len(attachments) > 0 and not os.path.exists(os.path.join(output_path, message.EntryID)):
            os.makedirs(os.path.join(output_path, message.EntryID))

        for attachment in attachments:
            attachment.SaveAsFile(os.path.join(output_path, message.EntryID, attachment.FileName))
        emails.append(each_email)

    return emails


def send_an_email(recipients: list, subject: str, body: str):
    pythoncom.CoInitialize()
    outlook = win32com.client.Dispatch("Outlook.Application")
    mail = outlook.CreateItem(0)
    mail.Subject = subject
    mail.BodyFormat = 2  # 2代表HTML格式
    mail.HTMLBody = body
    for recipient in recipients:
        mail.Recipients.Add(recipient)
    mail.Send()


