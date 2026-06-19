from django.urls import path
from django.views.generic import RedirectView
from .. import views

urlpatterns = [
    path('', RedirectView.as_view(pattern_name='login', permanent=False)),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('signup/step1/', views.signup_step1, name='signup_step1'),
    path('signup/step2/', views.signup_step2, name='signup_step2'),
    path('logout', views.cerrar_sesion, name='logout'),
]
