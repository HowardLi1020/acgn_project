from django.urls import path
from Animations import views 

app_name='Animations'
# http://127.0.0.1:8000/animation/
urlpatterns = [
    path('', views.index, name='index'),
    path('add_animations/', views.add_animations, name='add_animations'),# http://127.0.0.1:8000/animations/add_animations
    path('edit/<int:id>', views.edit, name='edit'),# http://127.0.0.1:8000/animations/edit
    path('delete/<int:id>', views.delete, name='delete'),# http://127.0.0.1:8000/animations/delete
    
]
