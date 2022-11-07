from unicodedata import name
from django.urls import path
from . import views

app_name = 'vuniversity'
urlpatterns = [
    #path('<name>', views.getHtml),
    path('login/',views.login_view, name="Login"),
    path('lecturer/', views.lec_get_started, name='Get_started'),
    path('lecturer/all_lecture/', views.see_all_lecture, name ="all_lecture"),
    path('logout/', views.logout_view, name="logout"),
    path('student/',views.std_get_started ,name='std_Get_started'),
    path('student/all_lecture',views.std_all_lecture ,name='see_all_lecture'),
    path('lecturer/next_lecture',views.live_lecture , name= 'live_lecture'),
    path('student/show_live',views.std_live,name='std_live'),

    path('jan/api/ask/', views.ask_api, name='ask_api'),
    path('jan/api/time/', views.time_api, name='time_api'),

    path('lecturer/next_lecture/summary/', views.summary , name='show_summary'),
    path('jan/api/alter/', views.alter_api, name='alter')

]