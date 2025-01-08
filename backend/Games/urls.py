from django.urls import path
from Games import views 

app_name='Games'
# http://127.0.0.1:8000/Games/
urlpatterns = [
    path('', views.index, name='index'),
    path('add_games/', views.add_games, name='add_games'),# http://127.0.0.1:8000/games/add_games
    path('edit/<int:id>', views.edit, name='edit'),# http://127.0.0.1:8000/games/edit
    path('delete/<int:id>', views.delete, name='delete'),# http://127.0.0.1:8000/games/delete
    
]