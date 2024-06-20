from django.urls import path

from . import views

app_name = "drawing"

urlpatterns = [
    path('delete-room/<int:pk>/', views.RoomDeleteView.as_view(), name="delete_room"),
    path('sign-in/', views.SignInView.as_view(), name="sign_in"),
    path('sign-up/', views.SignUpView.as_view(), name="sign_up"),
    path('log-out/', views.logout_view, name="logout"),
    path('room/<int:pk>/', views.room, name="room"),
    path('', views.index, name="index")
]