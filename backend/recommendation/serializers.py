# recommendation/serializers.py
from rest_framework import serializers

class RecommendationRequestSerializer(serializers.Serializer):
    """用於處理推薦請求的序列化器"""
    query = serializers.CharField(required=True, max_length=500)
    top_k = serializers.IntegerField(required=False, default=10, min_value=1, max_value=100)
    content_type = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    genres = serializers.ListField(
        required=False, 
        child=serializers.CharField(max_length=100),
        allow_empty=True
    )
    # 可以添加更多過濾條件

class ContentMetadataSerializer(serializers.Serializer):
    """內容元數據序列化器"""
    # 共同欄位
    release_date = serializers.DateField(required=False, allow_null=True)
    
    # 電影特有欄位
    director = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    cast = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    rating = serializers.FloatField(required=False, allow_null=True)
    
    # 動畫特有欄位
    episodes = serializers.IntegerField(required=False, allow_null=True)
    studio = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    voice_actors = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    
    # 遊戲特有欄位
    platform = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    developer = serializers.CharField(required=False, allow_blank=True, allow_null=True)

class RecommendationResultSerializer(serializers.Serializer):
    """推薦結果序列化器"""
    id = serializers.IntegerField()
    title = serializers.CharField()
    type = serializers.CharField()
    description = serializers.CharField(allow_blank=True, allow_null=True)
    genres = serializers.ListField(child=serializers.CharField(), allow_empty=True)
    similarity_score = serializers.FloatField()
    poster = serializers.CharField(allow_blank=True, allow_null=True)
    metadata = ContentMetadataSerializer()