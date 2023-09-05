import hashlib
import pickle
import re
from threading import Thread

import jieba
from django.core.paginator import Paginator
from django.db.models import Q, F
from django.shortcuts import render
from haystack.views import SearchView
from rest_framework import viewsets
from rest_framework.generics import get_object_or_404
from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework.views import APIView
from zhconv import convert

from apps.article.serializers import ArticleSerializer
from blog import settings
from blog.settings import PAGE_SIZE as page_size, VALID_DAYS, HOT_TAGS

# Create your views here.
from apps.article.constants import search_key_prefix, STOP_WORDS
from apps.article.models import Article, SearchKeyWord
from apps.core.redis_cache import redis_cache_default

class HomeView(APIView):
    def get(self, request, format=None):
        data = "hello"
        return Response(data)

def home(request):
    # todo 取消page_size参数

    page_num = request.GET.get('page_num', '1')
    if not page_num.isnumeric():
        page_num = 1
    page_num = int(page_num)
    search = request.GET.get('keywords', '').strip()
    tags = request.GET.get('tags', '')
    sort = request.GET.get('sort', '')
    article_list = Article.objects.filter(delete_time=None)
    if sort:
        if sort == "hot":
            article_list = get_hot_article(article_list)
        elif sort == "month_download_num":
            month_ago = timezone.now() - timedelta(days=30)
            article_list = article_list.filter(create_time__gte=month_ago).order_by("-download_num")
        else:
            article_list = article_list.order_by(f"-{sort}")
    if search:
        article_list = article_list.filter(
            Q(title__icontains=search) | Q(summary__icontains=search) | Q(body__icontains=search))
        if not request.user.is_staff or settings.ENV != "prod":
            thread = Thread(target=record_search, args=(search,))
            thread.start()
    if tags:
        article_list = article_list.filter(tags__name=tags)
    paginator = Paginator(article_list, page_size)
    page_num = min(page_num, paginator.count)
    # page_num = max(page_num, 1)
    page_obj = paginator.get_page(page_num)
    user = request.user
    time_threshold = timezone.now() - timedelta(days=VALID_DAYS)
    for article in page_obj:
        # todo 外键prefecth 优化
        order = ArticleOrder.objects.filter(article__id=article.id, buyer__id=user.id,
                                            create_time__gte=time_threshold, ).first()
        has_liked = ArticleLike.objects.filter(article_id=article.id, user_id=user.id, status=1).first()
        article.has_payed = True if order else False
        article.has_liked = True if has_liked else False
        article.all_tags = article.tags.all()
    # unread_notification = Notification.objects.filter(receiver__id=user.id, status=0)
    announcement = Announcement.objects.filter(delete_time=None).first()
    context = {
        "announcement": announcement,
        "page_obj": page_obj,
        # "show_pre": page_num > 2,
        # "show_post": paginator.num_pages > page_num + 1,
        "total": paginator.count,
        "search": search,
        "tags": tags,
        "sort": sort,
        "path": request.get_full_path(),
        "hot_tags": HOT_TAGS,
        # "noindex": True if (tags or sort) else False
        # "unread_mn": True if unread_notification else False,
    }

    if search:
        context['meta_title'] = f"{search}-搜索结果"
        return render(request, 'article/search.html', context)
    else:
        context['meta_title'] = tags
        context['sort_map'] = {"hot": "热度", "download_num": "总销量", "month_download_num": "月销量", "price": "价格"}
        return render(request, 'article/index.html', context)

def record_search(keywords):
    # todo paddle 模式

    jieba.load_userdict(settings.JIEBA_FILE_PATH)
    seg_list = jieba.cut(keywords)
    for seg in seg_list:
        seg = convert(seg, 'zh-cn').strip()
        if seg in STOP_WORDS:
            continue
        if len(seg) < 2:
            continue
        match_obj = re.match("\d{1,5}[pPvVmMgG]", seg)
        if match_obj:
            continue
        search_keyword_obj = SearchKeyWord.objects.filter(keyword=seg).first()
        if search_keyword_obj:
            search_keyword_obj.search_num = F('search_num') + 1
            search_keyword_obj.save()
        else:
            SearchKeyWord(keyword=seg).save()

class HaystackSearchView(SearchView):
    def build_form(self, form_kwargs=None):
        """
        Instantiates the form the class should use to process the search query.
        """
        data = None
        kwargs = {"load_all": self.load_all}
        if form_kwargs:
            kwargs.update(form_kwargs)

        if len(self.request.GET):
            data = self.request.GET
            data = data.copy()
            q = data.get("q")
            if q:
                q = convert(q, 'zh-cn').strip()
                data["q"] = q
        if self.searchqueryset is not None:
            kwargs["searchqueryset"] = self.searchqueryset

        return self.form_class(data, **kwargs)

    def create_response(self):
        """
        Generates the actual HttpResponse to send back to the user.
        """
        # todo 优化性能
        context = self.get_context()
        object_list = context.get('paginator').object_list
        query = context.get("query").strip()
        md5 = hashlib.md5()
        md5.update(query.encode("utf-8"))
        hash_query = md5.hexdigest()
        search_key = f"{search_key_prefix}_{hash_query}"
        if redis_cache_default.get(search_key):
            article_list = pickle.loads(redis_cache_default.get(search_key))
        else:
            raw_article_list = Article.objects.filter(delete_time=None).filter(
                Q(title__icontains=query) | Q(summary__icontains=query) | Q(body__icontains=query))
            haystack_article_ids = [object.object.id for object in object_list]
            raw_article_ids = [object.id for object in raw_article_list]
            total_article_ids = set(haystack_article_ids + raw_article_ids)
            article_list = Article.objects.filter(id__in=total_article_ids)
            redis_cache_default.set(search_key, pickle.dumps(article_list), ex=3600 * 24)
        page_num = int(self.request.GET.get('page_num', '1'))
        paginator = Paginator(article_list, page_size)
        page_num = min(page_num, paginator.count)
        page_obj = paginator.get_page(page_num)
        context["page_obj"] = page_obj
        context['meta_title'] = f"{query}-搜索结果"
        context['q'] = query
        if not self.request.user.is_staff or settings.ENV != "prod":
            thread = Thread(target=record_search, args=(context.get("query"),))
            thread.start()
        return render(self.request, self.template, context)


class ArticleViewSet(viewsets.ViewSet):
    """
    A simple ViewSet for listing or retrieving users.
    """
    def list(self, request):
        queryset = Article.objects.all()
        serializer = ArticleSerializer(queryset, many=True)
        data =  serializer.data
        return Response(data)

    def retrieve(self, request, pk=None):
        queryset = Article.objects.all()
        user = get_object_or_404(queryset, pk=pk)
        serializer = ArticleSerializer(user)
        return Response(serializer.data)

def slug_detail(request, article_id, slug):
    article = get_object_or_404(Article, pk=article_id, delete_time=None)
    if article.slug != slug:
        kwargs = {
            "article_id": article_id,
            "slug": article.slug,
        }
        redirect_url = reverse("article:slug_detail", kwargs=kwargs)
        return redirect(redirect_url, permanent=True)
    user = request.user
    # todo 优化浏览量统计，直接写库，
    if not user.is_staff:
        article.views += 1
    super(Article, article).save(update_fields=["views"])
    article.all_tags = article.tags.all()
    # paginator = Paginator(article_comments, page_size)
    # page_num = min(page_num, paginator.count)
    # page_obj = paginator.get_page(page_num)
    time_threshold = timezone.now() - timedelta(days=VALID_DAYS)
    order = ArticleOrder.objects.filter(article__id=article.id, buyer__id=user.id,
                                        create_time__gte=time_threshold).first()
    has_liked = ArticleLike.objects.filter(article_id=article.id, user_id=user.id, status=1).first()
    article.has_payed = True if order else False
    article.has_liked = True if has_liked else False
    # todo 缓存上一篇下一篇
    next_article = get_next_article(article)
    pre_article = get_pre_article(article)
    meta_description = f"{article.title};{article.summary}"
    meta_description = re.sub("\s", "", meta_description)
    context = {
        "article": article,
        "next_article": next_article,
        "pre_article": pre_article,
        "article_recommend": get_article_recommend(article),
        "article_history_hot": get_article_history_hot(),
        "article_month_hot": get_article_month_hot(),
        "meta_title": f"{article.title}-自由分享小站",
        "meta_keywords": get_seo_keywords(article),
        "meta_description": meta_description
    }
    return render(request, 'article/detail.html', context)