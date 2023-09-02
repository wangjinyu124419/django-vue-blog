import jieba
from django.contrib import admin
# Register your models here.
from django.urls import reverse
from django.utils.html import format_html
from django.utils.timezone import now

from apps.article.constants import search_key_prefix
from apps.article.forms import AticleForm
from apps.article.models import Article, Announcement, SearchKeyWord, Segment
# from apps.general_app.admin import ReadOnlyModelAdmin
# from apps.general_app.redis_cache import redis_cache_default
# from apps.vip.models import ArticleOrder
from apps.core.redis_cache import redis_cache_default
from gen_utils.segment_util import refreash_jieba_dict


class ArticleAdmin(admin.ModelAdmin):
    form = AticleForm
    search_fields = ['title']
    list_filter = ['price']
    # 不支持中文
    # prepopulated_fields = {"slug": ("title",)}

    list_display = (
        'id', 'detail_link', 'price', 'baidu_link', 'extract_code', 'views', 'download_num',
        'delete_time',
        'update_time',
        'create_time',
    )

    # todo  标签横向排列
    fieldsets = (
        (None, {
            'fields': (
                'title', 'slug', 'delete_time', 'summary', 'price', 'baidu_share_content', 'upack_code',
                'modify_update_time',
                'no_watermark',
                'has_face',
                'is_collection', 'is_freeshare', "tags", 'body')
        }),
    )

    ordering = ('-create_time',)

    def baidu_link(self, obj):
        return format_html(f'<a href="{obj.download_link}">百度网盘链接</a>')

    baidu_link.short_description = '下载链接'

    def detail_link(self, obj):
        return format_html(f'<a href="/article/detail/{obj.id}">{obj.title}</a>')

    detail_link.short_description = '帖子详情'

    # def article_order(self, obj):
    #     info = (ArticleOrder._meta.app_label, ArticleOrder._meta.model_name)
    #     vip_order_admin_url = reverse('admin:%s_%s_changelist' % info)
    #     todo计算总额
    #     card_ids = VipOrder.objects.filter(buyer_id=obj.id).values_list("card_id")
    #     card_ids= [card_id[0] for card_id in card_ids]
    #     total_price = VipCard.objects.filter(card_id__in=card_ids).annotate(Sum("card_type"))
    #     return format_html(f'<a href="{vip_order_admin_url}?q={obj.title}">帖子订单</a>')

    # article_order.short_description = '帖子订单'

    # todo 优化 save_related
    def save_related(self, request, form, formsets, change):
        super(ArticleAdmin, self).save_related(request, form, formsets, change)
        instance = form.instance
        if instance.price == 0:
            instance.tags.add(instance.free_tag)
        if instance.no_watermark:
            instance.tags.add(instance.no_watermark_tag)
        if instance.has_face:
            instance.tags.add(instance.has_face_tag)
        if instance.is_collection:
            instance.tags.add(instance.is_collection_tag)
        if instance.is_freeshare:
            instance.tags.add(instance.freeshare_tag)


    def save_model(self, request, obj, form, change):
        """
        Given a model instance save it to the database.
        """
        if form.cleaned_data.get("modify_update_time"):
            obj.update_time = now()
        obj.save()
        search_keys = redis_cache_default.keys(f"{search_key_prefix}*")
        for search_key in search_keys:
            redis_cache_default.delete(search_key)

    def delete_model(self, request, obj):
        """
        Given a model instance delete it from the database.
        """
        obj.delete_time = now()
        obj.save()

    def delete_queryset(self, request, queryset):
        # todo 完善帖子逻辑删除
        """Given a queryset, delete it from the database."""
        queryset.update(delete_time=now())

    class Media:
        # todo 调整js
        css = {"all": ("css/admin.css",)}
        js = (
            "admin/js/jquery-3.6.0.min.js",
            "ckeditor/ckeditor.js",
            "js/admin.js",
        )


# class AnnouncementAdmin(admin.ModelAdmin):
#     list_display = ('id', 'title', 'delete_time')
#     fieldsets = (
#         (None, {
#             'fields': ('title', 'delete_time', 'body')
#         }),
#     )
#
#     ordering = ('-create_time',)
#
#     class Media:
#         # todo 调整js
#         css = {"all": ("css/admin.css",)}
#         js = ("admin/js/jquery-3.6.0.min.js",
#               "ckeditor/ckeditor.js",
#               "js/admin.js",
#               )
#
#     def delete_model(self, request, obj):
#         """
#         Given a model instance delete it from the database.
#         """
#         obj.delete_time = now()
#         obj.save()
#
#     def delete_queryset(self, request, queryset):
#         # todo 完善帖子逻辑删除
#         """Given a queryset, delete it from the database."""
#         queryset.update(delete_time=now())
#
#
# class SearchKeyWordAdmin(ReadOnlyModelAdmin):
#     search_fields = ['keyword']
#     list_display = ('id', 'keyword', 'search_num', "update_time", "create_time")
#     ordering = ('-search_num', '-update_time')
#
#
# class SegmentAdmin(admin.ModelAdmin):
#     list_display = ('id', 'word', 'frequency', 'property')
#     fieldsets = (
#         (None, {
#             'fields': ('word', 'frequency', 'property')
#         }),
#     )
#     ordering = ('-create_time',)
#     search_fields = ['word']
#
#     def delete_queryset(self, request, queryset):
#         for segment in queryset:
#             jieba.del_word(segment.word)
#         """Given a queryset, delete it from the database."""
#         super(SegmentAdmin, self).delete_queryset(request, queryset)
#         refreash_jieba_dict()


admin.site.register(Article, ArticleAdmin)
# admin.site.register(Announcement, AnnouncementAdmin)
# admin.site.register(SearchKeyWord, SearchKeyWordAdmin)
# admin.site.register(Segment, SegmentAdmin)
