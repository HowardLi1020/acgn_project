from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Post, Reply, Like
from .serializers import PostSerializer, ReplySerializer, LikeSerializer

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all().order_by('-created_at')
    serializer_class = PostSerializer

    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        """處理按讚請求"""
        post = self.get_object()
        user_id = request.data.get("user_id")

        if not user_id:
            return Response({"error": "user_id 是必填欄位"}, status=status.HTTP_400_BAD_REQUEST)

        if Like.objects.filter(post=post, user_id=user_id).exists():
            return Response({"message": "你已經點過讚了"}, status=status.HTTP_400_BAD_REQUEST)

        Like.objects.create(post=post, user_id=user_id)
        return Response({"message": "成功點讚"}, status=status.HTTP_201_CREATED)

class ReplyViewSet(viewsets.ModelViewSet):
    queryset = Reply.objects.all().order_by('-created_at')  # 讓最新回覆排在最前
    serializer_class = ReplySerializer

class LikeViewSet(viewsets.ModelViewSet):
    """只允許新增按讚，不允許查看所有按讚紀錄"""
    queryset = Like.objects.all()
    serializer_class = LikeSerializer

    def list(self, request, *args, **kwargs):
        return Response({"error": "不允許直接查看按讚紀錄"}, status=status.HTTP_403_FORBIDDEN)
