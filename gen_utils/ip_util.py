import logging

import requests

logger = logging.getLogger(__name__)


class IpUtil:
    ip_locatio_api = "http://ip-api.com/json/{}?lang=zh-CN"
    timeout = 60

    @classmethod
    def get_client_ip(cls, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    @classmethod
    def get_ip_location(cls, ip):
        try:
            data = requests.get(cls.ip_locatio_api.format(ip), timeout=cls.timeout).json()
            country = data.get("country", "")
            status = data.get("status")
            if status == "fail":
                logger.error(f"获取ip信息失败:{ip}")
                return ''
            if country == '中国':
                geo = data.get("country", "") + data.get("regionName", "")
            else:
                geo = country
            return geo
        except Exception:
            logger.exception(f"获取ip信息异常:{ip}")
