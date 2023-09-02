import os
import re

import jieba
from PIL import Image
from django.conf import settings
from django.db import models
from lxml import etree
from slugify import slugify

from apps.core.models import Base
from apps.tag.models import Tag
from gen_utils.url_util import url_to_hyperlink

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class Article(Base):
    """帖子"""
    # todo propertycache
    # no_watermark_tag = Tags.objects.filter(name="无水印").first()
    # free_tag = Tags.objects.filter(name="免费").first()
    # is_collection_tag = Tags.objects.filter(name="合集").first()
    # has_face_tag = Tags.objects.filter(name="露脸").first()
    # freeshare_tag = Tags.objects.filter(name="freeshare首发").first()

    CATEGORY = (
        ('all', '全部'),
    )
    PRICE_CHOICE = (
        (0, 0),
        (1, 1),
        (2, 2),
        (3, 3),
        (4, 4),
        (5, 5),
        (6, 6),
        (7, 7),
        (8, 8),
        (9, 9),
        (10, 10),
        (15, 15),
        (20, 20),
        (25, 25),
        (30, 30),
        (35, 35),
        (40, 40),
        (45, 45),
        (50, 50),
        (60, 60),
        (70, 70),
        (80, 80),
        (90, 90),
        (100, 100),
        (150, 150),
        (200, 200),
    )
    id = models.AutoField(primary_key=True)
    title = models.CharField(verbose_name='标题', max_length=200, unique=True)
    slug = models.CharField(verbose_name='slug标题', default='', max_length=60)
    summary = models.TextField(verbose_name='摘要', default="")
    # todo 优化封面设计
    cover_urls = models.CharField(verbose_name='封面图urls', max_length=1000)
    # summary_pic_url = models.CharField(verbose_name='推荐图url', max_length=200, null=True)
    # todo ckeditor required=True
    # todo ckeditor 修复ckeditor显示bug
    body = models.TextField(verbose_name='正文')
    download_link = models.CharField(verbose_name='下载链接', max_length=500)
    dl_is_valid = models.BooleanField(verbose_name='链接是否有效', default=True)
    extract_code = models.CharField(verbose_name='提取码', max_length=500)
    baidu_share_content = models.TextField(verbose_name='百度分享')
    upack_code = models.CharField(verbose_name='解压码', max_length=500, blank=True, null=True, default='laowang')
    views = models.PositiveIntegerField(verbose_name='浏览量', default=0)
    download_num = models.PositiveIntegerField(verbose_name='下载次数', default=0)
    # todo 帖子原价
    # is_free = models.BooleanField(verbose_name='是否免费', default=False)
    price = models.IntegerField(verbose_name='价格', default=1, choices=PRICE_CHOICE)
    author_id = models.IntegerField(verbose_name='作者', default=1)
    category = models.CharField(verbose_name='分类', max_length=100, choices=CATEGORY, default='all')
    no_watermark = models.BooleanField(verbose_name="无水印", default=False)
    has_face = models.BooleanField(verbose_name="露脸", default=False)
    is_collection = models.BooleanField(verbose_name="合集", default=False)
    is_freeshare = models.BooleanField(verbose_name="freeshare首发", default=False)
    tags = models.ManyToManyField(Tag, blank=False)

    # todo 帖子标签。
    # tags =

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-update_time']
        verbose_name = "帖子"
        verbose_name_plural = verbose_name

    def get_absolute_url(self):
        from django.urls import reverse
        # return reverse('article:detail', kwargs={'article_id': self.id})
        return reverse('article:slug_detail', kwargs={'article_id': self.id, 'slug': self.slug})

    def save(self, *args, **kwargs):
        """
        链接：https://pan.baidu.com/s/1y_jw2JgKqF7UAUmJiuMVqQ
        提取码：28gp
        复制这段内容后打开百度网盘手机App，操作更方便哦--来自百度网盘超级会员V6的分享

        链接: https://pan.baidu.com/s/1p8Woi9TRmqhopqUtCGj_Mw  密码: vwjj
        --来自百度网盘超级会员V6的分享
        """
        # TODO 优化浏览量增加时的save逻辑
        if self.baidu_share_content:
            badu_share_content = self.baidu_share_content
            download_link = re.search('https?://[-A-Za-z0-9+&@#/%?=~_|!:,.;]+', badu_share_content).group()
            extract_code = re.search('码.*?([a-zA-Z0-9]{4})', badu_share_content).group(1)
            self.download_link = download_link
            self.extract_code = extract_code
        selector = etree.HTML(self.body)
        cover_urls = selector.xpath('//img/@src')[:4]
        cover_urls_str = ''
        # todo 优化图片上传
        for cover_url in cover_urls:
            try:
                img_path = os.path.join(settings.MEDIA_ROOT, cover_url.split('/')[-1])
                im = Image.open(img_path)
            except:
                continue
            width, height = im.width, im.height
            img_str = f'<img data-src="{cover_url}" style="height: {height}px; width: {width}px;">'
            cover_urls_str += img_str
        self.cover_urls = "<p>" + cover_urls_str + "</p>"
        # main_title = self.title.rsplit('【', maxsplit=1)[0]
        # self.slug = re.sub('\W+', '-', main_title).strip('-')
        self.set_slug()
        # self.summary = url_to_hyperlink(self.summary)
        super().save(*args, **kwargs)

    def viewed(self):
        # todo 浏览量性能
        self.views += 1
        self.save(update_fields=['views'])

    @property
    def comment_count(self):
        return len(self.comment_set.filter(delete_time=None))

    @property
    def like_count(self):
        from apps.personal_center.models import ArticleLike
        return ArticleLike.objects.filter(article=self.id, delete_time=None, status=1).count()

    def set_slug(self, slug=""):
        slug = slug or self.slug
        if not slug:
            return
        if not re.match(r'^[-A-Za-z\d]+\Z', slug):
            jieba.load_userdict(settings.JIEBA_FILE_PATH)
            seg_list = [word for word in jieba.cut(slug)]
            jieba_slug = '-'.join(seg_list)
            slug_max_len = self.__class__._meta.get_field("slug").max_length
            slug = slugify(jieba_slug, max_length=slug_max_len, word_boundary=True, save_order=True)

        # slug_items = slug.split("-")
        # slug_list = []
        # for item in slug_items:
        #     slug_list.append(item)
        #     temp_slug = "-".join(slug_list)
        #     if len(temp_slug)>slug_max_len:
        #         slug_list.pop(-1)
        #         break
        # final_slug =  "-".join(slug_list)
        self.slug = slug


class Announcement(Base):
    title = models.CharField(verbose_name='标题', max_length=200)
    body = models.TextField(verbose_name='正文')
    views = models.PositiveIntegerField(verbose_name='浏览量', default=0)

    class Meta:
        ordering = ['-create_time']
        verbose_name = "公告"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.body = url_to_hyperlink(self.body)
        super(Announcement, self).save(*args, **kwargs)


class SearchKeyWord(Base):
    keyword = models.CharField(verbose_name="搜索关键词", max_length=64)
    search_num = models.IntegerField(verbose_name="搜索次数", default=1)
    update_time = models.DateTimeField('修改时间', auto_now=True)

    class Meta:
        ordering = ['-search_num']
        verbose_name = "搜索记录"
        verbose_name_plural = verbose_name


class Segment(Base):
    word = models.CharField(verbose_name="分词", max_length=64, unique=True)
    frequency = models.CharField(verbose_name="词频", max_length=32, blank=True, null=True, default="")
    property = models.CharField(verbose_name="词性", max_length=32, blank=True, null=True, default="")

    class Meta:
        ordering = ['-create_time']
        verbose_name = "结巴分词库"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.word

    def save(self, *args, **kwargs):
        self.word = self.word.lower()
        super(Segment, self).save(*args, **kwargs)
        from gen_utils.segment_util import refreash_jieba_dict
        refreash_jieba_dict()

    def delete(self, *args, **kwargs):
        super(Segment, self).delete(*args, **kwargs)
        jieba.del_word(self.word)
        from gen_utils.segment_util import refreash_jieba_dict
        refreash_jieba_dict()
