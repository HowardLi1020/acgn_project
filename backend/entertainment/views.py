from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from .models import Game, Animation, Movie
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import GameSerializer, AnimationSerializer, MovieSerializer

# ✅ 取得所有遊戲
@api_view(["GET"])
def get_games(request):
    games = Game.objects.all()
    serializer = GameSerializer(games, many=True)
    return Response(serializer.data)

# ✅ 取得所有動畫
@api_view(["GET"])
def get_animations(request):
    animations = Animation.objects.all()
    serializer = AnimationSerializer(animations, many=True)
    return Response(serializer.data)

# ✅ 取得所有電影
@api_view(["GET"])
def get_movies(request):
    movies = Movie.objects.all()
    serializer = MovieSerializer(movies, many=True)
    return Response(serializer.data)

# ✅ 取得單個遊戲
@api_view(["GET"])
def get_game_detail(request, game_id):
    game = get_object_or_404(Game, game_id=game_id)  # ✅ 修正
    serializer = GameSerializer(game)
    return Response(serializer.data)

# ✅ 取得單個動畫
@api_view(["GET"])
def get_animation_detail(request, animation_id):
    animation = get_object_or_404(Animation, animation_id=animation_id)  # ✅ 修正
    serializer = AnimationSerializer(animation)
    return Response(serializer.data)

# ✅ 取得單個電影
@api_view(["GET"])
def get_movie_detail(request, movie_id):
    movie = get_object_or_404(Movie, movie_id=movie_id)  # ✅ 修正
    serializer = MovieSerializer(movie)
    return Response(serializer.data)
