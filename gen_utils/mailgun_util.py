import logging

import requests

from config import MAILGUN_API_KEY


class MailGun:
    timeout = 60
    api_key = MAILGUN_API_KEY
    auth = ("api", api_key)
    email_api = "https://api.mailgun.net/v3/freeshare.blog/messages"
    sender_address = "freeshare<noreply@freeshare.com>"
    code_template = """
            <h1>请使用下面的验证码验证您的操作，验证码 10 分钟内有效:</h1>
            <span style="padding: 10px 20px; font-size: 24px;background-color: #EB6F5A;border-radius:4px;color:#fff;">{}</span>
    """

    @classmethod
    def send_message(
            cls,
            receiver_address,
            subject,
            content,
            email_type="html",
            files=None,
    ):
        """
        @param sender_name: 发件人昵称
        @param sender_address: 发件地址
        @param receiver_address: 收件地址
        @param subject: 主题
        @param content: 正文
        @param email_type: 邮件类型,html或者text
        @param cc: 抄送
        @param bcc: 暗抄送
        @param files: 附件列表
        @return:
        """

        data = {
            "from": cls.sender_address,
            "to": receiver_address,
            "subject": subject,
            email_type: content,
        }
        try:
            res = requests.post(
                cls.email_api,
                auth=cls.auth,
                data=data,
                files=files,
                timeout=cls.timeout,
            )
            print(res.text, res.status_code)
            if res.status_code != 200:
                return False, res.text
            return True, None

        except Exception as e:
            logging.exception(e)
            return False, e


mailgun = MailGun()

if __name__ == '__main__':
    # maingun = MailGun()
    res = MailGun.send_message(
        receiver_address=['wangjinyu124419@163.com', '1244192592@qq.com'],
        subject='【freeshare】 请查收您的验证码',
        # content='【freeshare】 您的验证码是:3423,10分钟有效',
        content=MailGun.code_template.format('1234')

    )
    print(res)
