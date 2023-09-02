from blog.settings import JIEBA_FILE_PATH


def refreash_jieba_dict():
    with open(JIEBA_FILE_PATH, 'w', encoding='utf8') as f:
        from apps.article.models import Segment
        segment_queryset = Segment.objects.filter(delete_time=None)
        for segment in segment_queryset:
            one_line = segment.word
            if segment.frequency:
                one_line = one_line + " " + segment.frequency
            if segment.property:
                one_line = one_line + " " + segment.property
            f.write(one_line + "\n")


# refreash_jieba_dict()
