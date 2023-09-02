from django.contrib.admin.widgets import FilteredSelectMultiple
from django.forms import models, BooleanField

from apps.article.models import Article
from apps.tag.models import Tag


class AticleForm(models.ModelForm):
    tags = models.ModelMultipleChoiceField(queryset=Tag.objects.all(), label='标签', required=False,
                                           widget=FilteredSelectMultiple(verbose_name='标签', is_stacked=False))
    modify_update_time = BooleanField(label="更新修改时间", required=False)
    class Meta:
        model = Article
        fields = ['title', 'slug', 'body', 'extract_code']
