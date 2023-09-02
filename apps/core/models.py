from django.db import models
from django.utils.timezone import now


class Base(models.Model):
    create_time = models.DateTimeField('创建时间', default=now)
    update_time = models.DateTimeField('修改时间', default=now)
    delete_time = models.DateTimeField('删除时间', blank=True, null=True)

    class Meta:
        # 抽象模型
        abstract = True


class SiteSettings(Base):
    card_site1 = models.CharField(verbose_name="卡密网站1", max_length=512, null=True, blank=True)
    card_site2 = models.CharField(verbose_name="卡密网站2", max_length=512, null=True, blank=True)
    card_site3 = models.CharField(verbose_name="卡密网站3", max_length=512, null=True, blank=True)

    class Meta:
        ordering = ['-update_time']
        verbose_name = "配置"
        verbose_name_plural = verbose_name
