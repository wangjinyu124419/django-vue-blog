import logging
import os
from smtplib import SMTPRecipientsRefused

from django.core.mail import send_mail

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sexblog.settings")
import django

django.setup()


def send_auth_mail(code, to_email):
    try:
        send_mail(
            '重要操作验证码',
            '您的验证码五分钟有效:{}'.format(code),
            'wangjinyu124419@163.com',
            [to_email],
            fail_silently=False,
        )
        return True, None
    except SMTPRecipientsRefused:
        return False, '邮件地址不存在,请重新输入'
    except Exception as e:
        logging.exception(e)
        return False, '发送失败,请重试或联系管理员'


if __name__ == '__main__':
    send_auth_mail(1234, '1244192592@qq.com')
