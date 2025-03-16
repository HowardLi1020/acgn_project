from django.urls import path
from .views import get_games, get_animations, get_movies, get_game_detail, get_animation_detail, get_movie_detail  # ✅ 修正

urlpatterns = [
    path("games/", get_games),
    path("animations/", get_animations),
    path("movies/", get_movies),

    # ✅ 單筆查詢 API
    path("games/<int:game_id>/", get_game_detail, name="get_game_detail"),
    path("animations/<int:animation_id>/", get_animation_detail, name="get_animation_detail"),
    path("movies/<int:movie_id>/", get_movie_detail, name="get_movie_detail"),
]
