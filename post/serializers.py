from rest_framework import serializers

from post.models import Post


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ["id",
                  "content",
                  "image",
                  "created_at",
                  "user"]
