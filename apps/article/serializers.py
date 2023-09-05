from rest_framework import serializers

from apps.article.models import Article


class ArticleSerializer(serializers.ModelSerializer):
    tags = serializers.StringRelatedField(many=True, read_only=True)
    class Meta:
        model = Article
        fields = '__all__'