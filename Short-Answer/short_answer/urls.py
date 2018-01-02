from django.conf.urls import url
from django.views.generic import TemplateView
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^login/$', views.user_login, name='login'),
    url(r'^register/$', views.register, name='register'),
    url(r'^about/$', views.about, name='about'),
    url(r'^student_home/$', views.student_home, name='student_home'),
    url(r'^teacher_home/$', views.teacher_home, name='teacher_home'),
    url(r'^student_test/$', views.student_test, name='student_test'),
    url(r'^student_test/viewscore/$', views.viewscore, name='view_score'),
    url(r'^question_bank/$', views.question_bank, name='question_bank'),
    url(r'^logout/$', views.user_logout, name='logout'),
]
