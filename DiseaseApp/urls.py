from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('Aboutus', views.Aboutus, name='Aboutus'),
    path('AdminLogin', views.AdminLogin, name='AdminLogin'),
    path('UserLogin', views.UserLogin, name='UserLogin'),
    path('Signup', views.Signup, name='Signup'),
    # This was the one causing the error:
    path('predict/', views.PredictDisease, name='predict'), 
    path('PredictAction', views.PredictAction, name='PredictAction'),
    path('TrainML', views.TrainML, name='TrainML'),
    path('SignupAction', views.SignupAction, name='SignupAction'),
    path('UserLoginAction', views.UserLoginAction, name='UserLoginAction'),
    path('AdminLoginAction', views.AdminLoginAction, name='AdminLoginAction'),
]