from funcapp.models import Email, Client



# 这里将放置所有的数据库操作。
def has_email_been_registered(entry_id: str):
    """
    根据entry_id判断email是否已经被注册。
    :param entry_id: Email model中的entry_id。
    :return: bool
    """
    return Email.objects.filter(entry_id=entry_id).exists()


def register_an_email(email: Email):
    """
    如果邮件没有存在数据库，注册一封email并返回新的message_id。否则返回已有的message_id。
    :param email: Email model。
    :return: message_id
    """
    if has_email_been_registered(email.entry_id):
        return Email.objects.get(entry_id=email.entry_id).message_id
    else:
        email.save()
    return email.message_id


def get_all_emails():
    """
    获得所有的email。
    :return: Email
    """
    return Email.objects.all()


def get_target_email(message_id: int):
    """
    获得目标email。
    :param message_id:
    :return: Email
    """
    return Email.objects.get(message_id=message_id)


def update_target_email_status_and_judgement(message_id: int, status: str = None, audit_pass: str = None,
                                             audit_judgement: str = None):
    """
    更新目标email的状态和审核结果。如果找不到message_id则不做任何事。
    :param status:
    :param message_id:
    :param audit_pass:
    :param audit_judgement:
    :return: None
    """
    try:
        target_email = Email.objects.get(message_id=message_id)
        if status is not None:
            target_email.status = status
        if audit_pass is not None:
            target_email.audit_pass = audit_pass
        if audit_judgement is not None:
            target_email.audit_judgement = audit_judgement
        target_email.save()
    except Email.DoesNotExist:
        pass


def get_client_by_email_address(email_address: str):
    """
    获得目标email的client。
    :param email_address:
    :return: Client
    """
    return Client.objects.get(email_address=email_address)


def update_client_profile(client_id: int, profile: str):
    """
    如果根据client_id找到client则更新目标client的profile。否则什么都不做。
    :param client_id:
    :param profile:
    :return: None
    """
    try:
        target_client = Client.objects.get(id=client_id)
        target_client.profile = profile
        target_client.save()
    except Client.DoesNotExist:
        pass


