from django.db import models
from pypinyin import lazy_pinyin

from apps.core.models import Base


class Tag(Base):
    """"""
    id = models.AutoField(primary_key=True)
    name = models.CharField(verbose_name='名称', max_length=200, unique=True)
    pinyin_name = models.CharField(verbose_name='拼音名称', max_length=200, default="", blank=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['pinyin_name']
        verbose_name = "标签"
        verbose_name_plural = verbose_name

    def save(self, *args, **kwargs):
        self.pinyin_name = "".join(lazy_pinyin(self.name))
        super().save(*args, **kwargs)


