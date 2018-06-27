from rest_framework import serializers
from ..models import PostPage

class PostPageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostPage
        fields = ['id', 'title', 'slug']