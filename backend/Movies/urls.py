from django.urls import path
from Movies import views 

app_name='Movies'
# http://127.0.0.1:8000/Movies/
urlpatterns = [
    path('', views.index, name='index'),
    path('add_movie/', views.add_movie, name='add_movie'),# http://127.0.0.1:8000/Movies/add_movie
    path('edit/<int:id>', views.edit, name='edit'),# http://127.0.0.1:8000/Movies/edit
    path('delete/<int:id>', views.delete, name='delete'),# http://127.0.0.1:8000/Movies/delete
    
]
