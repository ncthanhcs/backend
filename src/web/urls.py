from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('<int:movie_id>/',views.detail ,name='detail'),
    path('signup/',views.signUp,name='signup'),
    path('login/',views.Login,name='login'),
    path('recommend/',views.recommend,name='recommend'),
    path('logout/',views.Logout,name='logout'),
    path('msignup/',views.msignUp,name='msignup'),
    path('mlogin/',views.mLogin,name='mlogin'),
    path('mlogout/',views.mLogout,name='mlogout'),
    path('getlistfilm/',views.getListFilm,name='getlistfilm'),
    path('searchmovie/',views.searchMovie,name='searchmovie'),
    path('uploadrating/',views.uploadRating,name='uploadrating'),

]